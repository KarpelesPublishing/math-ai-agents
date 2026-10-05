#!/usr/bin/env python3
"""Audit notebook/web parity and retain an exact occurrence coverage register.

This checks synchronization, execution and preservation. Independent chapter
tests establish the mathematics separately; this script is not an oracle.
"""
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(cell):
    text = cell['source']
    return ''.join(text) if isinstance(text, list) else text


def stream(cell):
    return ''.join(''.join(out['text']) if isinstance(out['text'], list) else out['text']
                   for out in cell.get('outputs', []) if out['output_type'] == 'stream')


def svg(cell):
    images = [out['data']['image/svg+xml'] for out in cell.get('outputs', [])
              if 'image/svg+xml' in out.get('data', {})]
    if len(images) != 1:
        raise AssertionError(f'Expected one SVG output, found {len(images)}')
    return ''.join(images[0]) if isinstance(images[0], list) else images[0]


def canonical_svg(text):
    """Ignore XML attribute order only; retain coordinates, text, styles and IDs.

    IPython's SVG display moves the namespace declaration. This is not a
    change to the diagram. Runtime/web serialization is still compared as bytes.
    """
    return ET.canonicalize(text)


def assigned(cell, name):
    for node in ast.parse(source(cell)).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError('No literal assignment for ' + name)


