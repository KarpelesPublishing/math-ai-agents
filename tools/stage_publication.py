#!/usr/bin/env python3
"""Build synchronized public companion files without publishing them.

The canonical companion is the source. The publisher checkout supplies its
shared stylesheets only; this command never writes outside the project.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit
import zipfile

BOOK = "The Mathematics of Artificial Intelligence Agents"
SUBTITLE = "A Readable Guide to Decisions, Planning, Memory, Tools, Learning, and Cooperation"
AUTHOR = "Jason Karpeles"
SLUG = "math-ai-agents"
REPO = f"https://github.com/KarpelesPublishing/{SLUG}"
BOOK_URL = f"https://karpeles.com/publishing/{SLUG}"
SITE_URL = f"https://karpeles.com/companions/{SLUG}/"
FRAME_START = '<!-- kml-publishing-frame:start -->'
FRAME_END = '<!-- kml-publishing-frame:end -->'
NOTICE = ("Examples distinguish declared teaching inputs from source-reported values. A figure shows "
          "what follows from the identified values and assumptions; it does not establish performance for a different agent.")
EXCLUDED_PARTS = {".venv", ".git", "__pycache__", ".pytest_cache", ".jupyter", ".local-state", "reader-output"}
EXCLUDED_NAMES = {".DS_Store", "setup-receipt.json"}
PUBLIC_FOLDERS = ("assets", "guide", "workbook", "solutions", "Companion", "data")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def included(root: Path):
    return sorted(p for p in root.rglob("*") if p.is_file()
                  and not EXCLUDED_PARTS.intersection(p.relative_to(root).parts)
                  and p.name not in EXCLUDED_NAMES and p.suffix not in {".pyc", ".pyo"})


def copy_tree(source: Path, destination: Path):
    for path in included(source):
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def relative(target: Path, page: Path) -> str:
    return os.path.relpath(target, page.parent).replace(os.sep, "/")


def github_link(path: str) -> str:
    return f"{REPO}/blob/main/{path}"


def publishing_frame(home_href: str) -> str:
    return (FRAME_START + '<nav class="kml-publishing-frame" aria-label="Publishing navigation">'
            '<a class="kml-publishing-brand" href="https://karpeles.com/publishing/">Karpeles Publishing</a><div>'
            f'<a href="{BOOK_URL}" class="kml-book-return">Back to the book</a>'
            '<a href="https://karpeles.com/publishing/books">Books</a>'
            '<a href="https://karpeles.com/publishing/companions">Companions</a>'
            '<a href="https://karpeles.com/publishing/listen">Listen</a>'
            f'<a href="{home_href}">All chapters</a></div></nav>' + FRAME_END)


def shared_links(site: Path, page: Path) -> str:
    links = []
    for name in ('companion.css', 'publishing-frame.css'):
        link = f'<link rel="stylesheet" href="{relative(site.parent / "_shared" / name, page)}">'
        links.append(FRAME_START + link + FRAME_END if name == 'publishing-frame.css' else link)
    return ''.join(links)


def repository_readme() -> str:
    return f'''# {BOOK}: companion notebooks and skills

*{SUBTITLE}*

Companion material for *{BOOK}* by {AUTHOR}. Each chapter has a
Jupyter notebook that reproduces its calculations and figures, and a skill
that an AI assistant can use to teach the chapter.

Interactive version: {SITE_URL}
About the book: {BOOK_URL}

## What is here

- `notebooks/`: one notebook per chapter, already run, so the results show on GitHub; orientation and a document-release capstone are included.
- `skills/`: a master skill for the book and one skill per chapter.
- Numeric chapter folders preserve existing skill links; `maa-` folders hold the same canonical skills used by the installer.
- `src/`, `tools/`, `data/`, and `tests/`: shared calculations, teaching inputs, and checks.
- `content/`, `assets/`, and `solutions/`: explanations, equations, figures and separate worked answers.

Examples identify constructed teaching inputs and source-reported measurements. Their assumptions and limits are stated with each calculation.

## Run the notebooks

You need Python 3.11 or later.

    pip install -r requirements.txt
    jupyter lab

Open any notebook in `notebooks/` and choose Run All. Keep the companion folders together.
For terminal commands, install the local package from the repository root:

    pip install -e .
    python -m math_ai_agents list
    python -m math_ai_agents run --chapter 6 --case example --text
    python -m math_ai_agents run --chapter 6 --input my-inputs.json --output report.json

Copy `data/examples/ch06.json`, or the file for your chapter, to get the input shape, then replace the values. The matching web demonstrations also run from the terminal:

    python -m math_ai_agents demo-list --chapter 6
    python -m math_ai_agents demo --chapter 6 --id C06-D01 --text

Run the checks with `python -m unittest discover -s tests`.

## Use the skills

Start with `skills/math-ai-agents/`, the master skill. It routes a question to a chapter method or demonstration. Each chapter skill names its equations, notebook and input contract.
Keep the repository together and use the same Python environment as the notebooks. Run the supplied installer from the repository root, for example:

    python tools/install_skills.py --target ~/.claude/skills

For Codex, use `--target ~/.codex/skills`. The installer selects the 28 canonical skills without duplicating numeric compatibility folders and records their runtime location. Keep the repository at that location. Existing skill folders are preserved. Run `python tools/install_skills.py --help` for its destination options.

## Copyright

Copyright {AUTHOR}. The code in this repository is released under the MIT License (see `LICENSE`).
'''


def footer(home_href: str, evidence_note: str = NOTICE) -> str:
    return (f'<footer class="cmp-footer"><div class="cmp-footer-inner">'
            f'<p class="cmp-footer-title"><em>{BOOK}</em> by {AUTHOR}</p>'
            f'<p class="cmp-footer-links"><a href="{home_href}">All chapters</a>'
            f'<a href="{BOOK_URL}">About the book</a><a href="{REPO}">GitHub</a></p>'
            f'<p class="cmp-footer-note">{html.escape(evidence_note)}</p></div></footer>')


def header(home_href: str, extra_links: list[tuple[str, str]], *, title: str = "",
           eyebrow: str = "", lead: str = "", summary: str = "") -> str:
    nav = ''.join(f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
                  for label, href in [("All chapters", home_href), *extra_links])
    title_block = ""
    if title:
        title_block = (f'<div class="cmp-title"><p class="cmp-eyebrow">{html.escape(eyebrow)}</p>'
                       f'<h1>{html.escape(title)}</h1><p class="cmp-lead">{html.escape(lead)}</p>'
                       f'<p class="cmp-summary">{html.escape(summary)}</p></div>')
    return (f'<header class="cmp-header"><div class="cmp-topbar"><a class="cmp-book" '
            f'href="{home_href}">{BOOK}</a><nav class="cmp-nav" aria-label="Companion navigation">'
            f'{nav}</nav></div>{title_block}</header>')


def reader_payload(text: str) -> dict:
    match = re.search(r'<script\b[^>]*id="reader-data"[^>]*>(.*?)</script>', text, re.S)
    if not match:
        raise ValueError("Reader has no embedded state data")
    return json.loads(match.group(1))


def clean_document(text: str, page: Path, site: Path, chapters: list[dict], evidence_note: str = NOTICE) -> str:
    """Adjust package instructions and URLs, preserving calculations and code."""
    text = re.sub(r'<nav>.*?</nav>', '', text, count=1, flags=re.S)
    text = re.sub(r'<p class="tag">Executed locally.*?</p>',
                  '<p class="tag">Calculated examples from the chapter notebook. '
                  'Constructed inputs do not measure deployed agents.</p>', text, flags=re.S)
    text = re.sub(r'(<h2>Technical Requirements</h2>)\s*<p>.*?</p>',
                  r'\1<p>Read the calculations and saved results here. '
                  f'To run or change them, use the <a href="{REPO}">notebooks on GitHub</a> '
                  'with Python 3.11 or later and the listed dependencies.</p>', text, flags=re.S)
    text = re.sub(r'<p class="tag">These pages are usable without Python.*?</p>',
                  f'<p class="tag">Read the examples here, or use the '
                  f'<a href="{REPO}">notebooks and chapter skills on GitHub</a>.</p>', text, flags=re.S)
    text = text.replace('The next cell finds the bundle and imports the same computation used by the chapter skill. '
                        'It does not change your system Python.',
                        'The next cell locates the companion files and imports the shared chapter calculation.')
    text = text.replace('Execution: completed locally; constructed inputs are not deployment measurements.',
                        'Constructed inputs are not deployment measurements.')
    text = text.replace('preserving offline reproducibility', 'preserving reproducibility')
    text = re.sub(r'<p>On Mac, double-click.*?</p>',
                  f'<p>To run the notebook, follow the <a href="{REPO}">GitHub instructions</a>. '
                  'The calculations use declared inputs and require no model subscription or API key.</p>', text, flags=re.S)
    text = re.sub(r'<p>The complete laboratory package adds.*?</p>',
                  f'<p>The <a href="{REPO}">chapter notebooks and assistant skills on GitHub</a> '
                  'use the same calculations as these pages. The master skill selects methods and their input contracts. '
                  'Assumptions remain part of every result. This workbook preserves the book problems and adds '
                  'chapter exercises with separate solutions.</p>', text, flags=re.S)
    text = re.sub(r'<p>Use this small manifest to compare a matching approval.*?</p>',
                  '<p>Use this manifest to compare a matching approval with a stale approval under the same '
                  f'document version. The <a href="{relative(site / "Companion/fixtures/release-probe.json", page)}">'
                  'release-probe input</a> contains the same values.</p>', text, flags=re.S)
    text = re.sub(r'<p>Run the simulator with this manifest.*?</p>',
                  '<p>Run the simulator from the repository folder that holds <code>scripts</code>. '
                  'The first command uses a manifest saved as <code>release-probe.json</code>; '
                  'the second uses the provided <code>Companion/fixtures/release-probe.json</code>.</p>', text, flags=re.S)
    text = text.replace('if that is your Python launcher.', 'if that is your Python command.')
    # Move the document's reading layout to its main element; publisher chrome remains full width.
    text = re.sub(r'(<style>)(.*?)</style>',
                  lambda match: match.group(1) + re.sub(r'\bbody\{', '.cmp-doc{', match.group(2)) + '</style>',
                  text, count=1, flags=re.S)
    # Package setup belongs to the GitHub instructions. Existing URLs stay valid.
    text = re.sub(r'<a href="[^"]*START-HERE\.md">[^<]*</a>',
                  f'<a href="{github_link("README.md")}">Run the notebooks</a>', text)

    def replace_link(match):
        prefix, href, suffix = match.groups()
        parsed = urlsplit(html.unescape(href))
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)
        target = (page.parent / parsed.path).resolve()
        if target.suffix.lower() not in {".md", ".ipynb"}:
            return match.group(0)
        try:
            target_rel = target.relative_to(site.resolve()).as_posix()
        except ValueError:
            raise ValueError(f"Document link escapes staged site: {href}")
        # Reading pages should lead to the rendered answer, not its Markdown source.
        if target.suffix.lower() == '.md' and Path(target_rel).parts[0] in {'solutions', 'workbook', 'guide'}:
            rendered = target.with_suffix('.html')
            if rendered.is_file():
                return prefix + relative(rendered, page) + ("#" + parsed.fragment if parsed.fragment else "") + suffix
        # The public repository has always used numeric chapter skill paths.
        # Canonical bundle paths remain available beside these compatibility aliases.
        if target_rel.startswith('skills/maa-'):
            target_rel = target_rel.replace('skills/maa-', 'skills/', 1)
        return prefix + github_link(target_rel) + ("#" + parsed.fragment if parsed.fragment else "") + suffix

    text = re.sub(r'(<a\b[^>]*href=")([^"]+)(")', replace_link, text)
    home_href = relative(site / "index.html", page)
    guide_href = relative(site / "guide/index.html", page)
    extra = [("Worked calculations", guide_href)]
    entry = next((c for c in chapters if Path(c["notebook"]).stem == page.stem), None)
    if entry:
        extra.extend([("Interactive chapter", relative(site / entry["reader"], page)),
                      ("Notebook on GitHub", github_link(entry["notebook"]))])
    text = text.replace('<html lang="en">', '<html lang="en" class="cmp-page cmp-text" data-theme="light">', 1)
    text = text.replace('</head>', shared_links(site, page) + '</head>', 1)
    text = re.sub(r'(<body[^>]*>)', r'\1' + publishing_frame(home_href) + header(home_href, extra)
                  + '<main class="cmp-doc" id="main">', text, count=1)
    text = text.replace('</body>', '</main>' + footer(home_href, evidence_note) + '</body>', 1)
    return text


def wrap_reader(text: str, page: Path, site: Path, entry: dict, neighbors: list[dict], evidence_note: str = NOTICE) -> str:
    """Keep engine content and state data; use the publisher's shared shell."""
    home_href = relative(site / "index.html", page)
    guide_path = site / "guide/chapters" / (Path(entry["notebook"]).stem + ".html")
    links = []
    if guide_path.exists():
        links.append(("Worked calculations", relative(guide_path, page)))
    links.append(("Notebook on GitHub", github_link(entry["notebook"])))
    for neighbor in neighbors:
        label = "Previous chapter" if neighbor["chapter"] < entry["chapter"] else "Next chapter"
        links.append((label, relative(site / neighbor["reader"], page)))
    old_header = re.search(r'<header>.*?</header>', text, re.S)
    if not old_header:
        raise ValueError(f"Expected reader header missing: {page}")

    def paragraph(cls):
        m = re.search(r'<p class="' + cls + r'">(.*?)</p>', old_header.group(), re.S)
        return html.unescape(re.sub('<[^>]+>', '', m.group(1))) if m else ""

    summary = re.search(r'<p>(.*?)</p>', old_header.group(), re.S)
    chapter_nav = re.search(r'<nav class="chapter-nav".*?</nav>', old_header.group(), re.S)
    new_header = header(home_href, links, title=entry["title"], eyebrow=f'Chapter {entry["chapter"]}',
                        lead=paragraph("lead"), summary=html.unescape(summary.group(1)) if summary else "")
    notice = re.search(r'<p class="notice">.*?</p>', old_header.group(), re.S)
    if notice:
        new_header = new_header.replace('</div></header>', notice.group() + '</div></header>')
    if chapter_nav:
        new_header = new_header.replace('</header>', chapter_nav.group() + '</header>')
    text = text[:old_header.start()] + new_header + text[old_header.end():]
    text = re.sub(r'<footer>.*?</footer>', footer(home_href, evidence_note), text, count=1, flags=re.S)
    text = text.replace('</head>', shared_links(site, page) + '</head>', 1)
    text = text.replace('<body>', '<body>' + publishing_frame(home_href), 1)
    text = text.replace('class="no-js"', 'class="no-js cmp-page"', 1)
    return text


