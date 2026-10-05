#!/usr/bin/env python3
"""Illustrated reader engine: validate chapter modules and build offline readers.

Each chapter module defines CHAPTER with four demonstrations. For every
combination of a demonstration's discrete controls the engine calls the
figure function, checks the result, stores the figure as a cleaned SVG and
embeds every state in one self-contained HTML page. A short script swaps the
precomputed state when a reader changes a control. Reading needs no network
and no Python.

Usage (the engine folder is scripts/readers in Book Forge, or any copy of it)
  python3 build_readers.py --config reader.config.json --chapters 6 --check
  python3 build_readers.py --config reader.config.json --chapters all
  python3 build_readers.py --config reader.config.json --chapters 1 2 --out /tmp/readers
  python3 build_readers.py --version

--check runs every figure function for every state and validates the
contract, but writes nothing. Without --check, readers and the index are
written to the configured output directory (or --out).

Look and structure are separate. The engine's own stylesheet
(static/reader.css) is a neutral base; a project may add its own look with
theme_css (a stylesheet, path relative to the configuration file) whose text is
inlined after the base style in every chapter page and the index page. With
"pager": true each chapter page ends with previous and next chapter links.

With "web": true (engine 1.5.0) the build is for a public website: pages
leave out the download-package wording (offline, precomputed, calculated in
advance), the "Ask the chapter skill" callout, the generator meta tag, the
engine version in the embedded data, demonstration IDs in source lines and
unbuilt chapters on the index, and links may point to https addresses (for
example a notebook on GitHub). Without it the output is unchanged.

ENGINE_VERSION is printed by --version and written into every reader page and
the index as <meta name="generator" content="illustrated reader engine X.Y.Z">,
so a project can tell which engine built a reader. Change it whenever a change
to this folder can change the bytes of a built reader.
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
ENGINE_VERSION = "1.5.1"
DEPENDENCIES = ("numpy", "matplotlib", "jinja2")
sys.dont_write_bytecode = True

REQUIRED_CHAPTER_FIELDS = ("number", "title", "subtitle", "summary", "demos")
REQUIRED_DEMO_FIELDS = (
    "id", "title", "question", "equations", "symbols", "prediction", "explanation",
    "application", "assumptions", "check", "answer", "provenance", "source_section",
    "source_anchor", "controls", "function",
)
OPTIONAL_CHAPTER_FIELDS = ("ask_skill",)
OPTIONAL_DEMO_FIELDS = (
    "misconception", "scope_note", "prediction_options", "prediction_answer", "prediction_feedback", "stepper",
    "evidence_kind",
)
DEFAULT_BUDGETS = {
    "demos_per_chapter": 4,
    "max_states_per_demo": 12,
    "min_values_per_control": 2,
    "max_values_per_control": 4,
    "max_reader_bytes": 4_000_000,
    "max_total_bytes": 55_000_000,
    "min_font_points": 9.5,
    "min_prediction_options": 2,
    "max_prediction_options": 4,
    "min_steps": 2,
    "max_steps": 8,
    "max_step_chars": 240,
    "min_scope_phrase_words": 4,
    "min_rendered_text_px": 9,
    "min_equation_scale": 0.6,
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


def clean_svg(raw, round_numbers=True):
    """Drop prolog, comments and metadata, round coordinates, collapse whitespace.

    round_numbers=False keeps every number exactly: typeset glyphs are scaled
    by small factors such as scale(0.015625), which two-decimal rounding would
    distort into overlapping letters.
    """
    s = re.sub(r"<\?xml[^>]*\?>", "", raw)
    s = re.sub(r"<!DOCTYPE[^>]*>", "", s)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)

    def rounded(m):
        text = f"{float(m.group(0)):.2f}".rstrip("0").rstrip(".")
        return "0" if text in ("-0", "") else text

    # Round numbers inside tags only (coordinates, path data); never touch text content.
    if round_numbers:
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
        self.theme_path, self.theme_css = load_theme(self.config_path, self.cfg.get("theme_css"))
        self.pager = self.cfg.get("pager", False)
        if not isinstance(self.pager, bool):
            raise SystemExit("Configuration pager must be true or false")
        self.web = self.cfg.get("web", False)
        if not isinstance(self.web, bool):
            raise SystemExit("Configuration web must be true or false")
        self.chapters = self._load_chapters()
        self.chapter_demo_counts = self._load_demo_counts(self.cfg.get("chapter_demo_counts", {}))

    def _load_demo_counts(self, raw):
        """Optional per-chapter demonstration counts, {"3": 3, "7": 5}; other chapters use the budget."""
        if not isinstance(raw, dict):
            raise SystemExit("Configuration chapter_demo_counts must map chapter numbers to counts")
        counts = {}
        for key, value in raw.items():
            if not isinstance(key, str) or not key.isdigit():
                raise SystemExit(f"Configuration chapter_demo_counts key '{key}' must be a chapter number string")
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise SystemExit(f"Configuration chapter_demo_counts['{key}'] must be a positive integer")
            if int(key) not in self.chapters:
                raise SystemExit(f"Configuration chapter_demo_counts names chapter {key}, which is not in the chapter list")
            counts[int(key)] = value
        return counts

    def demos_expected(self, number):
        """Demonstrations a chapter must carry: its chapter_demo_counts entry, else budgets.demos_per_chapter."""
        return self.chapter_demo_counts.get(number, self.budgets["demos_per_chapter"])

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
        skill_key = spec.get("fields", {}).get("skill", "skill")
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
                    label = None if isinstance(eq, str) else eq.get(eq_spec.get("number", "number"))
                    spoken = None if isinstance(eq, str) else eq.get(eq_spec.get("alt", "alt"))
                    equations.append({"tex": tex, "asset": self.path(asset) if asset else None,
                                      "number": str(label) if label is not None else None,
                                      "alt": spoken if isinstance(spoken, str) and spoken.strip() else None})
            skill = raw.get(skill_key)
            chapters[number] = {"number": number, "title": raw[fields["title"]], "slug": slug, "raw": raw, "equations": equations,
                                "skill": str(skill) if isinstance(skill, (str, int)) and str(skill).strip() else None}
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

    def pager_links(self, number):
        """Previous and next authored chapters in chapter list order, or None when the pager is off."""
        if not self.pager:
            return None
        order = self.authored_numbers()
        if number not in order:
            return None
        k = order.index(number)

        def link(n):
            c = self.chapters[n]
            return {"number": n, "title": c["title"], "href": f"../{c['slug']}/reader.html"}

        view = {"prev": link(order[k - 1]) if k > 0 else None, "next": link(order[k + 1]) if k + 1 < len(order) else None}
        return view if view["prev"] or view["next"] else None

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
            remote = self.web and re.match(r"https://", href)
            if not remote and spec.get("require_target", True) and not target.exists():
                notes.append(f"{key} link omitted: target {target} not found")
                continue
            out.append((key, spec.get("label", key.title()), href))
        return out, notes


# Section: theme

THEME_COMMENT = re.compile(r"/\*.*?\*/", re.S)
THEME_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I | re.S)


def theme_problems(css):
    """Reasons a theme stylesheet cannot be inlined into an offline reader (empty list when it can)."""
    problems = []
    if re.search(r"</style", css, re.I):
        problems.append("contains '</style', which would end the inlined style element")
    body = THEME_COMMENT.sub(" ", css)
    if re.search(r"@import", body, re.I):
        problems.append("uses @import; a theme must be one self-contained stylesheet")
    for m in THEME_URL.finditer(body):
        if not m.group(2).strip().lower().startswith("data:"):
            problems.append(f"loads url({m.group(2).strip()[:60]}); only data: URIs are allowed, readers work offline")
    rest = THEME_URL.sub(" ", body)
    if re.search(r"(?:https?:|ftp:)?//[a-z0-9.-]+\.[a-z]{2,}", rest, re.I):
        problems.append("names a network address; readers work offline")
    return problems


def load_theme(config_path, value):
    """Return (path, css text) for the optional theme_css setting, or (None, None)."""
    if value in (None, ""):
        return None, None
    if not isinstance(value, str):
        raise SystemExit("Configuration theme_css must be a path (relative to the configuration file) to a .css file")
    path = Path(value)
    path = path if path.is_absolute() else (Path(config_path).parent / path).resolve()
    if not path.is_file():
        raise SystemExit(f"Theme stylesheet not found (theme_css): {path}")
    css = path.read_text(encoding="utf-8")
    problems = theme_problems(css)
    if problems:
        raise SystemExit(f"Theme stylesheet {path} cannot be used: " + "; ".join(problems))
    return path, css


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
    expected_demos = project.demos_expected(number)
    if len(demos) != expected_demos:
        errors.append(f"CHAPTER has {len(demos)} demonstrations; exactly {expected_demos} are required")
    for path, text in iter_strings({k: v for k, v in chapter.items() if k != "demos"}):
        check_text(project, path, text, errors)
    for key in sorted(set(chapter) - set(REQUIRED_CHAPTER_FIELDS) - set(OPTIONAL_CHAPTER_FIELDS)):
        errors.append(f"CHAPTER has an unknown field '{key}'")
    validate_ask_skill(project, number, chapter, errors)

    text_path, note = project.canonical_text(number)
    notes.append("canonical text: " + (str(text_path) if text_path else note))
    source = text_path.read_text(encoding="utf-8") if text_path else ""
    headings = text_headings(source) if source else []
    allowed = {normalize_tex(t) for t in text_equations(source)} if source else set()
    allowed |= {normalize_tex(e["tex"]) for e in project.chapters.get(number, {}).get("equations", [])}
    allowed.discard("")
    for e_i, eq in enumerate(project.chapters.get(number, {}).get("equations", [])):
        if eq.get("alt"):
            check_text(project, f"chapter list equation {e_i + 1} alt", eq["alt"], errors)

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
        for key in sorted(set(demo) - set(REQUIRED_DEMO_FIELDS) - set(OPTIONAL_DEMO_FIELDS)):
            errors.append(f"{where}: unknown field '{key}'")
        validate_demo_options(project, demo, where, source, headings, text_path, errors)
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


def nonempty_str(value):
    return isinstance(value, str) and bool(value.strip())


def phrase_form(text):
    """Text compared for a phrase match: emphasis marks dropped, whitespace collapsed, lower case."""
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", html.unescape(text))).strip().lower()


def validate_ask_skill(project, number, chapter, errors):
    """Optional CHAPTER.ask_skill = {"prompt": str}; needs the chapter's skill name in the chapter list."""
    if "ask_skill" not in chapter:
        return
    ask = chapter["ask_skill"]
    if not isinstance(ask, dict) or set(ask) != {"prompt"} or not nonempty_str(ask.get("prompt")):
        errors.append('CHAPTER.ask_skill must be {"prompt": non-empty str} and nothing else')
    if not project.chapters.get(number, {}).get("skill"):
        errors.append("CHAPTER.ask_skill needs the chapter's skill name in the chapter list (field 'skill', "
                      "or the name given by chapter_list.fields.skill)")


