"""Run the same authored demonstrations in notebooks, skills and web readers.

The chapter functions are the single computational source. Display metrics
retain their declared precision; plot_data separately retains the original
numeric artist coordinates before SVG serialization and rounding.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

from .core import bundle_root


@lru_cache(maxsize=1)
def _engine():
    directory = bundle_root() / 'tools/readers/engine'
    sys.path.insert(0, str(directory)) if str(directory) not in sys.path else None
    try:
        import matplotlib
        matplotlib.use('Agg')
        spec = importlib.util.spec_from_file_location('maa_demo_reader_engine', directory / 'build_readers.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    except ImportError as error:
        raise ValueError('Demonstrations need the tools declared in requirements-notebooks.txt.') from error


@lru_cache(maxsize=27)
def _chapter(chapter):
    if type(chapter) is not int or not 1 <= chapter <= 27:
        raise ValueError('Choose an integer chapter from 1 through 27.')
    _engine()
    path = bundle_root() / f'tools/readers/chapters/ch{chapter:02d}.py'
    spec = importlib.util.spec_from_file_location(f'maa_demo_chapter_{chapter:02d}', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def demo_catalog(chapter):
    """Authored metadata and control domains, returned as an independent copy."""
    return copy.deepcopy(_chapter(chapter).CHAPTER['demos'])


def _select(chapter, demo_id):
    if not isinstance(demo_id, str):
        raise ValueError('A demonstration ID is required, such as C03-D01.')
    module = _chapter(chapter)
    demo = next((item for item in module.CHAPTER['demos'] if item['id'] == demo_id), None)
    if demo is None:
        raise ValueError(f'Demonstration {demo_id!r} does not belong to Chapter {chapter}.')
    return module, demo


def demo_states(chapter, demo_id):
    """Yield every declared control combination in the web reader's order."""
    _, demo = _select(chapter, demo_id)
    for values in itertools.product(*(control['values'] for control in demo['controls'])):
        yield dict(zip((control['key'] for control in demo['controls']), values))


def _controls(demo, controls):
    if controls is None:
        return {item['key']: item['default'] for item in demo['controls']}
    if not isinstance(controls, dict):
        raise ValueError('Controls must be a complete JSON object.')
    expected = {item['key'] for item in demo['controls']}
    if set(controls) != expected:
        raise ValueError('Supply exactly these controls: ' + ', '.join(sorted(expected)))
    for item in demo['controls']:
        value = controls[item['key']]
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Control values must be finite.')
        matches = [v for v in item['values'] if value == v and
                   (type(value) is type(v) or type(value) in (int, float) and type(v) in (int, float))]
        if not matches:
            raise ValueError(f"{item['key']} must be one of {item['values']!r}.")
    return copy.deepcopy(controls)


def _plot_data(figure):
    import numpy as np
    from matplotlib.patches import Rectangle

    def array(value):
        value = np.ma.asarray(value)
        if np.ma.is_masked(value):
            raise ValueError('Plot data contains masked values; declare undefined values explicitly.')
        return np.asarray(value, dtype=float).tolist()

    axes = []
    for axis in figure.axes:
        axes.append({
            'title': axis.get_title(), 'x_label': axis.get_xlabel(), 'y_label': axis.get_ylabel(),
            'x_scale': axis.get_xscale(), 'y_scale': axis.get_yscale(),
            'x_limits': array(axis.get_xlim()), 'y_limits': array(axis.get_ylim()),
            'x_tick_labels': [tick.get_text() for tick in axis.get_xticklabels()],
            'y_tick_labels': [tick.get_text() for tick in axis.get_yticklabels()],
            'lines': [{'label': line.get_label(), 'x': array(line.get_xdata()),
                       'y': array(line.get_ydata())} for line in axis.lines],
            'collections': [dict(
                **({'offsets': array(item.get_offsets())} if hasattr(item, 'get_offsets') else {}),
                **({'segments': [array(segment) for segment in item.get_segments()]}
                   if hasattr(item, 'get_segments') else {}),
                **({'paths': [{'vertices': array(path.vertices),
                              'codes': path.codes.tolist() if path.codes is not None else None}
                             for path in item.get_paths()]}
                   if hasattr(item, 'get_paths') else {})) for item in axis.collections],
            'rectangles': [{'x': float(item.get_x()), 'y': float(item.get_y()),
                            'width': float(item.get_width()), 'height': float(item.get_height())}
                           for item in axis.patches if isinstance(item, Rectangle)],
            'images': [array(item.get_array()) for item in axis.images],
            'text': [item.get_text() for item in axis.texts],
        })
    json.dumps(axes, allow_nan=False)
    return axes


def run_demo(chapter, demo_id, controls=None, *, include_figure=True):
    """Compute a declared teaching state; supplied controls are never filled in.

    This runs the very function used to build the corresponding web state.
    Independent oracle tests establish numerical correctness separately.
    """
    engine = _engine()
    module, demo = _select(chapter, demo_id)
    selected = _controls(demo, controls)
    project = SimpleNamespace(style={}, budgets=engine.DEFAULT_BUDGETS)
    engine.apply_style(project)
    import matplotlib.pyplot as plt
    figure = None
    try:
        result = getattr(module, demo['function'])(**selected)
        figure, metrics, interpretation = result[:3]
        # The web builder draws before inspecting and serializing a figure.
        # Settle the same transforms before capturing raw coordinates or SVG IDs.
        figure.canvas.draw()
        extra = result[3] if len(result) == 4 else {}
        extra = {'alt': extra} if isinstance(extra, str) else extra
        report = {
            'chapter': chapter, 'demo_id': demo_id, 'title': demo['title'], 'controls': selected,
            'evidence_kind': demo.get('evidence_kind', 'constructed teaching example'),
            'metrics': [[str(label), engine.display_value(value)] for label, value in metrics.items()],
            'interpretation': interpretation.strip(), 'steps': extra.get('steps', []),
            'alt': engine.state_alt(demo, interpretation, extra.get('alt')),
            'plot_data': _plot_data(figure), 'assumptions': demo['assumptions'],
            'provenance': demo['provenance'], 'source_section': demo['source_section'],
            'receipt': {'executed': True, 'engine_version': engine.ENGINE_VERSION,
                        'method_sha256': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
                        'runtime_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        }
        if include_figure:
            report['figure_svg'] = engine.figure_svg(figure)
        json.dumps(report, allow_nan=False)
        return report
    finally:
        if figure is not None:
            plt.close(figure)


def demo_report_text(report):
    lines = [report['title'], 'Controls: ' + json.dumps(report['controls'], ensure_ascii=False),
             'Evidence: ' + report['evidence_kind'], '', 'Calculated quantities:']
    lines.extend(f'{label}: {value}' for label, value in report['metrics'])
    lines.extend(['', 'Worked steps:', *[f'{i + 1}. {step}' for i, step in enumerate(report['steps'])],
                  '', report['interpretation'], '', 'Assumptions: ' + report['assumptions'],
                  'Source section: ' + report['source_section'], 'Provenance: ' + report['provenance']])
    return '\n'.join(lines)
