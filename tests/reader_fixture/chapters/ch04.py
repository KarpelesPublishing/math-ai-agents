"""Fixture chapter 4: a staircase. Exercises every optional reader field (engine 1.2.0).

Demonstration 1 has 12 states (4 x 3), a Back/Next stepper, worked steps per
state, a prediction with options and feedback, a misconception and a scope
note. Demonstration 2 has only the prediction fields, Demonstration 3 none of
the optional fields, Demonstration 4 worked steps without a stepper.
"""
from readerkit import new_figure, fmt


def _np():
    """numpy is imported only when a figure is drawn, so static tests can load this module without it."""
    import numpy
    return numpy


def stair_picture(steps=2, rise=15):
    fig, ax = new_figure()
    xs = _np().arange(steps + 1)
    ax.step(xs, xs * rise, where="post")
    ax.set_xlim(0, 4.5)
    ax.set_ylim(0, 90)
    ax.set_xlabel("Step number n")
    ax.set_ylabel("Height h (cm)")
    h = steps * rise
    interpretation = f"h = {steps} x {rise} = {h} cm."
    worked = [f"Rise per step r = {rise} cm.", f"Number of steps n = {steps}.", f"Height h = {steps} x {rise} = {h} cm."]
    return fig, {"Height h": f"{h} cm"}, interpretation, {"alt": f"A staircase of {steps} steps reaching {h} cm.", "steps": worked}


def plain_picture(steps=2):
    fig, ax = new_figure()
    xs = _np().arange(steps + 1)
    ax.step(xs, xs * 10, where="post")
    ax.set_xlim(0, 4.5)
    ax.set_ylim(0, 45)
    ax.set_xlabel("Step number n")
    ax.set_ylabel("Height h (cm)")
    return fig, {"Height h": fmt(steps * 10, 0)}, f"h = {steps} x 10 = {steps * 10} cm."


def steps_only_picture(steps=2):
    fig, ax = new_figure()
    xs = _np().arange(steps + 1)
    ax.step(xs, xs * 20, where="post")
    ax.set_xlim(0, 4.5)
    ax.set_ylim(0, 90)
    ax.set_xlabel("Step number n")
    ax.set_ylabel("Height h (cm)")
    return fig, {"Height h": fmt(steps * 20, 0)}, f"h = {steps} x 20 = {steps * 20} cm.", {
        "steps": [f"n = {steps} steps of 20 cm.", f"h = {steps} x 20 = {steps * 20} cm."]}


def _base(i, title, fn, section, controls):
    return {
        "id": f"C04-D0{i}", "title": title, "question": "How high does the staircase climb?",
        "equations": ["h = n r"], "symbols": "n is the number of steps, r the rise of one step in cm, h the height in cm.",
        "prediction": "Add one step of rise 15 cm. How much higher is the top?",
        "explanation": "Each step adds one rise, so the height is the number of steps times the rise.",
        "application": "Check a staircase drawing.", "assumptions": "Equal constructed steps.",
        "check": "What is the height of 5 steps of 12 cm?", "answer": "5 x 12 = 60 cm.",
        "provenance": "Constructed example.", "source_section": section,
        "source_anchor": section.lower().replace(" ", "-"),
        "controls": controls, "function": fn,
    }


PREDICTION = {
    "prediction_options": ["15 cm higher", "30 cm higher", "No higher"],
    "prediction_answer": 0,
    "prediction_feedback": {"correct": "One more step adds one rise: 15 cm.",
                            "incorrect": "One more step adds exactly one rise, 15 cm. Move the steps control to see it."},
}

DEMO1 = {
    **_base(1, "Climb", "stair_picture", "Height of a staircase",
            [{"key": "steps", "label": "Number of steps", "values": [1, 2, 3, 4], "default": 2},
             {"key": "rise", "label": "Rise per step (cm)", "values": [10, 15, 20], "default": 15}]),
    **PREDICTION,
    "stepper": "steps",
    "misconception": {"title": "Adding the rise only once",
                      "text": "The rise is added once per step, so four steps of 15 cm climb 4 x 15 = 60 cm, not 15 cm."},
    "scope_note": {"text": "Uneven steps need the sum of their rises; this demonstration assumes equal steps.",
                   "source_section": "What this chapter does not settle"},
}

CHAPTER = {
    "number": 4, "title": "Stairs", "subtitle": "Height is the number of steps times the rise.",
    "summary": "Four constructed staircases.",
    "ask_skill": {"prompt": "Explain why a staircase of n equal steps of rise r climbs n x r."},
    "demos": [
        DEMO1,
        {**_base(2, "Predict", "plain_picture", "Height of a staircase",
                 [{"key": "steps", "label": "Number of steps", "values": [1, 2, 3, 4], "default": 2}]), **PREDICTION},
        _base(3, "Plain", "plain_picture", "Walking the stairs one step at a time",
              [{"key": "steps", "label": "Number of steps", "values": [1, 2, 3, 4], "default": 2}]),
        _base(4, "Worked", "steps_only_picture", "Walking the stairs one step at a time",
              [{"key": "steps", "label": "Number of steps", "values": [1, 2, 3, 4], "default": 2}]),
    ],
}