def validate_demo_options(project, demo, where, source, headings, text_path, errors):
    """Optional demo fields: misconception, scope_note, prediction options and feedback, stepper."""
    b = project.budgets
    if "misconception" in demo:
        m = demo["misconception"]
        if not isinstance(m, dict) or set(m) != {"title", "text"} or not all(nonempty_str(m.get(k)) for k in ("title", "text")):
            errors.append(f'{where}: misconception must be {{"title": str, "text": str}}, both non-empty')
    if "scope_note" in demo:
        n = demo["scope_note"]
        if not isinstance(n, dict) or set(n) != {"text", "source_section"} or not all(nonempty_str(n.get(k)) for k in ("text", "source_section")):
            errors.append(f'{where}: scope_note must be {{"text": str, "source_section": str}}, both non-empty')
        elif not source:
            errors.append(f"{where}: scope_note needs the canonical chapter text to confirm its source_section; none is available")
        else:
            label = clean_heading(n["source_section"])
            words = len(phrase_form(label).split())
            if label not in headings:
                if words < b["min_scope_phrase_words"]:
                    errors.append(f"{where}: scope_note source_section '{label}' is not a heading in {text_path.name}, "
                                  f"and a phrase must have at least {b['min_scope_phrase_words']} words")
                elif phrase_form(label) not in phrase_form(source):
                    errors.append(f"{where}: scope_note source_section '{label}' is neither a heading nor a phrase in {text_path.name}")
    keys = ("prediction_options", "prediction_answer", "prediction_feedback")
    present = [k for k in keys if k in demo]
    if present and len(present) != len(keys):
        errors.append(f"{where}: prediction_options, prediction_answer and prediction_feedback go together; missing "
                      + ", ".join(k for k in keys if k not in demo))
    elif present:
        options, answer, feedback = (demo[k] for k in keys)
        lo, hi = b["min_prediction_options"], b["max_prediction_options"]
        if not isinstance(options, list) or not lo <= len(options) <= hi or not all(nonempty_str(o) for o in options):
            errors.append(f"{where}: prediction_options must be a list of {lo} to {hi} non-empty strings")
        elif len({o.strip() for o in options}) != len(options):
            errors.append(f"{where}: prediction_options repeat an option")
        elif isinstance(answer, bool) or not isinstance(answer, int) or not 0 <= answer < len(options):
            errors.append(f"{where}: prediction_answer must be the index (0 to {len(options) - 1}) of the correct option")
        if not isinstance(feedback, dict) or set(feedback) != {"correct", "incorrect"} or not all(nonempty_str(feedback.get(k)) for k in ("correct", "incorrect")):
            errors.append(f'{where}: prediction_feedback must be {{"correct": str, "incorrect": str}}, both non-empty')
    if "stepper" in demo:
        keys_here = [c.get("key") for c in demo.get("controls", []) if isinstance(c, dict)]
        if demo["stepper"] not in keys_here:
            errors.append(f"{where}: stepper must name one of the demonstration's control keys ({', '.join(map(str, keys_here))})")


