#!/usr/bin/env python3
"""Illustrated reader engine: validate chapter modules and build offline readers.

Each chapter module defines CHAPTER with four demonstrations. For every
combination of a demonstration's discrete controls the engine calls the
figure function, checks the result, stores the figure as a cleaned SVG and
embeds every state in one self-contained HTML page. A short script swaps the
precomputed state when a reader changes a control. Reading needs no network
and no Python.

Usage
  python build_readers.py --config reader.config.json --chapters 6 --check
  python build_readers.py --config reader.config.json --chapters all
  python build_readers.py --config reader.config.json --chapters 1 2 --out /tmp/readers

--check runs every figure function for every state and validates the
contract, but writes nothing. Without --check, readers and the index are
written to the configured output directory (or --out).
"""
from __future__ import annotations

import argparse
import base64
import html
import importlib
import importlib.util
import io
import itertools
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
ENGINE_VERSION = "1.0.0"
DEPENDENCIES = ("numpy", "matplotlib", "jinja2")
sys.dont_write_bytecode = True

REQUIRED_CHAPTER_FIELDS = ("number", "title", "subtitle", "summary", "demos")
REQUIRED_DEMO_FIELDS = (
    "id", "title", "question", "equations", "symbols", "prediction", "explanation",
    "application", "assumptions", "check", "answer", "provenance", "source_section",
    "source_anchor", "controls", "function",
)
DEFAULT_BUDGETS = {
    "demos_per_chapter": 4,
    "max_states_per_demo": 8,
    "min_values_per_control": 2,
    "max_values_per_control": 4,
    "max_reader_bytes": 2_500_000,
    "max_total_bytes": 45_000_000,
    "min_font_points": 9.5,
}
DEFAULT_FORBIDDEN_TERMS = [
    "matplotlib", "numpy", "scipy", "jinja", "pandas", "jupyter", "pip install",
    "conda", "python", "node.js",
]
DEFAULT_EMPIRICAL_PHRASES = [
    "studies show", "research shows", "data show", "industry average",
    "in production we measured", "real-world data", "survey found",
]
DASHES = {"\u2014": "em dash", "\u2013": "en dash", "\u2012": "figure dash", "\u2015": "horizontal bar", "\u2212": "unicode minus"}
HAND_CALC = re.compile(
    r"\(?-?\d+(?:\.\d+)?\)?\s*(?:[x*/+]|\s-\s)\s*\(?-?\d+(?:\.\d+)?\)?[^=]{0,160}=\s*\(?-?\d"
)
NONFINITE_WORD = re.compile(r"(?<![A-Za-z])(nan|inf|infinity)(?![A-Za-z])", re.I)


class ContractError(Exception):
    """A chapter does not satisfy the reader contract."""


# Section: utilities

def require_dependencies():
    missing = []
    for name in DEPENDENCIES:
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    if missing:
        raise SystemExit(
            "The reader engine needs the Python packages numpy, matplotlib and jinja2. "
            f"Missing from {sys.executable}: {', '.join(missing)}. "
            "Run the builder with an environment that provides them."
        )


def dash_problems(text):
    found = [name for ch, name in DASHES.items() if ch in text]
    if "--" in text:
        found.append("double hyphen")
    return found


