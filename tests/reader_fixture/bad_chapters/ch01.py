"""Fixture chapter that breaks the contract on purpose (one violation per demonstration)."""
import math
import numpy as np
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
    return fig, {"Ratio": float("nan") if k == 2 else 1.0}, "The ratio is nan when k is two."


def fine_picture(k=1):
    fig, ax = new_figure()
    ax.plot([0, 1], [0, k])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig, {"Value": str(k)}, f"Value {k} x 2 = {2 * k}."


def base(i, **changes):
    d = {
        "id": f"C01-D0{i}", "title": "Bad", "question": "Bad?", "equations": ["y = a x + b"],
        "symbols": "s", "prediction": "p", "explanation": "e", "application": "a",
        "assumptions": "constructed", "check": "c?", "answer": "a", "provenance": "Constructed example.",
        "source_section": "A line has a slope", "source_anchor": "a-line-has-a-slope",
        "controls": [{"key": "k", "label": "k", "values": [1, 2], "default": 1}], "function": "fine_picture",
    }
    d.update(changes)
    return d


CHAPTER = {
    "number": 1, "title": "Straight Lines", "subtitle": "Broken on purpose \u2014 with an em dash.",
    "summary": "Bad.",
    "demos": [
        base(1, function="no_label_picture", equations=["y = m x + c"]),
        base(2, function="nan_picture", source_section="A heading that does not exist", source_anchor="a-heading-that-does-not-exist"),
        base(3, controls=[{"key": "k", "label": "k", "values": [1, 2, 3, 4, 5], "default": 9}]),
        base(4, provenance="Measured in production.", explanation="Install numpy " + "-" * 2 + " then run it."),
    ],
}