def check_steps(project, where, steps, errors):
    """Optional per-state worked steps: 2 to 8 short strings."""
    b = project.budgets
    if not isinstance(steps, (list, tuple)) or not b["min_steps"] <= len(steps) <= b["max_steps"] or not all(nonempty_str(t) for t in steps):
        errors.append(f"{where}: steps must be a list of {b['min_steps']} to {b['max_steps']} non-empty strings")
        return None
    out = []
    for i, text in enumerate(steps, 1):
        text = text.strip()
        if len(text) > b["max_step_chars"]:
            errors.append(f"{where}: step {i} has {len(text)} characters; keep each step to {b['max_step_chars']}")
        check_text(project, f"{where} step {i}", text, errors, computed=True)
        out.append(text)
    return out


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


SVG_FONT_PX = re.compile(r"font(?:-size)?:[^;\"]*?([\d.]+)px")


def figure_min_width(svg, project):
    """Smallest CSS width (px) at which the figure's body text renders at min_rendered_text_px.

    The SVG viewBox is in points and its text sizes are in the same units, so
    text renders at size x (rendered width / viewBox width) CSS pixels. The
    body size is the smallest declared size at or above min_font_points
    (sub- and superscripts are smaller by design); the result never exceeds
    the drawing's natural width (viewBox width x 4/3 px).
    """
    box = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) [\d.]+"', svg)
    if not box:
        return None
    width = float(box.group(1))
    floor = float(project.budgets["min_font_points"])
    sizes = [float(x) for x in SVG_FONT_PX.findall(svg)]
    body = min([x for x in sizes if x >= floor - 1e-6] or [floor])
    target = float(project.budgets["min_rendered_text_px"])
    return int(math.ceil(min(width * target / body, width * 4 / 3)))