def iter_strings(value, path="CHAPTER"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from iter_strings(v, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from iter_strings(v, f"{path}[{i}]")


def normalize_tex(tex):
    """Whitespace, brace, tag, spacing-command and trailing-punctuation normalization."""
    t = re.sub(r"\\tag\*?\{[^{}]*\}", "", tex)
    t = re.sub(r"\\(?:qquad|quad)(?![A-Za-z])|\\[,;:!]", "", t)
    t = re.sub(r"\s+", "", t)
    t = t.replace("{", "").replace("}", "")
    return t.rstrip(".,;")


def strip_code_fences(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def text_equations(text):
    """Display and inline mathematics found in a Markdown or HTML chapter file."""
    body = strip_code_fences(text)
    found = []
    for pattern in (r"\\\[(.*?)\\\]", r"\$\$(.*?)\$\$", r"\\\((.*?)\\\)"):
        found += [m.group(1) for m in re.finditer(pattern, body, re.S)]
    without_display = re.sub(r"\$\$.*?\$\$", "", body, flags=re.S)
    found += [m.group(1) for m in re.finditer(r"(?<![\\$])\$([^\n$]+)\$", without_display)]
    found += [m.group(1) for m in re.finditer(r"`([^`\n]+)`", body)]
    return found


def text_headings(text):
    heads = [m.group(1) for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M)]
    heads += [re.sub(r"<[^>]+>", "", m.group(1)) for m in re.finditer(r"<h[1-6][^>]*>(.*?)</h[1-6]>", text, re.S | re.I)]
    return [clean_heading(h) for h in heads]


def clean_heading(text):
    text = re.sub(r"[*_`]", "", html.unescape(text))
    return re.sub(r"\s+", " ", text).strip()


def slugify(text):
    text = clean_heading(text).lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def display_value(value):
    """Display policy for metric values and control values."""
    if hasattr(value, "item") and getattr(value, "size", 1) == 1:
        value = value.item()
    if isinstance(value, bool) or value is None:
        raise ContractError(f"metric value {value!r}: use a string, int or float (write undefined values as text)")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError("metric value is NaN or infinite; state why it is undefined as text")
        text = f"{value:.6g}"
        return "0" if text == "-0" else text
    if isinstance(value, str):
        return value
    raise ContractError(f"metric value of type {type(value).__name__}; use str, int or float")


def svg_data_uri(svg_text):
    return "data:image/svg+xml;base64," + base64.b64encode(svg_text.encode("utf-8")).decode("ascii")


def clean_svg(raw):
    """Drop prolog, comments and metadata, round coordinates, collapse whitespace."""
    s = re.sub(r"<\?xml[^>]*\?>", "", raw)
    s = re.sub(r"<!DOCTYPE[^>]*>", "", s)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)

    def rounded(m):
        text = f"{float(m.group(0)):.2f}".rstrip("0").rstrip(".")
        return "0" if text in ("-0", "") else text

    # Round numbers inside tags only (coordinates, path data); never touch text content.
    s = re.sub(r"<[^>]+>", lambda tag: re.sub(r"-?\d+\.\d{3,}", rounded, tag.group(0)), s)
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s*\n\s*", " ", s)
    return s.strip()


# Section: project

class Project:
    """Everything project specific comes from the configuration file."""

    def __init__(self, config_path):
        self.config_path = Path(config_path).resolve()
        if not self.config_path.is_file():
            raise SystemExit(f"Configuration file not found: {self.config_path}")
        self.cfg = json.loads(self.config_path.read_text(encoding="utf-8"))
        project = self.cfg.get("project", {})
        self.root = (self.config_path.parent / project.get("root", ".")).resolve()
        self.branding = self.cfg.get("branding", {})
        for key in ("book_title", "series_line"):
            if not self.branding.get(key):
                raise SystemExit(f"Configuration needs branding.{key}")
        self.modules_dir = self.path(self.cfg.get("chapter_modules", "chapters"))
        self.module_pattern = self.cfg.get("module_pattern", "ch{number:02d}.py")
        self.out_dir = self.path(self.cfg.get("output_dir", "readers"))
        # Link targets are checked against the configured output location, so a
        # build written elsewhere with --out produces identical bytes.
        self.link_base = self.out_dir
        self.python_paths = [self.path(p) for p in self.cfg.get("python_paths", [])]
        self.budgets = {**DEFAULT_BUDGETS, **self.cfg.get("budgets", {})}
        rules = self.cfg.get("text_rules", {})
        self.forbidden_terms = rules.get("forbidden_terms", DEFAULT_FORBIDDEN_TERMS)
        self.empirical_phrases = rules.get("empirical_phrases", DEFAULT_EMPIRICAL_PHRASES)
        self.provenance_word = rules.get("provenance_must_include", "")
        self.links = self.cfg.get("links", {})
        self.math = self.cfg.get("math", {})
        self.style = self.cfg.get("style", {})
        self.chapters = self._load_chapters()

    def path(self, value):
        p = Path(value)
        return p if p.is_absolute() else (self.root / p).resolve()

    def _load_chapters(self):
        spec = self.cfg.get("chapter_list")
        if not spec:
            raise SystemExit("Configuration needs chapter_list (inline list or a file with field names)")
        if "inline" in spec:
            items, fields = spec["inline"], {"number": "number", "title": "title", "slug": "slug"}
            slug_mode, eq_spec = "value", spec.get("equations")
        else:
            data = json.loads(self.path(spec["path"]).read_text(encoding="utf-8"))
            items = data[spec["items_key"]] if spec.get("items_key") else data
            fields = {"number": "number", "title": "title", "slug": "slug", **spec.get("fields", {})}
            slug_mode, eq_spec = spec.get("slug_mode", "value"), spec.get("equations")
        chapters = {}
        for raw in items:
            number = int(raw[fields["number"]])
            slug = str(raw[fields["slug"]])
            if slug_mode == "path_stem":
                slug = Path(slug).stem
            equations = []
            if eq_spec:
                for eq in raw.get(eq_spec["field"], []) or []:
                    tex = eq if isinstance(eq, str) else eq.get(eq_spec.get("tex", "tex"), "")
                    asset = None if isinstance(eq, str) else eq.get(eq_spec.get("asset", "asset"))
                    equations.append({"tex": tex, "asset": self.path(asset) if asset else None})
            chapters[number] = {"number": number, "title": raw[fields["title"]], "slug": slug, "raw": raw, "equations": equations}
        return dict(sorted(chapters.items()))

    def module_path(self, number):
        return self.modules_dir / self.module_pattern.format(number=number)

    def authored_numbers(self):
        return [n for n in self.chapters if self.module_path(n).is_file()]

    def canonical_text(self, number):
        """Return (path or None, note). Raises ContractError for a forbidden path."""
        spec = self.cfg.get("canonical_text")
        if not spec:
            return None, "no canonical_text configured"
        forbidden = spec.get("forbidden", [])
        candidate, origin = None, None
        manifest = spec.get("manifest")
        if manifest and self.path(manifest["path"]).is_file():
            data = json.loads(self.path(manifest["path"]).read_text(encoding="utf-8"))
            items = data[manifest["list_key"]] if manifest.get("list_key") else data
            wanted = manifest["id_format"].format(number=number)
            for item in items:
                if str(item.get(manifest["id_key"])) == wanted:
                    candidate, origin = (manifest.get("base", "."), item[manifest["path_key"]]), "manifest"
                    break
        if candidate is None and spec.get("paths", {}).get(str(number)):
            candidate, origin = (spec.get("base", "."), spec["paths"][str(number)]), "paths"
        if candidate is None and spec.get("field"):
            value = self.chapters.get(number, {}).get("raw", {}).get(spec["field"])
            if value:
                candidate, origin = (spec.get("field_base", "."), value), "chapter list field"
        if candidate is None:
            return None, "no canonical chapter path known"
        base, relative = candidate
        for bad in forbidden:
            if bad in str(relative).replace("\\", "/"):
                raise ContractError(f"canonical text path {relative} is under the forbidden location {bad}")
        path = self.path(Path(base) / relative)
        if not path.is_file():
            if spec.get("required"):
                raise ContractError(f"canonical chapter text not found: {path}")
            return None, f"canonical chapter text not available ({origin}: {relative}); section headings not checked"
        return path, f"{origin}: {relative}"

    def link_targets(self, number):
        """Links from a reader, as (key, label, href). Omitted when unset or the target is missing."""
        chapter = self.chapters[number]
        values = {**{k: v for k, v in chapter["raw"].items() if isinstance(v, (str, int))},
                  "number": number, "number02": f"{number:02d}", "slug": chapter["slug"]}
        out, notes = [], []
        for key in ("notebook", "skill", "guide"):
            spec = self.links.get(key)
            if not spec:
                continue
            try:
                href = spec["href"].format_map(values)
            except KeyError as exc:
                notes.append(f"{key} link omitted: no field {exc}")
                continue
            target = (self.link_base / chapter["slug"] / href).resolve()
            if spec.get("require_target", True) and not target.exists():
                notes.append(f"{key} link omitted: target {target} not found")
                continue
            out.append((key, spec.get("label", key.title()), href))
        return out, notes


# Section: loading and validation

def load_module(project, number):
    path = project.module_path(number)
    for p in [ENGINE, *project.python_paths]:
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    name = f"reader_chapter_{number:02d}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "CHAPTER"):
        raise ContractError(f"{path.name} defines no CHAPTER")
    return module


def check_text(project, where, text, errors, computed=False):
    for problem in dash_problems(text):
        errors.append(f"{where}: contains {problem}; use an ASCII hyphen, comma, colon or parentheses")
    lower = text.lower()
    for term in project.forbidden_terms:
        if re.search(r"(?<![a-z])" + re.escape(term.lower()) + r"(?![a-z])", lower):
            errors.append(f"{where}: mentions the software dependency '{term}'; reader text must not")
    for phrase in project.empirical_phrases:
        if phrase.lower() in lower:
            errors.append(f"{where}: phrase '{phrase}' suggests an empirical claim; examples must be constructed")
    if computed and NONFINITE_WORD.search(text):
        errors.append(f"{where}: contains NaN or inf; write 'undefined' with the reason")


def validate_chapter_static(project, number, module):
    """Checks that need no rendering. Returns (errors, notes)."""
    errors, notes = [], []
    chapter = module.CHAPTER
    b = project.budgets
    for field in REQUIRED_CHAPTER_FIELDS:
        if not chapter.get(field):
            errors.append(f"CHAPTER.{field} is missing or empty")
    if errors:
        return errors, notes
    if chapter["number"] != number:
        errors.append(f"CHAPTER.number is {chapter['number']}, module file says {number}")
    demos = chapter["demos"]
    if len(demos) != b["demos_per_chapter"]:
        errors.append(f"CHAPTER has {len(demos)} demonstrations; exactly {b['demos_per_chapter']} are required")
    for path, text in iter_strings({k: v for k, v in chapter.items() if k != "demos"}):
        check_text(project, path, text, errors)

    text_path, note = project.canonical_text(number)
    notes.append("canonical text: " + (str(text_path) if text_path else note))
    source = text_path.read_text(encoding="utf-8") if text_path else ""
    headings = text_headings(source) if source else []
    allowed = {normalize_tex(t) for t in text_equations(source)} if source else set()
    allowed |= {normalize_tex(e["tex"]) for e in project.chapters.get(number, {}).get("equations", [])}
    allowed.discard("")

    ids = set()
    for i, demo in enumerate(demos, 1):
        did = demo.get("id", f"demo {i}")
        where = f"{did}"
        expected = f"C{number:02d}-D{i:02d}"
        if demo.get("id") != expected:
            errors.append(f"{where}: id must be {expected}")
        if did in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(did)
        for field in REQUIRED_DEMO_FIELDS:
            if not demo.get(field):
                errors.append(f"{where}: field '{field}' is missing or empty")
        for path, text in iter_strings({k: v for k, v in demo.items() if k not in ("function", "equations", "controls")}, did):
            check_text(project, path, text, errors)
        for c_i, control in enumerate(demo.get("controls", [])):
            for path, text in iter_strings({k: v for k, v in control.items() if k in ("label", "value_labels")}, f"{did}.controls[{c_i}]"):
                check_text(project, path, text, errors)
        if project.provenance_word and project.provenance_word.lower() not in str(demo.get("provenance", "")).lower():
            errors.append(f"{where}: provenance must say '{project.provenance_word}'")
        if not str(demo.get("answer", "")).strip() or not str(demo.get("check", "")).strip().endswith("?"):
            errors.append(f"{where}: check must be a question ending in '?' and answer must be present")
        fn = demo.get("function")
        if not isinstance(fn, str) or not callable(getattr(module, fn or "", None)):
            errors.append(f"{where}: function '{fn}' is not a callable defined in the module")
        for eq in demo.get("equations", []):
            if not isinstance(eq, str) or normalize_tex(eq) not in allowed:
                errors.append(f"{where}: equation not found in the chapter text or chapter list: {eq!r}")
        section = clean_heading(str(demo.get("source_section", "")))
        if demo.get("source_anchor") and demo.get("source_anchor") != slugify(section):
            errors.append(f"{where}: source_anchor must be '{slugify(section)}' (slug of source_section)")
        if source and section not in headings:
            errors.append(f"{where}: source_section '{section}' is not a heading in {text_path.name}")
        controls = demo.get("controls", [])
        if not 1 <= len(controls) <= 3:
            errors.append(f"{where}: use one to three controls")
        keys = set()
        product = 1
        for control in controls:
            key = control.get("key", "")
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", key or ""):
                errors.append(f"{where}: control key {key!r} must be a lowercase Python identifier")
            if key in keys:
                errors.append(f"{where}: duplicate control key {key}")
            keys.add(key)
            values = control.get("values", [])
            if not control.get("label"):
                errors.append(f"{where}: control {key} needs a label")
            if not b["min_values_per_control"] <= len(values) <= b["max_values_per_control"]:
                errors.append(f"{where}: control {key} has {len(values)} values; use {b['min_values_per_control']} to {b['max_values_per_control']}")
            if any(isinstance(v, bool) or not isinstance(v, (int, float, str)) for v in values):
                errors.append(f"{where}: control {key} values must be int, float or str")
            if len({repr(v) for v in values}) != len(values):
                errors.append(f"{where}: control {key} has repeated values")
            if control.get("default") not in values:
                errors.append(f"{where}: control {key} default {control.get('default')!r} is not among its values")
            labels = control.get("value_labels")
            if labels is not None and len(labels) != len(values):
                errors.append(f"{where}: control {key} value_labels must match values")
            product *= max(len(values), 1)
        if product > b["max_states_per_demo"]:
            errors.append(f"{where}: {product} control combinations; at most {b['max_states_per_demo']} are allowed")
        if fn and callable(getattr(module, fn or "", None)):
            import inspect
            params = inspect.signature(getattr(module, fn)).parameters
            for key in keys:
                if key not in params:
                    errors.append(f"{where}: function {fn} has no parameter '{key}'")
    return errors, notes


def apply_style(project):
    import matplotlib
    import matplotlib.pyplot as plt
    from cycler import cycler

    style = {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial", "Liberation Sans"],
        "font.size": 11.5, "axes.titlesize": 12, "axes.labelsize": 11.5,
        "xtick.labelsize": 10.5, "ytick.labelsize": 10.5, "legend.fontsize": 10.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#6b757b", "axes.labelcolor": "#172a3b", "text.color": "#172a3b",
        "xtick.color": "#4a565e", "ytick.color": "#4a565e",
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "grid.alpha": 0.2, "lines.linewidth": 2.2, "axes.unicode_minus": False,
        "svg.fonttype": "none", "svg.hashsalt": "illustrated-reader", "svg.id": None,
        "path.simplify": True,
    }
    style.update(project.style.get("rcparams", {}))
    for key in [k for k in style if k not in matplotlib.rcParams]:
        style.pop(key)
    plt.rcdefaults()
    plt.rcParams.update(style)
    colors = project.style.get("colors", ["#136f75", "#8f5d0f", "#334c72", "#a24a33", "#5d6a37"])
    plt.rcParams["axes.prop_cycle"] = cycler(color=colors)


def inspect_figure(fig, project, where):
    import numpy as np
    from matplotlib.patches import Rectangle
    from matplotlib.text import Text

    errors = []
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for a_i, ax in enumerate(fig.axes):
        if not ax.get_visible() or not ax.axison or ax.get_label() == "<colorbar>":
            continue
        if not ax.get_xlabel().strip():
            errors.append(f"{where}: axes {a_i} has no x-axis label")
        if not ax.get_ylabel().strip():
            errors.append(f"{where}: axes {a_i} has no y-axis label")
        for line in ax.get_lines():
            data = np.asarray(line.get_xydata(), dtype=float)
            if data.size and not np.all(np.isfinite(data)):
                errors.append(f"{where}: a plotted line contains NaN or inf; omit undefined points and say so")
        for coll in ax.collections:
            offsets = np.ma.asarray(coll.get_offsets())
            if offsets.size and not np.all(np.isfinite(np.ma.filled(offsets.astype(float), 0.0))):
                errors.append(f"{where}: a scatter or collection contains NaN or inf")
        for patch in ax.patches:
            if isinstance(patch, Rectangle):
                vals = [patch.get_x(), patch.get_y(), patch.get_width(), patch.get_height()]
                if not all(math.isfinite(float(v)) for v in vals):
                    errors.append(f"{where}: a bar or rectangle has a NaN or inf size")
        for image in ax.images:
            arr = np.ma.asarray(image.get_array())
            if arr.size and not np.all(np.isfinite(np.ma.filled(arr.astype(float), 0.0))):
                errors.append(f"{where}: an image contains NaN or inf")
        boxes = []
        for t in ax.texts:
            if t.get_visible() and t.get_text().strip():
                boxes.append((t.get_text(), t.get_window_extent(renderer)))
        frame = ax.get_window_extent(renderer)
        for text, box in boxes:
            if box.x0 < frame.x0 - 2 or box.x1 > frame.x1 + 2 or box.y0 < frame.y0 - 2 or box.y1 > frame.y1 + 2:
                errors.append(f"{where}: label {text!r} extends outside the plotting area")
        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            boxes.append(("legend", legend.get_window_extent(renderer)))
        for (ta, ba), (tb, bb) in itertools.combinations(boxes, 2):
            if ba.overlaps(bb):
                inter_w = min(ba.x1, bb.x1) - max(ba.x0, bb.x0)
                inter_h = min(ba.y1, bb.y1) - max(ba.y0, bb.y0)
                if inter_w > 1.5 and inter_h > 1.5:
                    errors.append(f"{where}: labels overlap: {ta!r} and {tb!r}")
    min_font = project.budgets["min_font_points"]
    for t in fig.findobj(Text):
        text = t.get_text()
        if not t.get_visible() or not text.strip():
            continue
        if t.get_fontsize() < min_font:
            errors.append(f"{where}: text {text!r} is {t.get_fontsize():.1f} pt; minimum is {min_font} pt")
        for problem in dash_problems(text):
            errors.append(f"{where}: figure text {text!r} contains {problem}")
    return errors


def figure_svg(fig):
    buffer = io.StringIO()
    fig.savefig(buffer, format="svg", bbox_inches="tight", pad_inches=0.12,
                metadata={"Date": None, "Creator": None, "Format": None, "Type": None})
    return clean_svg(buffer.getvalue())


def state_key(indices):
    return ",".join(str(i) for i in indices)


def control_display(control, index):
    labels = control.get("value_labels")
    if labels:
        return str(labels[index])
    return display_value(control["values"][index])


def render_demo(project, module, demo, errors):
    """Render every state. Returns dict key -> state, or None after errors."""
    import matplotlib.pyplot as plt

    controls = demo["controls"]
    states = {}
    fn = getattr(module, demo["function"])
    for indices in itertools.product(*(range(len(c["values"])) for c in controls)):
        params = {c["key"]: c["values"][i] for c, i in zip(controls, indices)}
        selected = ", ".join(f"{c['label']}: {control_display(c, i)}" for c, i in zip(controls, indices))
        where = f"{demo['id']} [{selected}]"
        apply_style(project)
        try:
            result = fn(**params)
        except Exception as exc:  # report every failing state
            errors.append(f"{where}: figure function raised {type(exc).__name__}: {exc}")
            plt.close("all")
            continue
        if not (isinstance(result, tuple) and len(result) == 3):
            errors.append(f"{where}: function must return (figure, metrics, interpretation)")
            plt.close("all")
            continue
        fig, metrics, interpretation = result
        if not hasattr(fig, "savefig") or not isinstance(metrics, dict) or not metrics or not isinstance(interpretation, str) or not interpretation.strip():
            errors.append(f"{where}: return (matplotlib Figure, non-empty dict, non-empty str)")
            plt.close("all")
            continue
        errors.extend(inspect_figure(fig, project, where))
        svg = figure_svg(fig)
        plt.close("all")
        shown = []
        for label, value in metrics.items():
            try:
                text = display_value(value)
            except ContractError as exc:
                errors.append(f"{where}: metric {label!r}: {exc}")
                continue
            check_text(project, f"{where} metric {label!r}", f"{label} {text}", errors, computed=True)
            shown.append([str(label), text])
        check_text(project, f"{where} interpretation", interpretation, errors, computed=True)
        if not (HAND_CALC.search(interpretation) or any(HAND_CALC.search(v) for _, v in shown)):
            errors.append(f"{where}: no hand-sized calculation (for example '0.85 x 100 + 0.15 x 0 = 85.0') in the interpretation or metrics")
        alt = f"Figure: {demo['title']}. {interpretation.strip()}"
        states[state_key(indices)] = {
            "image": svg_data_uri(svg), "alt": alt, "metrics": shown,
            "interpretation": interpretation.strip(), "selected": selected,
        }
    return states


def equation_blocks(project, number, demo):
    """Pre-rendered SVG for equations with a known asset, else TeX source for local MathJax."""
    known = {normalize_tex(e["tex"]): e for e in project.chapters.get(number, {}).get("equations", [])}
    blocks = []
    for tex in demo["equations"]:
        entry = known.get(normalize_tex(tex))
        if entry and entry["asset"] and entry["asset"].is_file():
            svg = clean_svg(entry["asset"].read_text(encoding="utf-8"))
            match = re.search(r'height="([\d.]+)ex"', svg)
            height = round(float(match.group(1)) * 0.55, 2) if match else 1.6
            blocks.append({"kind": "svg", "src": svg_data_uri(svg), "tex": tex, "height": height})
        else:
            blocks.append({"kind": "tex", "tex": tex})
    return blocks


def build_chapter(project, number, check_only=False):
    """Validate and render one chapter. Returns (html or None, report)."""
    report = {"chapter": number, "errors": [], "notes": []}
    if number not in project.chapters:
        report["errors"].append(f"chapter {number} is not in the configured chapter list")
        return None, report
    try:
        module = load_module(project, number)
    except ContractError as exc:
        report["errors"].append(str(exc))
        return None, report
    except Exception as exc:
        report["errors"].append(f"module failed to import: {type(exc).__name__}: {exc}")
        return None, report
    try:
        errors, notes = validate_chapter_static(project, number, module)
    except ContractError as exc:
        errors, notes = [str(exc)], []
    report["errors"] += errors
    report["notes"] += notes
    if errors:
        return None, report
    chapter = module.CHAPTER
    demos = []
    for demo in chapter["demos"]:
        states = render_demo(project, module, demo, report["errors"])
        defaults = state_key(c["values"].index(c["default"]) for c in demo["controls"])
        view = [{"key": c["key"], "label": c["label"], "options": [
            {"index": i, "text": control_display(c, i), "selected": c["values"][i] == c["default"]}
            for i in range(len(c["values"]))]} for c in demo["controls"]]
        demos.append({**demo, "states": states, "default_key": defaults, "controls_view": view,
                      "default_state": states.get(defaults), "equation_blocks": equation_blocks(project, number, demo)})
    if report["errors"]:
        return None, report
    links, link_notes = project.link_targets(number)
    report["notes"] += link_notes
    page = render_page(project, number, chapter, demos, links)
    size = len(page.encode("utf-8"))
    report["bytes"] = size
    report["states"] = sum(len(d["states"]) for d in demos)
    check_text_page(project, page, report["errors"])
    if size > project.budgets["max_reader_bytes"]:
        report["errors"].append(f"reader is {size} bytes; budget is {project.budgets['max_reader_bytes']}")
    return (None if report["errors"] else page), report


def jinja_env():
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    return Environment(loader=FileSystemLoader(ENGINE / "templates"), autoescape=select_autoescape(["j2", "html"]),
                       trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)


def render_page(project, number, chapter, demos, links):
    payload = {"engine": ENGINE_VERSION, "chapter": number, "demos": [
        {"id": d["id"], "title": d["title"],
         "controls": [{"key": c["key"], "label": c["label"], "default": c["values"].index(c["default"]),
                       "values": [control_display(c, i) for i in range(len(c["values"]))]} for c in d["controls"]],
         "states": d["states"]} for d in demos]}
    payload_text = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True)
    payload_text = payload_text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    needs_mathjax = any(b["kind"] == "tex" for d in demos for b in d["equation_blocks"])
    entry = project.chapters[number]
    return jinja_env().get_template("chapter.html.j2").render(
        b=project.branding, chapter=chapter, entry=entry, demos=demos, links=links,
        payload=payload_text, css=(ENGINE / "static/reader.css").read_text(encoding="utf-8"),
        javascript=(ENGINE / "static/reader.js").read_text(encoding="utf-8"),
        mathjax=project.math.get("mathjax_script") if needs_mathjax else None,
        index_href=project.links.get("index", {}).get("href", "../index.html"), engine_version=ENGINE_VERSION)


