"""Fixture chapter 2: area of a square, one control per demonstration."""
import numpy as np
from readerkit import new_figure, fmt


def area_picture(side=1):
    s = np.linspace(0, 4, 50)
    fig, ax = new_figure()
    ax.plot(s, s ** 2)
    ax.plot([side], [side ** 2], "o")
    ax.set_xlabel("Side s")
    ax.set_ylabel("Area A")
    return fig, {"Area": fmt(side ** 2, 1)}, f"A = {side} x {side} = {fmt(side ** 2, 1)}."


CHAPTER = {
    "number": 2, "title": "Squares", "subtitle": "Area grows with the square of the side.",
    "summary": "Constructed squares.",
    "demos": [{
        "id": f"C02-D0{i}", "title": f"Square {i}", "question": "How big is the square?",
        "equations": ["A = s^{2}"], "symbols": "s is the side and A the area.",
        "prediction": "Doubling the side multiplies the area by what?", "explanation": "Square the side.",
        "application": "Scale a drawing.", "assumptions": "Constructed squares.",
        "check": "What is the area of a side 3 square?", "answer": "9.",
        "provenance": "Constructed example.", "source_section": "The area of a square",
        "source_anchor": "the-area-of-a-square",
        "controls": [{"key": "side", "label": "Side", "values": [1, 2, 3, 4], "default": 2}],
        "function": "area_picture",
    } for i in range(1, 5)],
}