def state_key(indices):
    return ",".join(str(i) for i in indices)


def control_display(control, index):
    labels = control.get("value_labels")
    if labels:
        return str(labels[index])
    return display_value(control["values"][index])


def end_sentence(text):
    """Text with a closing period, unless it already ends in terminal punctuation (. ? !)."""
    text = str(text).rstrip()
    return text if text.endswith((".", "?", "!")) else text + "."


def state_alt(demo, interpretation, alt=None):
    """Alt text for one state's figure: the module's own alt when given, else the interpretation."""
    text = alt.strip() if isinstance(alt, str) and alt.strip() else interpretation.strip()
    return f"Figure: {end_sentence(demo['title'])} {text}"


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
        if not (isinstance(result, tuple) and len(result) in (3, 4)):
            errors.append(f"{where}: function must return (figure, metrics, interpretation) or (figure, metrics, interpretation, extra)"
                          " where extra is the alt text or a dict with 'alt' and/or 'steps'")
            plt.close("all")
            continue
        fig, metrics, interpretation = result[:3]
        given_alt = result[3] if len(result) == 4 else None
        given_steps = None
        if isinstance(given_alt, dict):
            extra = given_alt
            unknown = sorted(set(extra) - {"alt", "steps"})
            if unknown or not extra:
                errors.append(f"{where}: the optional fourth return value, when a dict, takes only 'alt' and 'steps' (got {', '.join(unknown) or 'nothing'})")
                plt.close("all")
                continue
            if "alt" in extra and not nonempty_str(extra["alt"]):
                errors.append(f"{where}: the fourth return value's 'alt' must be a non-empty str")
                plt.close("all")
                continue
            given_alt = extra.get("alt")
            if "steps" in extra:
                given_steps = check_steps(project, where, extra["steps"], errors)
                if given_steps is None:
                    plt.close("all")
                    continue
            result = result[:3] if given_alt is None else (*result[:3], given_alt)
        if not hasattr(fig, "savefig") or not isinstance(metrics, dict) or not metrics or not isinstance(interpretation, str) or not interpretation.strip():
            errors.append(f"{where}: return (matplotlib Figure, non-empty dict, non-empty str)")
            plt.close("all")
            continue
        if len(result) == 4 and not (isinstance(given_alt, str) and given_alt.strip()):
            errors.append(f"{where}: the optional fourth return value (alt text) must be a non-empty str")
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
        if given_alt is not None:
            check_text(project, f"{where} alt", given_alt, errors, computed=True)
        alt = state_alt(demo, interpretation, given_alt)
        states[state_key(indices)] = {
            "image": svg_data_uri(svg), "alt": alt, "metrics": shown,
            "interpretation": interpretation.strip(), "selected": selected,
        }
        min_width = figure_min_width(svg, project)
        if min_width:
            states[state_key(indices)]["min_width"] = min_width
        if given_steps is not None:
            states[state_key(indices)]["steps"] = given_steps
    with_steps = sum(1 for st in states.values() if "steps" in st)
    if with_steps and with_steps != len(states):
        errors.append(f"{demo['id']}: {with_steps} of {len(states)} states return steps; give steps for every state or for none")
    return states