def home_page(chapters: list[dict], readers: dict[int, dict], site: Path, evidence_note: str = NOTICE) -> str:
    demo_count = sum(len(v["demos"]) for v in readers.values())
    cards = []
    for entry in chapters:
        number = entry["chapter"]
        if number not in readers:
            continue
        cards.append(f'<li class="cmp-card"><div class="cmp-card-top"><span class="cmp-num">{number}</span>'
                     f'<span class="cmp-count">{len(readers[number]["demos"])} demonstrations</span></div>'
                     f'<h3><a href="{entry["reader"]}">{html.escape(entry["title"])}</a></h3>'
                     f'<p class="cmp-card-summary">{html.escape(entry["outcome"])}</p><div class="cmp-actions">'
                     f'<a href="{entry["reader"]}">Open chapter</a>'
                     f'<a href="{github_link(entry["notebook"])}">Notebook on GitHub</a></div></li>')
    extras = [("Worked calculations", "guide/index.html"), ("Workbook", "workbook/workbook.html"),
              ("Separate solutions", "workbook/solutions.html"), ("Notation guide", "workbook/notation-guide.html"),
              ("Release console", "Companion/release-console.html")]
    extras_html = ''.join(f'<li><a href="{href}">{label}</a></li>' for label, href in extras if (site / href).exists())
    return (f'<!doctype html>\n<html lang="en" class="cmp-page cmp-home"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{BOOK}: Interactive companion</title>'
            f'<meta name="description" content="Interactive figures and calculations for each chapter of {BOOK}.">'
            + shared_links(site, site / 'index.html') + '</head><body>'
            + publishing_frame("index.html") + header("index.html", [("About the book", BOOK_URL), ("GitHub", REPO)]) +
            f'<div class="cmp-masthead"><div class="cmp-wrap"><h1>{BOOK}</h1><p class="cmp-byline">By {AUTHOR}</p>'
            f'<p class="cmp-intro">{SUBTITLE}</p>'
            f'<p class="cmp-intro">Interactive figures and calculations for each chapter of <em>{BOOK}</em>.</p>'
            f'<ul class="cmp-stats"><li><b>{len(readers)}</b>chapters</li><li><b>{demo_count}</b>demonstrations</li></ul>'
            '</div></div><main class="cmp-wrap" id="main"><section class="cmp-part"><h2>Choose a chapter</h2>'
            '<ul class="cmp-grid">' + ''.join(cards) + '</ul></section>'
            f'<section class="cmp-more"><h2>More for this book</h2><ul>{extras_html}</ul></section>'
            '<section class="cmp-github"><h2>Notebooks and skills on GitHub</h2>'
            '<p>Each chapter notebook develops the same examples and figures. Chapter skills and the master skill help '
            f'an assistant select and teach the relevant method.</p><p><a href="{REPO}">{REPO}</a></p></section>'
            '</main>' + footer("index.html", evidence_note) + '</body></html>\n')