def audit(root, report, register, backup=None, figures=None):
    root = root.resolve()
    sys.path.insert(0, str(root / 'src'))
    from math_ai_agents.demos import demo_catalog, demo_states, run_demo, demo_report_text
    from math_ai_agents.demos import _engine
    engine = _engine()
    entries = json.loads((root / 'chapter-map.json').read_text())
    assert [item['chapter'] for item in entries] == list(range(1, 28))
    records = []; states_checked = 0; demos_checked = 0; equations = 0
    preserved = []; errors = []; notebooks = []
    for path in sorted((root / 'notebooks').glob('*.ipynb')):
        nb = json.loads(path.read_text())
        cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code' and source(cell).strip()]
        assert nb['metadata'].get('lab_execution', {}).get('code_cells') == len(cells), path.name
        assert [cell['execution_count'] for cell in cells] == list(range(1, len(cells) + 1)), path.name
        assert not any(out['output_type'] == 'error' for cell in cells for out in cell.get('outputs', [])), path.name
        notebooks.append({'path': str(path.relative_to(root)), 'sha256': digest(path), 'code_cells': len(cells)})
    assert len(notebooks) == 29
    for entry in entries:
        chapter = entry['chapter']
        path = root / entry['notebook']; nb = json.loads(path.read_text())
        reader = root / entry['reader']; text = reader.read_text()
        web = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))
        definitions = demo_catalog(chapter)
        assert nb['metadata']['maa_demonstrations'] == [item['id'] for item in definitions]
        assert [item['id'] for item in entry['demonstrations']] == [item['id'] for item in definitions]
        canonical = root.parent / entry['source_path']
        if canonical.is_file():
            assert digest(canonical) == entry['source_sha256'], entry['source_path']
        notebook_sources = [source(cell) for cell in nb['cells']]
        for equation in entry['equations']:
            assert any(equation['tex'] in cell for cell in notebook_sources), equation['number']
            assert (root / equation['asset']).is_file(), equation['asset']
        equations += len(entry['equations'])
        if backup:
            oldpath = backup / 'Companion' / entry['notebook']
            old = json.loads(oldpath.read_text())
            oldsrc = [source(cell) for cell in old['cells']]
            cursor = 0; changed = []
            for original in oldsrc:
                if original in notebook_sources[cursor:]:
                    cursor = notebook_sources.index(original, cursor) + 1
                else:
                    changed.append(original)
            # Two reviewed prose corrections; all equations and code must persist.
            oldcode = [source(cell) for cell in old['cells'] if cell['cell_type'] == 'code']
            newcode = [source(cell) for cell in nb['cells'] if cell['cell_type'] == 'code']
            assert all(item in newcode for item in oldcode), f'Original code lost in {path.name}'
            assert not changed or chapter in (13, 23), f'Unreviewed source change in {path.name}'
            preserved.append({'chapter': chapter, 'original_cells': len(oldsrc), 'retained_exactly': len(oldsrc)-len(changed),
                              'reviewed_prose_corrections': len(changed), 'original_code_preserved': True})
        for authored, mapping, payload in zip(definitions, entry['demonstrations'], web['demos']):
            did = authored['id']; demos_checked += 1
            assert did == mapping['id'] == payload['id']
            cells = {cell['metadata']['maa_demo_role']: cell for cell in nb['cells']
                     if cell['metadata'].get('maa_demo_id') == did}
            assert set(cells) == {'teaching', 'worked-state', 'changed-state', 'all-states'}, did
            teaching = source(cells['teaching'])
            for field in ('question', 'symbols', 'explanation', 'application', 'assumptions', 'prediction', 'provenance', 'source_section'):
                assert authored[field] in teaching, (did, field)
            for option in authored.get('prediction_options', []):
                assert option in teaching, (did, option)
            defaults = {item['key']: item['default'] for item in authored['controls']}
            assert assigned(cells['worked-state'], 'demo_controls') == defaults
            changed = assigned(cells['changed-state'], 'changed_controls')
            assert sum(changed[key] != defaults[key] for key in defaults) == 1
            outputs = json.loads(stream(cells['all-states']))
            states = list(demo_states(chapter, did))
            assert len(states) == len(outputs) == len(payload['states']) == mapping['states']
            solution = (root / f'solutions/ch{chapter:02d}.md').read_text()
            assert authored['check'] in solution and authored['answer'] in solution
            for index, (controls, saved) in enumerate(zip(states, outputs)):
                result = run_demo(chapter, did, controls)
                assert payload.get('evidence_kind', 'constructed teaching example') == result['evidence_kind'], did
                indices = [control['values'].index(controls[control['key']]) for control in authored['controls']]
                key = ','.join(map(str, indices)); displayed = payload['states'][key]
                assert saved == {'controls': controls, 'metrics': result['metrics']}, (did, key, 'notebook table')
                for field in ('metrics', 'steps', 'interpretation', 'alt'):
                    assert result[field] == displayed[field], (did, key, field)
                image = base64.b64decode(displayed['image'].split(',', 1)[1]).decode()
                assert image == result['figure_svg'], (did, key, 'web SVG')
                assert 2 <= len(result['steps']) <= 8, (did, key, 'worked steps')
                for controls2, role in ((defaults, 'worked-state'), (changed, 'changed-state')):
                    if controls == controls2:
                        assert stream(cells[role]).strip() == demo_report_text(result).strip(), (did, role, 'report')
                        saved_svg = svg(cells[role])
                        assert canonical_svg(saved_svg) == canonical_svg(image), (did, role, 'SVG')
                if figures and controls == defaults:
                    figures.mkdir(parents=True, exist_ok=True)
                    (figures / (did + '.svg')).write_text(result['figure_svg'])
                records.append({'chapter': chapter, 'demo_id': did, 'state_key': key, 'controls': controls,
                                'source_section': authored['source_section'], 'source_path': entry['source_path'],
                                'source_sha256': entry['source_sha256'], 'equations': authored['equations'],
                                'notebook': entry['notebook'], 'cell_ids': {k: v['id'] for k,v in cells.items()},
                                'reader': entry['reader'], 'skill': entry['skill_path'],
                                'evidence_kind': result['evidence_kind'],
                                'method_sha256': result['receipt']['method_sha256'],
                                'metrics_sha256': hashlib.sha256(json.dumps(result['metrics']).encode()).hexdigest(),
                                'raw_plot_sha256': hashlib.sha256(json.dumps(result['plot_data'], sort_keys=True).encode()).hexdigest(),
                                'svg_sha256': hashlib.sha256(image.encode()).hexdigest(), 'parity': 'VERIFIED'})
                states_checked += 1
        print(f'Chapter {chapter:02d}: four demonstrations and all states match', flush=True)
    assert demos_checked == 108 and states_checked == 1173 and equations == 111
    register.parent.mkdir(parents=True, exist_ok=True)
    register.write_text(json.dumps({'scope': 'Exact notebook/web coverage and parity, not an independent numerical oracle.',
                                    'records': records}, indent=2, ensure_ascii=False)+'\n')
    summary = {'status': 'VERIFIED', 'demonstrations': demos_checked, 'states': states_checked,
               'canonical_display_equations_preserved': equations, 'notebooks': notebooks,
               'executed_code_cells': sum(item['code_cells'] for item in notebooks),
               'original_cell_preservation': preserved, 'register': str(register), 'register_sha256': digest(register),
               'engine_version': engine.ENGINE_VERSION, 'runtime_sha256': digest(root/'src/math_ai_agents/demos.py'),
               'svg_comparison': 'Runtime/web SVG byte identity; notebook SVG XML canonical identity (IPython reorders namespace attributes). No numeric rounding or figure-ID substitution.',
               'independent_math_checks': 'Separate chapter and raw-coordinate oracle suites; see release QA report.',
               'real_browser_acceptance': 'UNVERIFIED', 'errors': errors}
    report.parent.mkdir(parents=True, exist_ok=True); report.write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('notebooks','original_cell_preservation')},indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--register', type=Path, required=True)
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--figures', type=Path)
    args = parser.parse_args()
    audit(args.root, args.report, args.register, args.backup, args.figures)


if __name__ == '__main__':
    main()