def alt_tex(tex):
    """LaTeX shortened for alt text: no tag, spacing commands, delimiter sizing or repeated spaces."""
    t = re.sub(r"\\tag\*?\{[^{}]*\}", "", tex)
    t = re.sub(r"\\!", "", t)
    t = re.sub(r"\\(?:qquad|quad)(?![A-Za-z])|\\[,;:]", " ", t)
    t = re.sub(r"\\(?:left|right|[bB]igg?[lr]?)(?![A-Za-z])", "", t)
    return re.sub(r"\s+", " ", t).strip()


def equation_alt(tex, number=None, alt=None):
    """Readable alt text for an equation image: the chapter list's alt when given, else its LaTeX."""
    label = f"Equation ({number})" if number and re.fullmatch(r"[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*", str(number)) else "Equation"
    if isinstance(alt, str) and alt.strip():
        return f"{label}: {alt.strip()}"
    return f"{label}, written in LaTeX: {alt_tex(tex)}"


TEX_FONT_POINTS = 16
MATHTEXT_SUBSTITUTIONS = (
    (r"\\tag\*?\{[^{}]*\}", ""), (r"\\(?:left|right)(?![A-Za-z])", ""), (r"\\[bB]igg?[lr]?(?![A-Za-z])", ""),
    (r"\\le(?![A-Za-z])", r"\\leq"), (r"\\ge(?![A-Za-z])", r"\\geq"), (r"\\ne(?![A-Za-z])", r"\\neq"),
    (r"\\[dt]frac(?![A-Za-z])", r"\\frac"), (r"\\(?:text|textrm|mbox|mathrm)\{", r"\\mathrm{"),
    (r"\\operatorname\*", r"\\operatorname"), (r"\\[lr]vert(?![A-Za-z])", "|"), (r"\\!", ""),
)
PLAIN_SYMBOLS = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4", "epsilon": "\u03b5", "varepsilon": "\u03b5",
    "zeta": "\u03b6", "eta": "\u03b7", "theta": "\u03b8", "kappa": "\u03ba", "lambda": "\u03bb", "mu": "\u03bc",
    "nu": "\u03bd", "xi": "\u03be", "pi": "\u03c0", "rho": "\u03c1", "sigma": "\u03c3", "tau": "\u03c4",
    "phi": "\u03c6", "varphi": "\u03c6", "chi": "\u03c7", "psi": "\u03c8", "omega": "\u03c9",
    "Gamma": "\u0393", "Delta": "\u0394", "Theta": "\u0398", "Lambda": "\u039b", "Pi": "\u03a0", "Sigma": "\u03a3",
    "Phi": "\u03a6", "Psi": "\u03a8", "Omega": "\u03a9",
    "le": "\u2264", "leq": "\u2264", "ge": "\u2265", "geq": "\u2265", "ne": "\u2260", "neq": "\u2260",
    "times": "\u00d7", "cdot": "\u00b7", "approx": "\u2248", "in": "\u2208", "infty": "\u221e", "sum": "\u03a3",
    "prod": "\u03a0", "nabla": "\u2207", "mid": "|", "to": "\u2192", "rightarrow": "\u2192", "partial": "\u2202",
}


