"""Run a local chapter, find a method, or inspect a composed workflow."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from .core import analyze, report_text, available_chapters, chapter_content
from .routing import suggest, workflow


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Calculate a chapter example or analyze supplied JSON.")
    run.add_argument("--chapter", type=int, required=True)
    run.add_argument("--case", choices=["example", "changed", "transfer"], default="example")
    run.add_argument("--input", type=Path)
    run.add_argument("--output", type=Path)
    run.add_argument("--figure", type=Path)
    run.add_argument("--text", action="store_true")
    route = sub.add_parser("route", help="Suggest chapters; semantic review remains the assistant's job.")
    route.add_argument("request")
    flow = sub.add_parser("workflow")
    flow.add_argument("name")
    flow.add_argument("--input", type=Path)
    flow.add_argument("--output", type=Path)
    cap = sub.add_parser("capstone", help="Run the integrated fictitious document-release controller.")
    cap.add_argument("--input", type=Path)
    cap.add_argument("--output", type=Path)
    demo = sub.add_parser('demo', help='Run a matching web/notebook demonstration.')
    demo.add_argument('--chapter', type=int, required=True)
    demo.add_argument('--id', required=True)
    demo.add_argument('--input', type=Path, help='Complete declared controls as JSON.')
    demo.add_argument('--output', type=Path)
    demo.add_argument('--figure', type=Path)
    demo.add_argument('--text', action='store_true')
    catalog = sub.add_parser('demo-list', help='List chapter demonstrations and declared controls.')
    catalog.add_argument('--chapter', type=int, required=True)
    sub.add_parser("list")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            data = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
            report = analyze(args.chapter, data, args.case)
            if args.figure:
                from .plotting import save_figure
                save_figure(report, args.figure)
            output = report_text(report) if args.text else json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
        elif args.command == "route":
            output = json.dumps(suggest(args.request), indent=2)
        elif args.command == "workflow":
            data = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
            output = json.dumps(workflow(args.name, data), indent=2, ensure_ascii=False, allow_nan=False)
        elif args.command == "capstone":
            from .capstone import simulate
            data = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
            output = json.dumps(simulate(data), indent=2, ensure_ascii=False, allow_nan=False)
        elif args.command == 'demo':
            from .demos import run_demo, demo_report_text
            controls = json.loads(args.input.read_text(encoding='utf-8')) if args.input else None
            report = run_demo(args.chapter, args.id, controls, include_figure=bool(args.figure))
            if args.figure:
                args.figure.parent.mkdir(parents=True, exist_ok=True)
                args.figure.write_text(report.pop('figure_svg'), encoding='utf-8')
            output = demo_report_text(report) if args.text else json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
        elif args.command == 'demo-list':
            from .demos import demo_catalog
            output = json.dumps([{'id': d['id'], 'title': d['title'], 'controls': d['controls']}
                                 for d in demo_catalog(args.chapter)], indent=2, ensure_ascii=False)
        else:
            output = "\n".join(f"{n:02d}  {chapter_content(n)['slug']}" for n in available_chapters())
        target = getattr(args, "output", None)
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Cannot complete calculation: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