def visible_text(page):
    body = re.sub(r"<script\b.*?</script>", " ", page, flags=re.S)
    body = re.sub(r"<style\b.*?</style>", " ", body, flags=re.S)
    body = re.sub(r"<noscript\b.*?</noscript>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return html.unescape(body)


def check_text_page(project, page, errors):
    text = visible_text(page)
    for problem in dash_problems(text):
        errors.append(f"rendered page text contains {problem}")
    lower = text.lower()
    for term in project.forbidden_terms:
        if re.search(r"(?<![a-z])" + re.escape(term.lower()) + r"(?![a-z])", lower):
            errors.append(f"rendered page mentions the software dependency '{term}'")
    if re.search(r"(?:src|href)=\"(?:https?:)?//", page):
        errors.append("rendered page loads or links a network resource; readers must work offline")


def render_index(project, built):
    entries = []
    for number, chapter in project.chapters.items():
        reader = project.out_dir / chapter["slug"] / "reader.html"
        available = number in built or (reader.is_file() and project.module_path(number).is_file())
        entries.append({"number": number, "title": chapter["title"], "href": f"{chapter['slug']}/reader.html" if available else None})
    page = jinja_env().get_template("index.html.j2").render(
        b=project.branding, entries=entries, available=sum(1 for e in entries if e["href"]),
        css=(ENGINE / "static/reader.css").read_text(encoding="utf-8"), engine_version=ENGINE_VERSION)
    return page


def parse_chapters(project, values):
    if not values or values == ["all"]:
        return project.authored_numbers()
    numbers = []
    for v in values:
        for part in str(v).split(","):
            if part.strip():
                numbers.append(int(part))
    return numbers


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate chapter modules and build offline illustrated readers.")
    parser.add_argument("--config", required=True, help="Path to the project's reader.config.json")
    parser.add_argument("--chapters", nargs="*", default=["all"], help="Chapter numbers, or 'all' for every authored module")
    parser.add_argument("--check", action="store_true", help="Validate and render in memory; write nothing")
    parser.add_argument("--out", help="Output directory (default: output_dir from the configuration)")
    args = parser.parse_args(argv)
    require_dependencies()
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "illustrated-reader-mpl"))
    import matplotlib
    matplotlib.use("Agg")
    project = Project(args.config)
    if args.out:
        project.out_dir = Path(args.out).resolve()
    numbers = parse_chapters(project, args.chapters)
    if not numbers:
        print("No authored chapter modules found in " + str(project.modules_dir))
    failed, built, reports = False, [], []
    for number in numbers:
        page, report = build_chapter(project, number, check_only=args.check)
        reports.append(report)
        status = "ok" if not report["errors"] else "FAILED"
        size = f", {report['bytes'] / 1000:.0f} KB, {report['states']} states" if "bytes" in report else ""
        print(f"Chapter {number}: {status}{size}")
        for note in report["notes"]:
            print("  note: " + note)
        for error in report["errors"]:
            print("  error: " + error)
        if report["errors"]:
            failed = True
            continue
        if not args.check:
            target = project.out_dir / project.chapters[number]["slug"] / "reader.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page, encoding="utf-8")
            built.append(number)
    if not args.check:
        project.out_dir.mkdir(parents=True, exist_ok=True)
        (project.out_dir / "index.html").write_text(render_index(project, built), encoding="utf-8")
        total = sum(p.stat().st_size for p in project.out_dir.rglob("*") if p.is_file())
        print(f"Reader set: {total / 1e6:.2f} MB in {project.out_dir}")
        if total > project.budgets["max_total_bytes"]:
            print(f"  error: reader set exceeds {project.budgets['max_total_bytes']} bytes")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