def tex_plain(tex):
    """A clean readable text form of a TeX string, for when it cannot be typeset."""
    t = alt_tex(tex)
    for _ in range(4):
        t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", t)
        t = re.sub(r"\\(?:mathrm|mathbf|mathit|mathcal|operatorname|text|textrm|hat|bar|tilde)\{([^{}]*)\}", r"\1", t)
        t = re.sub(r"([\^_])\{([^{}]*)\}", lambda m: m.group(1) + (m.group(2) if len(m.group(2)) == 1 else f"({m.group(2)})"), t)
    t = re.sub(r"\\([A-Za-z]+)", lambda m: PLAIN_SYMBOLS.get(m.group(1), m.group(1)), t)
    t = t.replace("{", "").replace("}", "").replace("\\", "")
    t = re.sub(r"\s*([=<>+\u2264\u2265\u2260\u00d7])\s*", r" \1 ", t)
    return re.sub(r"\s+", " ", t).strip()


TEXT_MODE_GROUP = re.compile(r"\\(?:text|textrm|mbox)\{([^{}]*)\}")
FRAC_ARGUMENT = r"(\{[^{}]*\}|[0-9A-Za-z])"
FRAC_SHORTHAND = re.compile(r"\\frac(?![A-Za-z])\s*" + FRAC_ARGUMENT + r"\s*" + FRAC_ARGUMENT)


def text_mode_spaces(match):
    """\\text{a b} -> \\mathrm{a\\ b}: mathtext drops spaces in text groups, explicit spaces survive."""
    body = match.group(1)
    if " " not in body:
        return match.group(0)
    return r"\mathrm{" + re.sub(r" +", lambda m: r"\ " * len(m.group(0)), body) + "}"


def frac_brace(argument):
    return argument if argument.startswith("{") else "{" + argument + "}"


def mathtext_source(tex):
    """TeX rewritten into the Matplotlib mathtext subset (typesetting only; matching uses the original)."""
    source = TEXT_MODE_GROUP.sub(text_mode_spaces, tex)
    for pattern, replacement in MATHTEXT_SUBSTITUTIONS:
        source = re.sub(pattern, replacement, source)
    for _ in range(4):  # \\frac12 shorthand -> \\frac{1}{2}; nested shorthand resolves over passes
        source, count = FRAC_SHORTHAND.subn(
            lambda m: r"\frac" + frac_brace(m.group(1)) + frac_brace(m.group(2)), source)
        if not count:
            break
    return source


