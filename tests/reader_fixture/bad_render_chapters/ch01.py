"""Fixture chapter whose contract fields are valid but whose figures break the rules on purpose."""
from readerkit import new_figure


def no_label_picture(k=1):
    fig, ax = new_figure()
    ax.plot([0, 1], [0, k])
    ax.set_xlabel("x")
    return fig, {"Value": f"{k} x 2 = {2 * k}"}, f"Value is {k} x 2 = {2 * k}."


def nan_picture(k=1):
    fig, ax = new_figure()
    ax.plot([0, 1], [0, k])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ratio = float("nan") if k == 2 else 1.0
    return fig, {"Ratio": ratio}, f"Ratio check: {k} x 1 = {k}."


def raises_picture(k=1):
    if k == 2:
        raise ZeroDivisionError("division by zero")
    fig, ax = new_figure()
    ax.plot([0, 1], [0, k])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig, {"Value": str(k)}, f"Value {k} x 2 = {2 * k}."


def no_calc_picture(k=1):
    fig, ax = new_figure()
    ax.plot([0, 1], [0, k])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.text(0.5, 0.5, "first label", fontsize=11)
    ax.text(0.5, 0.5, "second label", fontsize=11)
    ax.text(0.1, 0.9, "tiny", fontsize=6)
    return fig, {"Value": str(k)}, "The value goes up."


def demo(i, fn):
    return {
        "id": f"C01-D0{i}", "title": "Render failure", "question": "Does it render?", "equations": ["y = a x + b"],
        "symbols": "k is a constructed number.", "prediction": "Guess.", "explanation": "Explained.",
        "application": "Applied.", "assumptions": "Constructed.", "check": "Why?", "answer": "Because.",
        "provenance": "Constructed example.", "source_section": "A line has a slope", "source_anchor": "a-line-has-a-slope",
        "controls": [{"key": "k", "label": "k", "values": [1, 2], "default": 1}], "function": fn,
    }


CHAPTER = {
    "number": 1, "title": "Straight Lines", "subtitle": "Rendering failures.", "summary": "Constructed failures.",
    "demos": [demo(1, "no_label_picture"), demo(2, "nan_picture"), demo(3, "raises_picture"), demo(4, "no_calc_picture")],
}
