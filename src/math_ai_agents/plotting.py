"""Restrained, labeled figures for chapter calculations."""
from __future__ import annotations

from io import StringIO
from pathlib import Path
import re


def figure_svg(report: dict) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    series = report["result"].get("series", [])
    if not series:
        raise ValueError("The chapter did not supply a plot series.")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.fonttype": "none"})
    figure, axes = plt.subplots(len(series), 1, figsize=(8, max(3.3, 2.9 * len(series))), squeeze=False)
    for axis, row in zip(axes.flat, series):
        x, y = row["x"], row["y"]
        if len(x) != len(y) or not x:
            raise ValueError("A figure series needs matching, nonempty x and y values.")
        axis.plot(x, y, color="#31586b", linewidth=1.8, marker="o" if len(x) <= 20 else None, markersize=4)
        labels = row.get("x_ticklabels")
        if labels is not None:
            if len(labels) != len(x):
                raise ValueError("x_ticklabels must match the x values.")
            axis.set_xticks(list(x))
            axis.set_xticklabels(labels)
        elif len(x) <= 20 and all(isinstance(v, int) and not isinstance(v, bool) for v in x):
            axis.set_xticks(list(x))  # integer positions only, never fractional ticks
        axis.set_xlabel(row.get("x_label", "Declared input"))
        axis.set_ylabel(row.get("y_label", "Calculated value"))
        axis.set_title(row["label"], loc="left", fontsize=11)
        axis.grid(axis="y", color="#d4d8da", linewidth=0.6)
    figure.suptitle(f"Chapter {report['chapter']}: {report['method'].replace('-', ' ')}", x=0.08, ha="left", fontsize=12)
    figure.tight_layout(rect=(0, 0, 1, 0.95))
    stream = StringIO()
    figure.savefig(stream, format="svg", metadata={"Date": None, "Creator": "Mathematics of AI Agents Laboratory"})
    plt.close(figure)
    svg = stream.getvalue()
    svg = re.sub(r"(<svg\b[^>]*>)", r'\1<title>Calculated chapter experiment</title><desc>Labeled plot of the explicitly supplied chapter inputs. See the adjacent explanation for assumptions.</desc>', svg, count=1)
    return svg


def save_figure(report: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(figure_svg(report), encoding="utf-8")
    return path
