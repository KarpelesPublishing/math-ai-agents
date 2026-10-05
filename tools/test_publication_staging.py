#!/usr/bin/env python3
"""Regression checks for public URL compatibility and synchronized packaging."""
import json
from pathlib import Path
import re
import tempfile
import unittest

from stage_publication import (REPO, build, clean_document, home_page,
                               publishing_frame, reader_payload, repository_readme,
                               reproducible_zip, shared_links, wrap_reader)
from verify_publication import Page, check_links, check_public_frames, check_repository_license


class PublicationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.site = self.base / 'web/companions/math-ai-agents'
        self.site.mkdir(parents=True)
        self.entry = {'chapter': 1, 'title': 'First chapter', 'outcome': 'First question',
                      'notebook': 'notebooks/01-first.ipynb', 'reader': 'readers/01-first/reader.html'}

    def test_archive_bytes_repeat_with_spaces(self):
        folder = self.base / 'folder with spaces'; folder.mkdir()
        (folder / 'input.json').write_text('{"p": 0.5}\n')
        first = reproducible_zip(folder, self.base / 'first.zip')
        second = reproducible_zip(folder, self.base / 'second.zip')
        self.assertEqual(first['sha256'], second['sha256'])

    def test_wrapper_preserves_state_payload(self):
        payload = {'chapter': 1, 'demos': [{'id': 'C01-D01', 'states': {'0': {'metrics': [['p', '0.5']]}}}]}
        text = ('<html lang="en" class="no-js"><head><style id="book-theme">.metric{color:var(--ink)}</style></head><body><header>'
                '<p class="lead">Question?</p><p>Same calculation.</p>'
                '<p class="notice">Identify source-reported values.</p>'
                '<nav class="chapter-nav"><a href="#C01-D01">One</a></nav></header>'
                '<main id="main"></main><footer>Old footer</footer>'
                '<script id="reader-data" type="application/json">' + json.dumps(payload) + '</script></body></html>')
        wrapped = wrap_reader(text, self.site / self.entry['reader'], self.site, self.entry, [])
        self.assertEqual(reader_payload(text), reader_payload(wrapped))
        self.assertIn('cmp-header', wrapped)
        self.assertIn('Notebook on GitHub', wrapped)
        self.assertIn('publishing-frame.css', wrapped)
        self.assertIn('Identify source-reported values.', wrapped)
        self.assertIn('.metric{color:var(--ink)}', wrapped)

    def test_home_counts_built_demonstrations(self):
        payloads = {1: {'demos': [{}, {}, {}]}}
        text = home_page([self.entry], payloads, self.site)
        self.assertIn('<li><b>1</b>chapters</li>', text)
        self.assertIn('<li><b>3</b>demonstrations</li>', text)
        self.assertIn('3 demonstrations', text)

    def test_website_prebuild_can_remove_generated_frame_and_its_stylesheet(self):
        markup = shared_links(self.site, self.site / 'index.html') + publishing_frame('index.html')
        blocks = re.findall(r'<!-- kml-publishing-frame:start -->([\s\S]*?)<!-- kml-publishing-frame:end -->', markup)
        self.assertEqual(len(blocks), 2)
        self.assertIn('publishing-frame.css', blocks[0])
        self.assertIn('class="kml-publishing-frame"', blocks[1])
        cleaned = re.sub(r'<!-- kml-publishing-frame:start -->[\s\S]*?<!-- kml-publishing-frame:end -->\n?', '', markup)
        self.assertNotIn('publishing-frame.css', cleaned)
        self.assertNotIn('class="kml-publishing-frame"', cleaned)
        self.assertIn('companion.css', cleaned)

    def test_repository_docs_keep_mit_license_and_existing_calculation_workflows(self):
        readme = repository_readme()
        self.assertIn('MIT License (see `LICENSE`)', readme)
        self.assertNotIn('All rights reserved', readme)
        self.assertIn('pip install -e .', readme)
        self.assertIn('run --chapter 6 --input my-inputs.json', readme)
        self.assertIn('skills/math-ai-agents', readme)
        self.assertIn('demo-list --chapter 6', readme)
        self.assertIn('python tools/install_skills.py --target ~/.claude/skills', readme)
        self.assertNotIn('cp -r skills/', readme)

    def test_license_preservation_rejects_missing_changed_or_conflicting_notice(self):
        root = self.base / 'canonical'; github = self.base / 'github'
        root.mkdir(); github.mkdir()
        (root / 'LICENSE').write_text('MIT License\nOriginal copyright notice\n')
        (github / 'README.md').write_text(repository_readme())
        self.assertEqual(check_repository_license(root, github)['status'], 'NEEDS-REGEN')
        (github / 'LICENSE').write_bytes((root / 'LICENSE').read_bytes())
        self.assertEqual(check_repository_license(root, github)['status'], 'VERIFIED')
        (github / 'LICENSE').write_text('MIT License\nChanged copyright notice\n')
        self.assertEqual(check_repository_license(root, github)['status'], 'NEEDS-REGEN')
        (github / 'LICENSE').write_bytes((root / 'LICENSE').read_bytes())
        (github / 'README.md').write_text('Copyright Jason Karpeles. All rights reserved.')
        self.assertEqual(check_repository_license(root, github)['status'], 'NEEDS-REGEN')

    def test_unmarked_or_duplicate_publisher_navigation_blocks_staging(self):
        page = self.site / 'index.html'
        frame = publishing_frame('index.html')
        page.write_text(shared_links(self.site, page) + frame)
        self.assertEqual(check_public_frames(self.site)['status'], 'VERIFIED')
        page.write_text(frame + frame)
        self.assertEqual(check_public_frames(self.site)['status'], 'NEEDS-REGEN')
        page.write_text('<nav class="kml-publishing-frame"></nav>')
        self.assertEqual(check_public_frames(self.site)['status'], 'NEEDS-REGEN')

    def test_document_links_use_existing_github_paths(self):
        page = self.site / 'guide/chapters/01-first.html'
        text = ('<html lang="en"><head><style>body{margin:0}</style></head><body>'
                '<a href="../../notebooks/01-first.ipynb">Notebook</a>'
                '<a href="../../skills/first/SKILL.md#method">Skill</a>'
                '<p>Value = 0.5.</p><pre><code>input = {"p": 0.5}</code></pre></body></html>')
        converted = clean_document(text, page, self.site, [self.entry])
        self.assertIn(REPO + '/blob/main/notebooks/01-first.ipynb', converted)
        self.assertIn(REPO + '/blob/main/skills/first/SKILL.md#method', converted)
        self.assertIn('Value = 0.5.', converted)
        self.assertIn('input = {"p": 0.5}', converted)
        self.assertIn('.cmp-doc{margin:0}', converted)

    def test_external_path_escape_rejected(self):
        page = self.site / 'guide/index.html'
        with self.assertRaisesRegex(ValueError, 'escapes staged site'):
            clean_document('<a href="../../../outside.md">Bad</a>', page, self.site, [])

    def test_worked_answer_prefers_rendered_page_and_preserves_anchor(self):
        answer = self.site / 'solutions/ch01.html'; answer.parent.mkdir()
        answer.write_text('<h2 id="demonstration-1">Worked reasoning</h2>')
        page = self.site / 'guide/chapters/01-first.html'
        converted = clean_document('<a href="../../solutions/ch01.md#demonstration-1">Answer and worked reasoning</a>',
                                   page, self.site, [])
        self.assertIn('href="../../solutions/ch01.html#demonstration-1"', converted)
        self.assertNotIn('/blob/main/solutions', converted)

    def test_skill_links_preserve_published_numeric_paths(self):
        page = self.site / 'guide/index.html'
        converted = clean_document('<a href="../skills/maa-01-score-threshold/SKILL.md">Skill</a>',
                                   page, self.site, [])
        self.assertIn('/blob/main/skills/01-score-threshold/SKILL.md', converted)
        self.assertNotIn('/blob/main/skills/maa-', converted)

    def test_versioned_checkout_preserved(self):
        root = self.base / 'project/Companion'; root.mkdir(parents=True)
        output = root.parent / 'output/publication/example'
        github = output / 'github/math-ai-agents'; (github / '.git').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'versioned checkout'):
            build(root, output, self.base / 'unused-styles', None)
        self.assertTrue((github / '.git').is_dir())

    def test_local_and_published_link_checks_are_distinct(self):
        github = self.base / 'github'; (github / 'notebooks').mkdir(parents=True)
        (github / 'notebooks/01-first.ipynb').write_text('{}')
        (self.site / 'index.html').write_text('<a href="chapter.html#term">Term</a>'
               f'<a href="{REPO}/blob/main/notebooks/01-first.ipynb">Notebook</a>')
        (self.site / 'chapter.html').write_text('<h1 id="term">Term</h1>')
        receipt = {'status': 'VERIFIED', 'commit': 'recorded', 'paths': []}
        checked = check_links(self.site, github, receipt)
        self.assertEqual(checked['github_paths_checked_in_staging'], 1)
        self.assertEqual(checked['live_github_path_verification']['missing_paths'], ['notebooks/01-first.ipynb'])
        self.assertTrue(checked['problems'])

    def test_visible_copy_excludes_code_without_changing_it(self):
        parsed = Page('<p>Constructed probability.</p><pre><code>launcher = 1</code></pre>'
                      '<script>install()</script><p>Expected value.</p>')
        self.assertEqual(''.join(parsed.text), 'Constructed probability.Expected value.')


if __name__ == '__main__':
    unittest.main(verbosity=2)
