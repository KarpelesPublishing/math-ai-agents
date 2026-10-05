"""Generate notebook sections from the same four demonstration definitions."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import pprint
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from math_ai_agents.demos import demo_catalog, demo_states, _engine


def equation_markdown(tex, equations):
    engine = _engine()
    known = next((entry for entry in equations if engine.normalize_tex(entry['tex']) == engine.normalize_tex(tex)), None)
    if known:
        return f"![Equation {known['number']}](../{known['asset']})"
    rendered = engine.tex_svg(tex)
    if rendered:
        target = ROOT / 'assets/demo-equations' / (hashlib.sha256(tex.encode()).hexdigest()[:20] + '.svg')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered[0])
        return f"![Mathematical relation](../{target.relative_to(ROOT)})"
    return engine.plain_tex(tex)


def sections(chapter, entry, markdown, code):
    cells = [markdown('## Explore the four chapter demonstrations\n\n'
                      'The following sections reproduce every demonstration in the illustrated chapter reader. '
                      'They use the same declared controls, calculation and figure. Begin with the prediction, '
                      'run the worked case, change one control, then inspect the complete state table. '
                      'The chapter experiment above remains available for your own compatible inputs.')]
    cells.append(code('from math_ai_agents.demos import demo_catalog, demo_states, run_demo, demo_report_text'))
    mappings = []
    answers = []
    for index, demo in enumerate(demo_catalog(chapter), 1):
        demo_id = demo['id']
        defaults = {control['key']: control['default'] for control in demo['controls']}
        equation_text = '\n\n'.join(equation_markdown(tex, entry['equations']) for tex in demo['equations'])
        domains = '\n'.join(f"- **{control['label']}:** `{control['key']}` accepts "
                            + ', '.join(repr(value) for value in control['values']) + '.' for control in demo['controls'])
        prose = (f'<a id="demo-{demo_id.lower()}"></a>\n\n### Demonstration {index}: {demo["title"]}\n\n'
                 f'{demo["question"]}\n\n{equation_text}\n\n**Symbols and units:** {demo["symbols"]}\n\n'
                 f'{demo["explanation"]}\n\n**Use in this chapter:** {demo["application"]}\n\n'
                 f'**Assumptions:** {demo["assumptions"]}\n\n**Predict before running:** {demo["prediction"]}\n\n'
                 f'**Controls you can change:**\n\n{domains}\n\n'
                 f'**Source section:** {demo["source_section"]}.\n\n'
                 f'**Evidence:** {demo.get("evidence_kind", "constructed teaching example")}.\n\n{demo["provenance"]}')
        if demo.get('prediction_options'):
            prose += '\n\nPrediction choices:\n\n' + '\n'.join(
                f'{i}. {option}' for i, option in enumerate(demo['prediction_options'], 1))
        if demo.get('scope_note'):
            prose += '\n\n**Boundary of the conclusion:** ' + demo['scope_note']['text']
        if demo.get('misconception'):
            prose += '\n\n**Common wrong turn:** ' + demo['misconception']['text']
        introductory = markdown(prose)
        introductory['metadata'].update({'maa_demo_id': demo_id, 'maa_demo_role': 'teaching'})
        cells.append(introductory)
        default_code = (f"demo_id = {demo_id!r}\ndemo_controls = {pprint.pformat(defaults, width=90, sort_dicts=False)}\n"
                        f"demo_result = run_demo({chapter}, demo_id, demo_controls)\n"
                        "print(demo_report_text(demo_result))\ndisplay(SVG(demo_result['figure_svg']))")
        executed = code(default_code)
        executed['metadata'].update({'maa_demo_id': demo_id, 'maa_demo_role': 'worked-state'})
        cells.append(executed)
        control = next(item for item in demo['controls'] if len(item['values']) > 1)
        changed = dict(defaults)
        changed[control['key']] = next(value for value in control['values'] if value != control['default'])
        cells.append(markdown(f'Change only **{control["label"]}** below. Predict which quantity and part of the figure should change. '
                              'Keep the other inputs fixed so the comparison has a clear meaning.'))
        changed_code = code(f"changed_controls = {pprint.pformat(changed, width=90, sort_dicts=False)}\n"
                            f"changed_demo = run_demo({chapter}, {demo_id!r}, changed_controls)\n"
                            "print(demo_report_text(changed_demo))\ndisplay(SVG(changed_demo['figure_svg']))")
        changed_code['metadata'].update({'maa_demo_id': demo_id, 'maa_demo_role': 'changed-state'})
        cells.append(changed_code)
        cells.append(markdown('The complete table below reruns every selectable state in the web demonstration. '
                              'Each row contains the controls and calculated quantities. It establishes coverage; '
                              'the separate analytical tests check whether those quantities are mathematically correct.'))
        state_code = code(f"state_rows = []\nfor controls in demo_states({chapter}, {demo_id!r}):\n"
                          f"    state = run_demo({chapter}, {demo_id!r}, controls, include_figure=False)\n"
                          "    state_rows.append({'controls': controls, 'metrics': state['metrics']})\n"
                          "print(json.dumps(state_rows, indent=2, ensure_ascii=False))")
        state_code['metadata'].update({'maa_demo_id': demo_id, 'maa_demo_role': 'all-states'})
        cells.append(state_code)
        cells.append(markdown(f'**Check your understanding:** {demo["check"]}\n\n'
                              f'[Answer and worked reasoning](../solutions/ch{chapter:02d}.md#demonstration-{index}). '
                              f'[Matching browser demonstration](../{entry["reader"]}#{demo_id}).'))
        mappings.append({'id': demo_id, 'title': demo['title'], 'notebook_anchor': 'demo-' + demo_id.lower(),
                         'source_section': demo['source_section'], 'source_anchor': demo['source_anchor'],
                         'equations': demo['equations'], 'controls': demo['controls'],
                         'function': demo['function'], 'states': len(list(demo_states(chapter, demo_id)))})
        answer = f'<a id="demonstration-{index}"></a>\n\n## Demonstration {index}\n\n{demo["check"]}\n\n{demo["answer"]}'
        if demo.get('prediction_options'):
            choice = demo['prediction_options'][demo['prediction_answer']]
            answer += (f'\n\n**Prediction answer:** {choice}.\n\n'
                       f'{demo["prediction_feedback"]["correct"]}\n\n'
                       f'**If you chose another answer:** {demo["prediction_feedback"]["incorrect"]}')
        answers.append(answer)
    return cells, mappings, '\n\n'.join(answers)
