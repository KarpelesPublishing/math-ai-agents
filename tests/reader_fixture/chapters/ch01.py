"""Fixture chapter 1: four small demonstrations of a straight line."""
import numpy as np
from readerkit import new_figure, fmt


def line_picture(slope=1, intercept=0):
    x = np.linspace(0, 4, 50)
    fig, ax = new_figure()
    ax.plot(x, slope * x + intercept)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    y2 = slope * 2 + intercept
    return fig, {"y at x = 2": fmt(y2, 1)}, f"At x = 2, y = {slope} x 2 + {intercept} = {fmt(y2, 1)}."


def meet_picture(slope=1, intercept=0):
    fig, ax = new_figure()
    x = np.linspace(0, 4, 50)
    ax.plot(x, slope * x + intercept)
    ax.plot(x, np.zeros_like(x) + 2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if slope == 0:
        meet = "undefined (parallel lines)"
        text = f"The lines y = 0 x + {intercept} and y = 2 are parallel, so 0 x 1 + {intercept} = {intercept} never changes and they do not meet."
    else:
        meet = fmt((2 - intercept) / slope, 2)
        text = f"They meet where {slope} x + {intercept} = 2, so x = (2 - {intercept}) / {slope} = {meet}."
    return fig, {"Meeting point x": meet}, text


def _demo(i, title, fn, section, equation, slopes):
    return {
        "id": f"C01-D0{i}", "title": title, "question": "Where does the line go?",
        "equations": [equation], "symbols": "a is the slope and b the intercept.",
        "prediction": "Guess the value at x = 2.", "explanation": "Multiply and add.",
        "application": "Read a rate of change.", "assumptions": "Exact arithmetic on a constructed line.",
        "check": "What is y at x = 0?", "answer": "The intercept b.",
        "provenance": "Constructed example.", "source_section": section,
        "source_anchor": section.lower().replace(" ", "-"),
        "controls": [{"key": "slope", "label": "Slope", "values": slopes, "default": slopes[1]},
                     {"key": "intercept", "label": "Intercept", "values": [0, 1], "default": 0}],
        "function": fn,
    }


CHAPTER = {
    "number": 1, "title": "Straight Lines", "subtitle": "Slope and intercept.",
    "summary": "Four constructed demonstrations of one line.",
    "demos": [
        _demo(1, "Slope", "line_picture", "A line has a slope", "y=ax+b", [0.5, 1, 2]),
        _demo(2, "Intercept", "line_picture", "A line has a slope", "y = a x + b", [1, 2]),
        _demo(3, "Meeting", "meet_picture", "Where two lines meet", "a_1 x + b_1 = a_2 x + b_2", [0, 1, 2]),
        _demo(4, "Meeting again", "meet_picture", "Where two lines meet", "a_1x+b_1=a_2x+b_2", [1, 3]),
    ],
}