def reproducible_zip(source: Path, archive_path: Path, prefix: str = "") -> dict:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in included(source):
            name = str(Path(prefix) / path.relative_to(source)).replace(os.sep, '/')
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if path.suffix == '.command' else 0o100644) << 16
            archive.writestr(info, path.read_bytes())
    return {'path': str(archive_path), 'bytes': archive_path.stat().st_size, 'sha256': sha(archive_path)}


def build(root: Path, output: Path, publisher_public: Path, lab_zip: Path | None) -> dict:
    root = root.resolve(); output = output.resolve(); project = root.parent
    if not output.is_relative_to(project / 'output/publication'):
        raise ValueError('Publication staging must be inside the project output/publication directory')
    output.mkdir(parents=True, exist_ok=True)
    github = output / 'github' / SLUG
    site = output / 'web' / 'companions' / SLUG
    shared = site.parent / '_shared'
    for target in (github, site, shared):
        if (target / '.git').exists():
            raise ValueError(f'Refusing to replace a versioned checkout: {target}')
    if not (root / 'LICENSE').is_file():
        raise ValueError('Preserved repository LICENSE is required before publication staging')
    # An interrupted rebuild must never leave an earlier receipt looking current.
    (output / 'release-manifest.json').unlink(missing_ok=True)
    for target in (github, site, shared):
        if target.exists():
            shutil.rmtree(target)
    chapters = json.loads((root / 'chapter-map.json').read_text())
    source_hashes = {p.relative_to(root).as_posix(): sha(p) for p in included(root)}
    copy_tree(root, github)
    aliases = []
    for entry in chapters:
        canonical_skill = Path(entry['skill_path']).parent
        alias_skill = canonical_skill.with_name(canonical_skill.name.removeprefix('maa-'))
        copy_tree(root / canonical_skill, github / alias_skill)
        aliases.append({'canonical': canonical_skill.as_posix(), 'published_alias': alias_skill.as_posix()})
    # Install the canonical registry once, even though legacy URL aliases also exist.
    # This adjustment applies to staging only; the portable bundle still has 28 folders.
    installer = github / 'tools/install_skills.py'
    installer_text = installer.read_text()
    helper = '''def skill_sources(root):
    """Select canonical skills from the registry, excluding URL compatibility aliases."""
    entries = json.loads((root / "chapter-map.json").read_text(encoding="utf-8"))
    return sorted([root / "skills/math-ai-agents/SKILL.md",
                   *(root / entry["skill_path"] for entry in entries)])


'''
    installer_text = installer_text.replace('def install(root:', helper + 'def install(root:', 1)
    installer_text = installer_text.replace('sorted((root / "skills").glob("*/SKILL.md"))', 'skill_sources(root)')
    write(installer, installer_text)
    write(github / 'README.md', repository_readme())
    shutil.copyfile(root / 'requirements-notebooks.txt', github / 'requirements.txt')
    # Recompute the repository's integrity file because README and requirements are public interfaces.
    gh_files = {p.relative_to(github).as_posix(): sha(p) for p in included(github) if p.name != 'file-integrity.json'}
    write(github / 'file-integrity.json', json.dumps({'algorithm': 'sha256', 'files': gh_files}, indent=2) + '\n')
    for folder in PUBLIC_FOLDERS:
        if (root / folder).is_dir():
            copy_tree(root / folder, site / folder)
    shared.mkdir(parents=True, exist_ok=True)
    for css in ('companion.css', 'publishing-frame.css'):
        shutil.copyfile(publisher_public / '_shared' / css, shared / css)
    config = json.loads((root / 'tools/readers/reader.config.json').read_text())
    config['project']['root'] = str(root)
    config['output_dir'] = str(site / 'readers')
    config['web'] = True
    config['pager'] = True
    # This is the existing reader presentation, also used by the published snapshot.
    # The publisher's shared sheet supplies the same shell as the other companions.
    config['theme_css'] = str(root / 'theme/reader-theme.css')
    config['branding'].update(series_line=BOOK, index_title='Interactive chapters',
                             index_back_href='../index.html', index_back_label='All chapters')
    evidence_note = config['branding'].get('footer_note', NOTICE)
    config['links'] = {'index': {'href': '../../index.html'},
                       'notebook': {'href': f'{REPO}/blob/main/notebooks/{{slug}}.ipynb',
                                    'label': 'Notebook on GitHub'}}
    config_path = output / 'web-reader.config.json'
    write(config_path, json.dumps(config, indent=2) + '\n')
    result = subprocess.run([sys.executable, str(root / 'tools/readers/engine/build_readers.py'),
                             '--config', str(config_path), '--chapters', 'all'],
                            capture_output=True, text=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    write(output / 'web-reader-build.log', result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'Web readers did not build; see {output / "web-reader-build.log"}')
    payloads = {}
    for index, entry in enumerate(chapters):
        page = site / entry['reader']
        text = page.read_text()
        payloads[entry['chapter']] = reader_payload(text)
        neighbors = chapters[max(0, index - 1):index] + chapters[index + 1:index + 2]
        write(page, wrap_reader(text, page, site, entry, neighbors, evidence_note))
    for folder in ('guide', 'workbook', 'solutions'):
        for page in (site / folder).rglob('*.html'):
            write(page, clean_document(page.read_text(), page, site, chapters, evidence_note))
    write(site / 'index.html', home_page(chapters, payloads, site, evidence_note))
    # Keep the older catalogue URL, serving the same home interface at its original depth.
    write(site / 'readers/index.html', '<!doctype html><html lang="en"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Interactive chapters</title>'
          '<meta http-equiv="refresh" content="0;url=../index.html"></head><body>'
          '<p><a href="../index.html">All chapters</a></p></body></html>\n')
    if lab_zip:
        destination = site / 'downloads/math-ai-agents-lab.zip'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(lab_zip, destination)
    site_archive = reproducible_zip(output / 'web', output / 'math-ai-agents-site.zip')
    gh_archive = reproducible_zip(github, output / 'math-ai-agents-github.zip')
    manifest = {'schema': 1, 'publication': 'staged only; no upload or repository mutation',
                'canonical_root': str(root), 'repository': REPO, 'website': SITE_URL,
                'counts': {'chapters': len(chapters), 'demonstrations': sum(len(v['demos']) for v in payloads.values()),
                           'states': sum(len(d['states']) for v in payloads.values() for d in v['demos']),
                           'notebooks': len(list((github / 'notebooks').glob('*.ipynb'))),
                           'skills': len(list((root / 'skills').glob('*/SKILL.md'))),
                           'skill_url_aliases': len(aliases)},
                'compatibility_skill_aliases': aliases,
                'canonical_files': source_hashes,
                'shared_styles': {p.name: sha(p) for p in shared.glob('*.css')},
                'site_files': {p.relative_to(site).as_posix(): sha(p) for p in included(site)},
                'github_files': {p.relative_to(github).as_posix(): sha(p) for p in included(github)},
                'archives': [site_archive, gh_archive]}
    write(output / 'release-manifest.json', json.dumps(manifest, indent=2) + '\n')
    return {'output': str(output), 'counts': manifest['counts'], 'archives': manifest['archives']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[2] / 'output/publication/unified-companion-2026-10-04')
    parser.add_argument('--publisher-public', type=Path, default=Path('/Users/jasonkarpeles/Documents/Github/kml-website/apps/web/public/companions'))
    parser.add_argument('--lab-zip', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.root, args.output, args.publisher_public, args.lab_zip), indent=2))


if __name__ == '__main__':
    main()