def tex_svg(tex):
    """Typeset TeX as an SVG with glyphs drawn as paths (no fonts, no script, no network).

    Returns (svg, width_em, height_em), or None when the TeX is outside the
    supported subset or Matplotlib is not installed (a template-only render).
    One em is the equation's font size.
    """
    try:
        from matplotlib import rc_context
        from matplotlib.figure import Figure
        from matplotlib.mathtext import MathTextParser
    except ImportError:
        return None

    source = mathtext_source(tex)
    source = "$" + source.strip() + "$"
    try:
        MathTextParser("path").parse(source)
    except Exception:  # unsupported command: the caller falls back to plain text
        return None
    with rc_context({"svg.fonttype": "path", "mathtext.fontset": "cm", "svg.hashsalt": "illustrated-reader-equation",
                     "text.color": "#14202b", "path.simplify": True}):
        fig = Figure(figsize=(1, 1))
        fig.text(0, 0, source, fontsize=TEX_FONT_POINTS)
        buffer = io.StringIO()
        try:
            fig.savefig(buffer, format="svg", bbox_inches="tight", pad_inches=0.03, transparent=True,
                        metadata={"Date": None, "Creator": None, "Format": None, "Type": None})
        except Exception:
            return None
    svg = clean_svg(buffer.getvalue(), round_numbers=False)
    size = re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg)
    if not size:
        return None
    return svg, round(float(size.group(1)) / TEX_FONT_POINTS, 2), round(float(size.group(2)) / TEX_FONT_POINTS, 2)


def equation_blocks(project, number, demo):
    """Pre-rendered SVG for equations with a known asset, else an SVG typeset here, else readable text.

    Every block works with no script and no network. Images carry width and
    min_width in em: they shrink with the column down to min_equation_scale of
    their natural width, then the equation scrolls sideways.
    """
    known = {normalize_tex(e["tex"]): e for e in project.chapters.get(number, {}).get("equations", [])}
    scale = float(project.budgets["min_equation_scale"])
    blocks = []
    for tex in demo["equations"]:
        entry = known.get(normalize_tex(tex)) or {}
        alt = equation_alt(tex, entry.get("number"), entry.get("alt"))
        typeset = None
        if entry.get("asset") and entry["asset"].is_file():
            svg = clean_svg(entry["asset"].read_text(encoding="utf-8"))
            match = re.search(r'height="([\d.]+)ex"', svg)
            height = round(float(match.group(1)) * 0.55, 2) if match else 1.6
            match = re.search(r'width="([\d.]+)ex"', svg)
            width = round(float(match.group(1)) * 0.55, 2) if match else None
        else:
            typeset = tex_svg(tex)
            if typeset is None:
                blocks.append({"kind": "text", "tex": tex, "text": tex_plain(tex)})
                continue
            svg, width, height = typeset
        blocks.append({"kind": "svg", "src": svg_data_uri(svg), "tex": tex, "height": height, "width": width,
                       "min_width": round(width * scale, 2) if width else None, "alt": alt, "typeset": typeset is not None})
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
                      "default_state": states.get(defaults), "equation_blocks": equation_blocks(project, number, demo),
                      "stepper_view": stepper_view(demo)})
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


def stepper_status(control, index):
    """Status line for a Back/Next stepper; reader.js writes the same text."""
    return f"Step {index + 1} of {len(control['values'])}: {control['label']}: {control_display(control, index)}"


def stepper_view(demo):
    """Template data for the optional stepper, or None."""
    key = demo.get("stepper")
    control = next((c for c in demo.get("controls", []) if c.get("key") == key), None) if key else None
    if control is None:
        return None
    index = control["values"].index(control["default"])
    return {"key": key, "label": control["label"], "status": stepper_status(control, index),
            "at_start": index == 0, "at_end": index == len(control["values"]) - 1}


