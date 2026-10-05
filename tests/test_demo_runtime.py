"""Shared demonstration interfaces and independently known plotted quantities."""
import copy
import base64
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from math_ai_agents.demos import demo_catalog, demo_states, run_demo

LAB = Path(__file__).resolve().parents[1]


class DemoRuntimeTests(unittest.TestCase):
    def test_catalog_covers_all_chapters_and_declared_states(self):
        demos = [demo for chapter in range(1, 28) for demo in demo_catalog(chapter)]
        self.assertEqual(len(demos), 108)
        self.assertEqual(len({demo['id'] for demo in demos}), 108)
        self.assertEqual(sum(len(list(demo_states(chapter, demo['id'])))
                             for chapter in range(1, 28) for demo in demo_catalog(chapter)), 1173)

    def test_catalog_and_supplied_controls_are_not_mutated(self):
        catalog = demo_catalog(1)
        catalog[0]['title'] = 'changed by caller'
        self.assertNotEqual(demo_catalog(1)[0]['title'], 'changed by caller')
        controls = {'dataset': 'gradual', 'cutoff': .5}
        original = copy.deepcopy(controls)
        run_demo(1, 'C01-D01', controls, include_figure=False)
        self.assertEqual(controls, original)

    def test_threshold_values_and_unrounded_plot_coordinates(self):
        report = run_demo(1, 'C01-D01', {'dataset': 'gradual', 'cutoff': .5})
        metrics = dict(report['metrics'])
        self.assertEqual(metrics['Verdicts'], '00011')
        self.assertEqual(metrics['First passing scale'], '4')
        line = report['plot_data'][0]['lines'][0]
        self.assertEqual(line['x'], [1, 2, 3, 4, 5])
        self.assertEqual(line['y'], [.42, .46, .49, .52, .56])
        self.assertIn('<svg', report['figure_svg'])
        self.assertTrue(report['steps'])
        json.dumps(report, allow_nan=False)

    def test_invalid_controls_stop_before_computation(self):
        for controls in [[], {}, {'dataset': 'gradual'}, {'dataset': 'gradual', 'cutoff': .5, 'extra': 1},
                         {'dataset': 'gradual', 'cutoff': float('nan')},
                         {'dataset': 'gradual', 'cutoff': True}, {'dataset': 'missing', 'cutoff': .5}]:
            with self.subTest(controls=controls), self.assertRaises(ValueError):
                run_demo(1, 'C01-D01', controls)
        for chapter, demo in [(1, 'C03-D01'), (0, 'C01-D01'), (True, 'C01-D01')]:
            with self.assertRaises(ValueError):
                run_demo(chapter, demo)

    def test_default_and_explicit_default_are_identical(self):
        first = run_demo(1, 'C01-D01')
        second = run_demo(1, 'C01-D01', {'dataset': 'gradual', 'cutoff': .5})
        self.assertEqual(first, second)

    def test_reported_evidence_is_distinct_from_constructed_inputs(self):
        for chapter, did in [(14, 'C14-D01'), (19, 'C19-D01'), (19, 'C19-D03'), (26, 'C26-D03')]:
            with self.subTest(demo=did):
                report = run_demo(chapter, did, include_figure=False)
                self.assertIn('source-reported', report['evidence_kind'])
        self.assertEqual(run_demo(24, 'C24-D01', include_figure=False)['evidence_kind'],
                         'constructed teaching example')

    def test_confidence_interval_endpoints_survive_raw_export(self):
        report = run_demo(24, 'C24-D01', include_figure=False)
        segments = [segment for axis in report['plot_data'] for item in axis['collections']
                    for segment in item.get('segments', [])]
        self.assertTrue(segments)
        self.assertTrue(all(len(segment) == 2 for segment in segments))
        self.assertTrue(any(segment[0] != segment[1] for segment in segments))

    def test_svg_matches_default_web_state_exactly(self):
        entries = json.loads((LAB / 'chapter-map.json').read_text())
        for chapter in (1, 3):
            entry = next(item for item in entries if item['chapter'] == chapter)
            page = (LAB / entry['reader']).read_text()
            payload = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', page, re.S).group(1))
            demo = payload['demos'][0]
            key = ','.join(str(control['default']) for control in demo['controls'])
            image = base64.b64decode(demo['states'][key]['image'].split(',', 1)[1]).decode()
            self.assertEqual(run_demo(chapter, demo['id'])['figure_svg'], image)

    def test_cli_exports_same_calculation_and_figure(self):
        with tempfile.TemporaryDirectory(prefix='demo runtime with spaces ') as directory:
            out = Path(directory) / 'report.json'
            figure = Path(directory) / 'figure.svg'
            run = subprocess.run([sys.executable, '-m', 'math_ai_agents', 'demo', '--chapter', '1',
                                  '--id', 'C01-D01', '--output', str(out), '--figure', str(figure)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(dict(json.loads(out.read_text())['metrics'])['Verdicts'], '00011')
            self.assertIn('<svg', figure.read_text())


if __name__ == '__main__':
    unittest.main()
