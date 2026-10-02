#!/usr/bin/env python3
"""Export executed laboratories as self-contained local reading pages."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE = '''body{max-width:920px;margin:40px auto;padding:0 24px;color:#20282c;background:#fff;font:17px/1.65 Georgia,serif}h1,h2,h3,nav,.tag{font-family:Arial,sans-serif;line-height:1.25}h1{font-size:32px}h2{margin-top:2.5em;font-size:23px}h3{margin-top:1.8em}a{color:#31586b}pre{padding:16px;background:#f3f5f5;overflow:auto;font:13px/1.5 Menlo,Consolas,monospace;white-space:pre-wrap}code{font:14px Menlo,Consolas,monospace}img,svg{max-width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:8px;border-bottom:1px solid #cdd3d6;text-align:left}.output{border-left:3px solid #ccd3d7;margin:18px 0;padding-left:16px}.tag{font-size:14px;color:#566168}.search{width:100%;box-sizing:border-box;padding:12px;font:16px Arial,sans-serif}.chapter{padding:14px 0;border-bottom:1px solid #d7dcde}.chapter p{margin:4px 0}.math-source{font-size:12px}nav{font-size:14px;margin-bottom:30px}@media print{body{margin:0;max-width:none;font-size:11pt}nav,.search{display:none}h2,h3{break-after:avoid}pre,.output{break-inside:avoid}}'''


def visible_tex(tex):
    # Component-set braces are literal sets, not invisible TeX grouping.
    return re.sub(r"(?<=\(){(\\theta[^}]*)}", lambda m: r"\{" + m.group(1) + r"\}", tex)


def math_inline(text):
    def span(tex):
        escaped = html.escape(visible_tex(tex))
        for symbol, entity in [("\\", "&#92;"), ("_", "&#95;"), ("*", "&#42;"), ("[", "&#91;"), ("]", "&#93;")]:
            escaped = escaped.replace(symbol, entity)
        return '<span class="math">&#92;(' + escaped + '&#92;)</span>'
    pieces = re.split(r"(```.*?```|`[^`\n]*`)", text, flags=re.S)
    for i, piece in enumerate(pieces):
        if i % 2:
            if not piece.startswith("```") and "\\" in piece:
                pieces[i] = span(piece[1:-1])
        else:
            pieces[i] = re.sub(r"(?<!\$)\$([^\n$]+)\$(?!\$)", lambda m: span(m.group(1)), piece)
            pieces[i] = re.sub(r"(?<=[0-9)])\*(?=[0-9(])", "&#42;", pieces[i])
    return "".join(pieces)


def page(title, body, asset_prefix="../assets", nav="index.html"):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><style>{STYLE}</style><script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)'],['$','$']],displayMath:[['\\\\[','\\\\]'],['$$','$$']],packages:['base','ams','newcommand','noundefined']}},svg:{{fontCache:'local'}}}};</script><script defer src="{asset_prefix}/mathjax/tex-svg.js"></script></head><body><nav><a href="{nav}">Laboratory guide</a></nav>{body}</body></html>'''


def render_md(text):
    import markdown
    return markdown.markdown(math_inline(text), extensions=["fenced_code", "tables", "sane_lists"])


def notebook_sections(nb, name="notebook"):
    """Render a notebook dict to HTML sections: prose, code, and every saved output."""
    sections = []
    for cell in nb["cells"]:
        source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        if cell["cell_type"] == "markdown":
            rendered = render_md(source)
            rendered = rendered.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
            sections.append(rendered)
        elif cell["cell_type"] == "code":
            sections.append("<pre><code>" + html.escape(source) + "</code></pre>")
            for output in cell.get("outputs", []):
                if output["output_type"] == "error":
                    raise ValueError("Cannot export failed notebook: " + name)
                if "text" in output:
                    value = output["text"]
                    sections.append('<div class="output"><pre>' + html.escape("".join(value) if isinstance(value, list) else value) + "</pre></div>")
                elif "image/svg+xml" in output.get("data", {}):
                    value = output["data"]["image/svg+xml"]
                    sections.append('<div class="output">' + ("".join(value) if isinstance(value, list) else value) + "</div>")
                elif "text/plain" in output.get("data", {}):
                    value = output["data"]["text/plain"]
                    sections.append('<div class="output"><pre>' + html.escape("".join(value) if isinstance(value, list) else value) + "</pre></div>")
    return sections


def export_notebook(path):
    nb = json.loads(path.read_text())
    sections = notebook_sections(nb, path.name)
    executed = nb["metadata"].get("lab_execution")
    if not executed:
        raise ValueError("Notebook has no current execution metadata: " + path.name)
    prefix = '<p class="tag">Executed locally with a fresh process and IPython kernel. This page is a reading edition; it does not run code. Constructed examples do not measure deployed agents.</p>'
    readers = {Path(e["notebook"]).stem: e["reader"] for e in json.loads((ROOT / "chapter-map.json").read_text())}
    if path.stem in readers:
        prefix = f'<p class="tag"><a href="../../{readers[path.stem]}">Illustrated reader for this chapter</a> · <a href="../../readers/index.html">All illustrated readers</a></p>' + prefix
    destination = ROOT / "guide/chapters" / (path.stem + ".html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page(path.stem, prefix + "\n".join(sections), "../../assets", "../index.html"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mathjax-source", type=Path)
    args = parser.parse_args()
    if args.mathjax_source:
        destination = ROOT / "assets/mathjax"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.mathjax_source / "es5/tex-svg.js", destination / "tex-svg.js")
        shutil.copy2(args.mathjax_source / "LICENSE", destination / "LICENSE")
    if not (ROOT / "assets/mathjax/tex-svg.js").exists():
        raise ValueError("Offline MathJax asset missing; supply --mathjax-source for the first build.")
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        export_notebook(path)
    for path in [*(ROOT / "workbook").glob("*.md"), *(ROOT / "solutions").glob("*.md")]:
        path.with_suffix(".html").write_text(page(path.stem, render_md(path.read_text()), "../assets", "../guide/index.html"))
    chapters = json.loads((ROOT / "chapter-map.json").read_text())
    cards = []
    for entry in chapters:
        stem = Path(entry["notebook"]).stem
        cards.append(f'''<section class="chapter"><h2><a href="chapters/{stem}.html">{entry['chapter']:02d}: {html.escape(entry['title'])}</a></h2><p>{html.escape(entry['outcome'])}</p><p class="tag"><a href="../{entry['notebook']}">Notebook</a> · <a href="../{entry['skill_path']}">Skill</a> · <a href="../{entry['reader']}">Illustrated reader</a> · <a href="../{entry['example_input']}">Input example</a> · <a href="../solutions/ch{entry['chapter']:02d}.html">Solutions</a></p></section>''')
    body = '''<h1>The Mathematics of AI Agents</h1><p>A laboratory companion by Jason Karpeles. Choose a mathematical question, inspect the calculation, then change an assumption or use your own documented inputs.</p><p><a href="chapters/00-start-here.html">Start with one successful calculation</a> · <a href="chapters/28-document-release-capstone.html">Follow a complete release controller</a></p><p><a href="../readers/index.html">Illustrated readers</a> · <a href="../workbook/workbook.html">Standalone workbook</a> · <a href="../workbook/solutions.html">Separate answers</a> · <a href="../workbook/notation-guide.html">Notation guide</a> · <a href="../START-HERE.md">Setup and recovery</a> · <a href="../Companion/release-console.html">Release console mock-up (Chapter 18)</a></p><p class="tag">These pages are usable without Python or an account. To change and execute code, use the notebook launcher. To apply a method with an assistant, install the chapter skills and master skill through the launcher.</p><label for="search">Find a question or chapter</label><input class="search" id="search" type="search" placeholder="For example: memory, utility, retry, delegation"><div id="chapters">''' + "\n".join(cards) + '''</div><script>document.getElementById('search').addEventListener('input',function(){const query=this.value.toLowerCase();for(const item of document.querySelectorAll('.chapter')){item.hidden=!item.textContent.toLowerCase().includes(query);}});</script>'''
    (ROOT / "guide/index.html").write_text(page("Mathematics of AI Agents Laboratory", body, "../assets", "index.html"))
    print("Exported executed notebook pages, workbook, answers and local guide.")


if __name__ == "__main__": main()
