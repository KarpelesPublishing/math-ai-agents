#!/usr/bin/env python3
"""Check staged companion links, identical reader states, and every DOM state.

This is deliberately separate from a browser check. A blocked browser never
receives a passing result from successful DOM or arithmetic tests.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import zipfile

from stage_publication import BOOK, REPO, SLUG, included, reader_payload, sha, write


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.links = []; self.ids = set(); self.text = []; self.excluded = 0
        self.skip_tags = {'style', 'script', 'pre', 'code', 'svg'}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if attrs.get(name):
                self.links.append((tag, name, attrs[name]))
        if tag in self.skip_tags:
            self.excluded += 1

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.excluded = max(0, self.excluded - 1)

    def handle_data(self, text):
        if not self.excluded:
            self.text.append(text)


def check_links(site: Path, github: Path, github_receipt: dict | None = None) -> dict:
    pages = {path.resolve(): Page(path.read_text()) for path in site.rglob('*.html')}
    problems = []; external = set(); local_count = 0; github_paths = set(); bad_public_links = []
    for page, parsed in pages.items():
        for tag, attr, value in parsed.links:
            url = urlsplit(value)
            if url.scheme == 'data':
                continue
            if url.scheme or url.netloc:
                external.add(value)
                if attr == 'src' and url.scheme in {'http', 'https'}:
                    problems.append({'page': str(page), 'url': value, 'problem': 'network-loaded resource'})
                prefix = REPO + '/blob/main/'
                if value.startswith(prefix):
                    rel = unquote(url.path.split('/blob/main/', 1)[1])
                    github_paths.add(rel)
                    if not (github / rel).is_file():
                        problems.append({'page': str(page), 'url': value, 'problem': 'GitHub path absent from staged repository'})
                continue
            if url.path.startswith('/'):
                # Public publishing routes are external website interfaces, not generated companion files.
                external.add('https://karpeles.com' + value)
                continue
            target = (page.parent / unquote(url.path)).resolve() if url.path else page
            if target.is_dir():
                target /= 'index.html'
            local_count += 1
            if url.path.endswith(('.md', '.ipynb')):
                bad_public_links.append({'page': str(page), 'url': value})
            if not target.is_file():
                problems.append({'page': str(page), 'url': value, 'problem': 'missing local file'})
            elif url.fragment and target.suffix == '.html':
                target_page = pages.get(target) or Page(target.read_text())
                if unquote(url.fragment) not in target_page.ids:
                    problems.append({'page': str(page), 'url': value, 'problem': 'missing fragment'})
    live = {'status': 'NOT_RUN', 'reason': 'No GitHub recursive-tree receipt provided.'}
    if github_receipt and github_receipt.get('status') == 'VERIFIED':
        missing = sorted(github_paths - set(github_receipt['paths']))
        live = {'status': 'VERIFIED' if not missing else 'NEEDS-REGEN',
                'commit': github_receipt['commit'], 'paths_checked': len(github_paths), 'missing_paths': missing,
                'scope': 'Path existence at the observed published commit. Revised contents remain staged.'}
        if missing:
            problems.append({'problem': 'New GitHub link paths need publication before website upload', 'paths': missing})
    return {'pages_checked': len(pages), 'local_links_checked': local_count,
            'github_paths_checked_in_staging': len(github_paths),
            'live_github_path_verification': live,
            'external_links': sorted(external), 'raw_notebook_or_markdown_links': bad_public_links,
            'problems': problems}


def check_public_copy(site: Path) -> dict:
    problems = []; mathematical_offline = []; preserved = []
    banned = re.compile(r'\b(?:precomputed|pre-computed|launcher|installation|install|extract(?:ed|ion)?|'
                        r'coming soon|in preparation)\b|calculated in advance|Demonstration C\d+-D\d+')
    for page in site.rglob('*.html'):
        text = ' '.join(Page(page.read_text()).text)
        for match in banned.finditer(text):
            context = text[max(0, match.start()-60):match.end()+80]
            mathematical_uses = ('extract primitive duration and reward timing', 'extracted available capability',
                                 "accepts 'extract', 'upload', 'link', 'secret'", 'Scale profiles and extraction profiles',
                                 'at least that much was extracted under one tested configuration')
            if any(phrase in context for phrase in mathematical_uses):
                preserved.append({'page': str(page), 'term': match.group(), 'context': context,
                                  'reason': 'Mathematical or data-analysis usage; not download instructions.'})
                continue
            problems.append({'page': str(page), 'term': match.group(),
                             'context': context})
        for match in re.finditer(r'\boffline\b', text):
            context = text[max(0, match.start()-60):match.end()+100]
            if 'updates are offline' in context:
                mathematical_offline.append({'page': str(page), 'context': context,
                                             'reason': 'Mathematical distinction between offline and online updates; retained to preserve correctness.'})
            else:
                problems.append({'page': str(page), 'term': 'offline', 'context': context})
        if '\u2014' in text or re.search(r'\s--\s', text):
            problems.append({'page': str(page), 'term': 'dash used as punctuation'})
    return {'status': 'VERIFIED' if not problems else 'NEEDS-REGEN', 'problems': problems,
            'preserved_mathematical_terminology': mathematical_offline + preserved,
            'method': 'Visible presentation prose; code, quoted outputs, scripts and SVG internals are excluded.'}


def check_repository_license(root: Path, github: Path) -> dict:
    source = root / 'LICENSE'; public = github / 'LICENSE'
    problems = []
    if not source.is_file() or not public.is_file():
        problems.append('Preserved repository LICENSE is missing')
    elif source.read_bytes() != public.read_bytes():
        problems.append('Public LICENSE differs from preserved repository LICENSE')
    readme = (github / 'README.md').read_text()
    if 'MIT License (see `LICENSE`)' not in readme or 'All rights reserved' in readme:
        problems.append('Repository README does not preserve the existing MIT licensing statement')
    return {'status': 'VERIFIED' if not problems else 'NEEDS-REGEN', 'problems': problems,
            'license_sha256': sha(public) if public.is_file() else None,
            'scope': 'Exact preserved LICENSE bytes and existing repository code-license statement.'}


def check_public_frames(site: Path) -> dict:
    problems = []; marked_pages = 0
    for page in site.rglob('*.html'):
        text = re.sub(r'<script\b[\s\S]*?</script>', '', page.read_text(), flags=re.I)
        navs = re.findall(r'<nav\b[^>]*class=["\'][^"\']*\bkml-publishing-frame\b[^"\']*["\'][^>]*>', text)
        stripped = re.sub(r'<!-- kml-publishing-frame:start -->[\s\S]*?<!-- kml-publishing-frame:end -->\n?', '', text)
        if len(navs) > 1:
            problems.append({'page': str(page), 'problem': 'Duplicate publisher navigation'})
        if navs:
            marked_pages += 1
            if 'class="kml-publishing-frame"' in stripped or 'publishing-frame.css' in stripped:
                problems.append({'page': str(page), 'problem': 'Publisher frame or stylesheet lacks integration markers'})
    return {'status': 'VERIFIED' if not problems else 'NEEDS-REGEN', 'marked_pages': marked_pages,
            'problems': problems,
            'scope': 'Generated frames are removable by publisher prebuild; actual website build checked separately.'}


def verify(root: Path, output: Path, report: Path, browser_receipt: Path | None, github_receipt: Path | None = None):
    root = root.resolve(); output = output.resolve()
    site = output / 'web/companions' / SLUG
    github = output / 'github' / SLUG
    manifest = json.loads((output / 'release-manifest.json').read_text())
    chapters = json.loads((root / 'chapter-map.json').read_text())
    comparisons = []; failures = []; state_count = 0; demo_count = 0
    for entry in chapters:
        canonical = reader_payload((root / entry['reader']).read_text())
        staged = reader_payload((site / entry['reader']).read_text())
        canonical.pop('engine', None); staged.pop('engine', None)
        same = canonical == staged
        canonical_notebook = root / entry['notebook']; public_notebook = github / entry['notebook']
        same_notebook = canonical_notebook.read_bytes() == public_notebook.read_bytes()
        comparisons.append({'chapter': entry['chapter'], 'reader_payload_identical': same,
                            'notebook_identical': same_notebook, 'notebook_sha256': sha(canonical_notebook),
                            'demonstrations': len(staged['demos']),
                            'states': sum(len(d['states']) for d in staged['demos'])})
        demo_count += len(staged['demos']); state_count += sum(len(d['states']) for d in staged['demos'])
        if not same:
            failures.append(f"Chapter {entry['chapter']}: canonical and website reader states differ")
        if not same_notebook:
            failures.append(f"Chapter {entry['chapter']}: staged notebook differs from canonical execution")
    reader_files = [str(site / c['reader']) for c in chapters]
    command = ['node', str(root / 'tools/readers/engine/dom_harness.js'), *reader_files]
    result = subprocess.run(command, capture_output=True, text=True)
    write(report.parent / 'web-dom-harness.log', result.stdout + result.stderr)
    dom = json.loads(result.stdout) if not result.returncode else {'status': 'NEEDS-REGEN', 'error': result.stderr}
    if result.returncode:
        failures.append('Website DOM harness failed')
    else:
        fields = ['equations_checked', 'demos', 'states_checked', 'control_changes', 'resets_checked',
                  'no_script_defaults', 'labelled_controls', 'predictions_checked', 'steps_checked',
                  'stepper_moves', 'panels_checked', 'pager_links']
        dom['totals'] = {key: sum(item.get(key, 0) for item in dom['reports']) for key in fields}
        if dom['totals']['states_checked'] != state_count or dom['totals']['demos'] != demo_count:
            failures.append('DOM harness counts differ from embedded demonstrations/states')
    github_evidence = json.loads(github_receipt.read_text()) if github_receipt and github_receipt.is_file() else None
    links = check_links(site, github, github_evidence)
    if links['problems'] or links['raw_notebook_or_markdown_links']:
        failures.append('Website link audit failed')
    copy = check_public_copy(site)
    if copy['problems']:
        failures.append('Public copy audit found package or developer wording')
    license_check = check_repository_license(root, github)
    if license_check['problems']:
        failures.append('Repository license preservation failed')
    frame_check = check_public_frames(site)
    if frame_check['problems']:
        failures.append('Publisher frame integration contract failed')
    home = (site / 'index.html').read_text()
    home_parser = Page(home)
    card_links = re.findall(r'<h3><a href="([^"]+)">', home)
    if Counter(card_links) != Counter(c['reader'] for c in chapters):
        failures.append('Home chapter cards differ from canonical chapter list')
    stats = re.findall(r'<li><b>(\d+)</b>(chapters|demonstrations)</li>', home)
    if dict((label, int(count)) for count, label in stats) != {'chapters': len(chapters), 'demonstrations': demo_count}:
        failures.append('Home statistics differ from built pages')
    integrity_problems = []
    for category, folder in [('canonical_files', root), ('site_files', site), ('github_files', github)]:
        for rel, digest in manifest[category].items():
            path = folder / rel
            if not path.is_file() or sha(path) != digest:
                integrity_problems.append({'category': category, 'path': rel})
    if integrity_problems:
        failures.append('Release manifest hashes are stale or missing')
    archives = []
    for archive_spec in manifest['archives']:
        archive_path = Path(archive_spec['path'])
        archive_problem = []
        if not archive_path.is_file() or sha(archive_path) != archive_spec['sha256']:
            archive_problem.append('Archive hash differs from release manifest')
        else:
            folder = site.parent.parent if archive_path.name.endswith('-site.zip') else github
            expected = {p.relative_to(folder).as_posix(): sha(p) for p in included(folder)}
            with zipfile.ZipFile(archive_path) as archive:
                if archive.testzip() is not None:
                    archive_problem.append('Archive CRC validation failed')
                actual = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}
            if actual != expected:
                archive_problem.append('Archive contents differ from staged files')
        archives.append({'path': str(archive_path), 'status': 'VERIFIED' if not archive_problem else 'NEEDS-REGEN',
                         'problems': archive_problem})
        if archive_problem:
            failures.append(f'{archive_path.name}: archive validation failed')
    laboratory_archive = site / 'downloads/math-ai-agents-lab.zip'
    laboratory_receipt = {'status': 'NOT_RUN', 'reason': 'No laboratory archive staged.'}
    if laboratory_archive.is_file():
        with zipfile.ZipFile(laboratory_archive) as archive:
            bad_crc = archive.testzip()
            archive_files = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}
        expected_files = {p.relative_to(root).as_posix(): sha(p) for p in included(root)}
        different = sorted(name for name in set(archive_files) | set(expected_files)
                           if archive_files.get(name) != expected_files.get(name))
        laboratory_receipt = {'status': 'VERIFIED' if not bad_crc and not different else 'NEEDS-REGEN',
                              'path': str(laboratory_archive), 'files': len(archive_files),
                              'sha256': sha(laboratory_archive), 'crc_problem': bad_crc,
                              'canonical_differences': different}
        if bad_crc or different:
            failures.append('Portable laboratory archive differs from current canonical companion')
    browser = (json.loads(browser_receipt.read_text()) if browser_receipt and browser_receipt.is_file()
               else {'status': 'NOT_RUN', 'reason': 'No real-browser receipt provided.'})
    receipt = {'status': 'VERIFIED' if not failures else 'NEEDS-REGEN',
               'scope': 'Staged file synchronization, public copy, link resolution and DOM behavior; no upload.',
               'counts': {'chapters': len(chapters), 'demonstrations': demo_count, 'states': state_count},
               'reader_and_notebook_comparisons': comparisons, 'dom_harness': dom,
               'links': links, 'public_copy': copy, 'repository_license': license_check,
               'publisher_frames': frame_check, 'integrity_problems': integrity_problems,
               'archives': archives,
               'laboratory_archive': laboratory_receipt,
               'real_browser': browser, 'failures': failures,
               'browser_acceptance': 'VERIFIED' if browser.get('status') == 'VERIFIED' else 'UNVERIFIED'}
    write(report, json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[2] / 'output/publication/unified-companion-2026-10-04')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--browser-receipt', type=Path)
    parser.add_argument('--github-receipt', type=Path)
    args = parser.parse_args()
    receipt = verify(args.root, args.output, args.report, args.browser_receipt, args.github_receipt)
    print(json.dumps({key: receipt[key] for key in ['status', 'counts', 'failures', 'browser_acceptance']}, indent=2))
    return 0 if not receipt['failures'] else 1


if __name__ == '__main__':
    sys.exit(main())