def jinja_env():
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    env = Environment(loader=FileSystemLoader(ENGINE / "templates"), autoescape=select_autoescape(["j2", "html"]),
                      trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    env.filters["end_sentence"] = end_sentence
    return env


def demo_payload(d):
    """One demonstration's script data. Optional features add keys only when the demonstration uses them."""
    entry = {"id": d["id"], "title": d["title"],
             "controls": [{"key": c["key"], "label": c["label"], "default": c["values"].index(c["default"]),
                           "values": [control_display(c, i) for i in range(len(c["values"]))]} for c in d["controls"]],
             "states": d["states"]}
    if d.get("evidence_kind"):
        entry["evidence_kind"] = d["evidence_kind"]
    if d.get("prediction_options"):
        entry["predict"] = {"answer": d["prediction_answer"], "correct": d["prediction_feedback"]["correct"].strip(),
                            "incorrect": d["prediction_feedback"]["incorrect"].strip()}
    if d.get("stepper"):
        entry["stepper"] = d["stepper"]
    return entry


def ask_skill_view(project, number, chapter, links):
    """Template data for the optional chapter-level 'Ask the chapter skill' callout, or None."""
    ask = chapter.get("ask_skill")
    if not ask:
        return None
    href = next((h for key, _label, h in links if key == "skill"), None)
    return {"prompt": ask["prompt"].strip(), "skill": project.chapters[number].get("skill"), "href": href}


WEB_MISSING_STATE = ("'This combination of values was not calculated in advance.'",
                     "'This combination of values is not available.'")


def render_page(project, number, chapter, demos, links):
    payload = {"engine": ENGINE_VERSION, "chapter": number, "demos": [demo_payload(d) for d in demos]}
    if project.web:
        del payload["engine"]
    payload_text = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True)
    payload_text = payload_text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    needs_mathjax = any(b["kind"] == "text" for d in demos for b in d["equation_blocks"])
    entry = project.chapters[number]
    return jinja_env().get_template("chapter.html.j2").render(
        b=project.branding, chapter=chapter, entry=entry, demos=demos, links=links,
        ask_skill=None if project.web else ask_skill_view(project, number, chapter, links), pager=project.pager_links(number),
        payload=payload_text, css=(ENGINE / "static/reader.css").read_text(encoding="utf-8"), theme_css=project.theme_css,
        javascript=reader_script(project), web=project.web,
        mathjax=project.math.get("mathjax_script") if needs_mathjax else None,
        index_href=project.links.get("index", {}).get("href", "../index.html"), engine_version=ENGINE_VERSION)


WEB_BANNED_WORDING = ("offline", "precomputed", "pre-computed", "calculated in advance", "no installation",
                      "launcher", "ask the chapter skill", "skill.md", ".ipynb", "illustrated reader engine")


def reader_script(project):
    script = (ENGINE / "static/reader.js").read_text(encoding="utf-8")
    return script.replace(*WEB_MISSING_STATE) if project.web else script


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
    if project.web:
        for term in WEB_BANNED_WORDING:
            if term in lower:
                errors.append(f"web page text contains download-package wording '{term}'")
    # A web build may link (never load) https pages, such as a notebook on GitHub.
    linked = r"href=\"(?:http:)?//" if project.web else r"href=\"(?:https?:)?//"
    if re.search(r"src=\"(?:https?:)?//", page) or re.search(linked, page):
        errors.append("rendered page loads or links a network resource; readers must work offline")


def render_index(project, built):
    entries = []
    for number, chapter in project.chapters.items():
        reader = project.out_dir / chapter["slug"] / "reader.html"
        available = number in built or (reader.is_file() and project.module_path(number).is_file())
        if project.web and not available:
            continue
        entries.append({"number": number, "title": chapter["title"], "href": f"{chapter['slug']}/reader.html" if available else None})
    page = jinja_env().get_template("index.html.j2").render(
        b=project.branding, entries=entries, available=sum(1 for e in entries if e["href"]),
        css=(ENGINE / "static/reader.css").read_text(encoding="utf-8"), theme_css=project.theme_css,
        engine_version=ENGINE_VERSION, web=project.web)
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
    parser.add_argument("--version", action="version", version=f"illustrated reader engine {ENGINE_VERSION}")
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
