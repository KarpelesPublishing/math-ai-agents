"""Chapter 3 reader: How to Predict Emergence.

Four demonstrations built on Equations (3.1) to (3.3), Figure 3.2 and the chapter's constructed
forecast example. Demonstration 2 and Demonstration 4 call the laboratory's own
frozen-forecast function (math_ai_agents.chapters.ch03.evaluate), so the reader,
the notebook and the chapter skill agree. Demonstration 1 and Demonstration 3
compute their mathematics directly. Every number is a constructed teaching value;
Demonstration 2 uses the book's own worked numbers.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch03 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

EQ_LOSS = r"L(C)=aC^b+c"
EQ_SLOPE = r"[(1-2)(0.10-0.20)+(3-2)(0.29-0.20)]/2=0.095"
EQ_PASS = r"\operatorname{pass}_\tau(q_m)=\mathbf{1}\{q_m\geq\tau\}"
EQ_GAMMA = r"\Gamma_m=f_\psi(z_m)+\epsilon_m"


# Demonstration 1: Equation (3.1), forecasting a held-out loss

TRUE_A, TRUE_B, TRUE_C = 1.5, -0.15, 1.0   # constructed constants of the true curve
WIGGLE_PATTERN = np.array([1.0, -1.0, -1.0, 1.0, 1.0])
EXPONENT_GRID = -np.arange(10, 1001) / 1000.0  # -0.010 ... -1.000, step 0.001


def true_loss(log_c):
    return TRUE_A * 10.0 ** (TRUE_B * np.asarray(log_c, dtype=float)) + TRUE_C


def fit_loss_curve(log_c, loss):
    """Search the exponent b on a grid; at each b solve a and c by least squares. Keep the best b."""
    c = 10.0 ** np.asarray(log_c, dtype=float)
    best = None
    for b in EXPONENT_GRID:
        design = np.column_stack([c ** b, np.ones_like(c)])
        coef = np.linalg.lstsq(design, loss, rcond=None)[0]
        sse = float(np.sum((design @ coef - loss) ** 2))
        if best is None or sse < best[0] - 1e-15:
            best = (sse, float(b), float(coef[0]), float(coef[1]))
    _, b, a, c0 = best
    return round(a, 3), b, round(c0, 3)  # constants are reported to three decimals


SILENT_SHIFT = np.array([0.0, 0.0, 0.0, 0.10, 0.10])  # two largest runs trained differently, difference unrecorded


def perturbation(runs):
    if runs == "wiggle":
        return 0.04 * WIGGLE_PATTERN
    if runs == "silent":
        return SILENT_SHIFT
    return np.zeros(5)


def forecast_case(decades, runs):
    """Fit runs sit two decades wide, ending `decades` below the held-out run (compute 1)."""
    log_c = -decades - 2.0 + 0.5 * np.arange(5)
    loss = true_loss(log_c) + perturbation(runs)
    a, b, c0 = fit_loss_curve(log_c, loss)
    forecast = a + c0  # at C = 1 the power C^b equals 1 for every b
    observed = TRUE_A + TRUE_C
    in_sample = float(np.max(np.abs(a * 10.0 ** (b * log_c) + c0 - loss)))
    return {"log_c": log_c, "loss": loss, "a": a, "b": b, "c": c0, "forecast": forecast,
            "observed": observed, "residual": observed - forecast, "in_sample": in_sample}


def extrapolation_picture(decades=2, runs="exact"):
    decades = int(decades)
    case = forecast_case(decades, runs)
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    lo = -decades - 2.0
    grid = np.linspace(lo - 0.15, 0.25, 200)
    fitted = case["a"] * 10.0 ** (case["b"] * grid) + case["c"]
    inside = grid <= -decades
    left.axvspan(-decades, 0.55, facecolor=PALETTE["light"], alpha=0.35, hatch="//", edgecolor="white", linewidth=0)
    left.plot(grid, true_loss(grid), color=PALETTE["grey"], linestyle=":", linewidth=1.6, label="true curve")
    left.plot(grid[inside], fitted[inside], color=PALETTE["teal"], linewidth=2, label="fit")
    left.plot(grid[~inside], fitted[~inside], color=PALETTE["teal"], linewidth=2, linestyle="dashed", label="fit, extrapolated")
    left.plot(case["log_c"], case["loss"], "o", color=PALETTE["ink"], markersize=7)
    left.plot([0], [case["observed"]], "D", color=PALETTE["navy"], markersize=9)
    left.plot([0], [case["forecast"]], "s", color=PALETTE["gold"], markersize=8)
    top = float(np.max(case["loss"])) + 1.2
    bottom = case["observed"] - 1.6
    left.set_xlim(lo - 0.35, 0.55)
    left.set_ylim(bottom, top)
    label_point(left, case["log_c"][0], case["loss"][0], "measured runs", color=PALETTE["ink"], dx=8, dy=8, ha="left").set_bbox(BOX)
    label_point(left, -decades + 0.05, top - 0.15, "extrapolated", color=PALETTE["grey"], dx=0, dy=0, ha="left", va="top")
    if abs(case["residual"]) < 5e-4:
        label_point(left, 0, case["observed"], "forecast = observed", color=PALETTE["ink"], dx=-9, dy=12, ha="right").set_bbox(BOX)
    else:
        up, down = (("forecast", PALETTE["gold"]), ("observed later", PALETTE["navy"])) if case["forecast"] > case["observed"] else \
            (("observed later", PALETTE["navy"]), ("forecast", PALETTE["gold"]))
        y_up = max(case["forecast"], case["observed"])
        y_down = min(case["forecast"], case["observed"])
        label_point(left, 0, y_up, up[0], color=up[1], dx=-9, dy=10, ha="right").set_bbox(BOX)
        label_point(left, 0, y_down, down[0], color=down[1], dx=-9, dy=-12, ha="right", va="top").set_bbox(BOX)
    left.set_xlabel("Training compute as a power of ten (0 = held-out run)")
    left.set_ylabel("Loss (constructed units)")
    left.set_title("Fit on the left, forecast on the right", fontsize=11.5)
    left.legend(loc="lower left", fontsize=10.5, frameon=True, framealpha=0.9)

    cases = {d: forecast_case(d, runs) for d in (1, 2, 3, 4)}
    residuals = [cases[d]["residual"] for d in (1, 2, 3, 4)]
    reach = max(0.12, 1.45 * max(abs(r) for r in residuals))
    for d in (1, 2, 3, 4):
        chosen = d == decades
        right.bar(d, cases[d]["residual"], width=0.6, color=PALETTE["teal"] if chosen else "white",
                  edgecolor=PALETTE["teal"], linewidth=1.6, hatch="" if chosen else "//")
        r = cases[d]["residual"]
        label_point(right, d, r, fmt(r, 3), color=PALETTE["ink"], dx=0, dy=5 if r >= 0 else -5,
                    ha="center", va="bottom" if r >= 0 else "top")
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xticks([1, 2, 3, 4])
    right.set_xlim(0.4, 4.6)
    right.set_ylim(-reach, reach)
    right.set_xlabel("Decades from the largest fit run to the held-out run")
    right.set_ylabel("Residual, observed minus forecast")
    right.set_title("Solid bar is the state shown on the left", fontsize=11.5)

    metrics = {
        "Fitted a, b, c": f"{fmt(case['a'], 3)}, {fmt(case['b'], 3)}, {fmt(case['c'], 3)}",
        "Largest misfit inside the measured runs": fmt(case["in_sample"], 3),
        "Forecast at the held-out run": fmt(case["forecast"], 3),
        "Observed later (constructed true value)": fmt(case["observed"], 3),
        "Residual, observed minus forecast": fmt(case["residual"], 3),
    }
    if runs == "exact":
        reading = ("The measured losses lie exactly on the true curve, so the search recovers it and the forecast has no error "
                   "at any distance. Choose another set of runs to see distance start to matter.")
    elif runs == "wiggle":
        reading = (f"The fit follows the measured runs to within {fmt(case['in_sample'], 3)}, yet the forecast is off by "
                   f"{fmt(abs(case['residual']), 3)}. Across the four distances the miss grows for this wiggle pattern "
                   "(compare the bars on the right). The forecast is a + c, so the miss comes from the fitted constants: "
                   f"a and c trade off against the exponent b, and here a = {fmt(case['a'], 3)} and c = {fmt(case['c'], 3)} "
                   f"against the true {fmt(TRUE_A, 1)} and {fmt(TRUE_C, 1)}.")
    else:
        reading = (f"The two largest measured runs sit 0.10 above the true curve because they were trained differently and nobody "
                   f"recorded the difference. The fit absorbs that shift as if it were scale, so it still follows the measured runs "
                   f"to within {fmt(case['in_sample'], 3)} while the forecast is off by {fmt(abs(case['residual']), 3)}, "
                   f"with a = {fmt(case['a'], 3)} and c = {fmt(case['c'], 3)} against the true {fmt(TRUE_A, 1)} and {fmt(TRUE_C, 1)}. "
                   "A fit cannot correct for a condition nobody recorded.")
    interpretation = (
        f"At the held-out run C = 1, so C^b = 1 for any exponent b and the observed loss is a x 1 + c = "
        f"{fmt(TRUE_A, 1)} x 1 + {fmt(TRUE_C, 1)} = {fmt(case['observed'], 1)}. The forecast is the fitted a + c = "
        f"{fmt(case['a'], 3)} + {fmt(case['c'], 3)} = {fmt(case['forecast'], 3)}. Residual = {fmt(case['observed'], 3)} - "
        f"{fmt(case['forecast'], 3)} = {fmt(case['residual'], 3)}. {reading}"
    )
    worked = [
        f"Five measured runs at compute 10^{fmt(case['log_c'][0], 1)} to 10^{fmt(case['log_c'][-1], 1)}; the held-out run is at C = 1, {decades} powers of ten beyond the largest.",
        f"Search b from -1.000 to -0.010; solve a and c by least squares at each b and keep the best: a = {fmt(case['a'], 3)}, b = {fmt(case['b'], 3)}, c = {fmt(case['c'], 3)}.",
        f"At C = 1 the power C^b is 1, so the forecast = a + c = {fmt(case['a'], 3)} + {fmt(case['c'], 3)} = {fmt(case['forecast'], 3)}.",
        f"The constructed true value is {fmt(TRUE_A, 1)} + {fmt(TRUE_C, 1)} = {fmt(case['observed'], 1)}.",
        f"Residual = {fmt(case['observed'], 3)} - {fmt(case['forecast'], 3)} = {fmt(case['residual'], 3)}.",
    ]
    alt = (f"Left, a fitted loss curve through five measured runs, extended as a dashed line {decades} powers of ten to a held-out run where the "
           f"forecast is {fmt(case['forecast'], 3)} and the observed value {fmt(case['observed'], 3)}. Right, residual bars at 1, 2, 3 and 4 powers of ten.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 2: the commitment boundary, the registered interval and what changing the forecast afterwards does

DEV_X = [1.0, 2.0, 3.0]
DEV_Y = [0.10, 0.21, 0.29]
FORECAST_X = 4.0
DELTA = 0.02
PROTOCOL = [
    "Declare family and target",
    "Declare the controls",
    "Collect all four cells",
    "Compute contrasts, uncertainty",
    "Fit without the held-out run",
    "Register point and interval",
    "Measure the held-out run",
    "Compare, including misses",
]


def registered_forecast(observed):
    """Point forecast from the laboratory's frozen-forecast function, checked against the book's numbers."""
    out = evaluate({"development_x": DEV_X, "development_y": DEV_Y, "test_x": [FORECAST_X],
                    "test_y": [float(observed)], "family": "linear"})["metrics"]
    if not (math.isclose(out["slope"], 0.095, abs_tol=1e-12) and math.isclose(out["intercept"], 0.01, abs_tol=1e-12)
            and math.isclose(out["predictions"][0], 0.39, abs_tol=1e-12)):
        raise AssertionError("laboratory forecast disagrees with the chapter's worked example")
    return out["slope"], out["intercept"], out["predictions"][0]


def draw_protocol(ax, redone):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Figure 3.2: the commitment boundary", fontsize=11.5)
    ys = [0.94 - 0.092 * i for i in range(6)] + [0.28, 0.18]
    for i, (y, text) in enumerate(zip(ys, PROTOCOL)):
        before = i < 6
        flagged = redone is not None and i + 1 == redone
        color = PALETTE["terracotta"] if flagged else PALETTE["ink"]
        ax.text(0.0, y, f"{i + 1}", ha="left", va="center", fontsize=11.5, fontweight="bold", color=PALETTE["gold"] if before else PALETTE["navy"])
        ax.text(0.07, y, text + ("  (redone after step 7)" if flagged else ""), ha="left", va="center", fontsize=10.5,
                color=color, fontweight="bold" if flagged else "normal")
    ax.plot([0, 1], [0.39, 0.39], color=PALETTE["ink"], linestyle="dashed", linewidth=1.6)
    ax.text(1.0, 0.43, "committed before the answer exists", ha="right", va="center", fontsize=10.5, color=PALETTE["gold"])
    ax.text(1.0, 0.35, "possible only after it exists", ha="right", va="center", fontsize=10.5, color=PALETTE["navy"])


def commit_picture(observed=0.43, commitment="kept"):
    observed = float(observed)
    slope, intercept, forecast = registered_forecast(observed)
    xbar = sum(DEV_X) / len(DEV_X)
    sxx = sum((x - xbar) ** 2 for x in DEV_X)
    weights = [1 / len(DEV_X) + (FORECAST_X - xbar) * (x - xbar) / sxx for x in DEV_X]
    weight_total = sum(abs(w) for w in weights)
    inherited = weight_total * DELTA
    half = inherited + DELTA
    low, high = forecast - half, forecast + half
    residual = observed - forecast
    inside = low <= observed <= high
    # Refit after the fact through all four points (x = 1, 2, 3, 4 are equally spaced).
    y1, y2, y3 = DEV_Y
    slope4 = (-3 * y1 - y2 + y3 + 3 * observed) / 10
    mean4 = (y1 + y2 + y3 + observed) / 4
    fitted4 = mean4 + 1.5 * slope4
    residual4 = observed - fitted4
    post_half = abs(residual)
    redone = {"kept": None, "refit": 5, "posthoc": 6}[commitment]

    fig, (left, ax) = new_figure(ncols=2, height=4.6)
    draw_protocol(left, redone)
    xs = np.linspace(0.6, FORECAST_X, 50)
    ax.plot(xs, intercept + slope * xs, color=PALETTE["teal"], linewidth=2)
    ax.plot(DEV_X, DEV_Y, "o", color=PALETTE["ink"], markersize=8)
    ax.errorbar([FORECAST_X], [forecast], yerr=[[forecast - low], [high - forecast]], fmt="none", ecolor=PALETTE["gold"],
                elinewidth=2.2, capsize=8, capthick=2.2)
    ax.plot([FORECAST_X], [forecast], "s", color=PALETTE["gold"], markersize=9)
    if commitment == "refit":
        ax.plot(xs, mean4 + slope4 * (xs - 2.5), color=PALETTE["olive"], linestyle=":", linewidth=2)
        ax.plot([FORECAST_X], [fitted4], "o", color=PALETTE["olive"], markersize=8, markerfacecolor="white", markeredgewidth=2)
    if commitment == "posthoc":
        ax.errorbar([FORECAST_X + 0.18], [forecast], yerr=post_half, fmt="none", ecolor=PALETTE["terracotta"], elinewidth=2.0,
                    capsize=8, capthick=2.0, linestyle="dashed")
    if inside:
        ax.plot([FORECAST_X], [observed], "D", color=PALETTE["navy"], markersize=9)
    else:
        ax.plot([FORECAST_X], [observed], "X", color=PALETTE["terracotta"], markersize=11)
    ax.set_xlim(0.5, 7.6)
    ax.set_ylim(0.0, 0.62)
    label_point(ax, 1, 0.10, "development", color=PALETTE["ink"], dx=8, dy=-12, ha="left", va="top")
    items = [(observed, f"observed {fmt(observed, 2)}", PALETTE["navy"] if inside else PALETTE["terracotta"]),
             (forecast, f"registered forecast {fmt(forecast, 2)}", PALETTE["gold"])]
    if commitment == "refit":
        items.append((fitted4, f"refit {fmt(fitted4, 3)}", PALETTE["olive"]))
    if commitment == "posthoc":
        items.append((forecast + post_half, f"after the fact {fmt(forecast - post_half, 2)} to {fmt(forecast + post_half, 2)}", PALETTE["terracotta"]))
    items.sort()
    gap = 0.085 * 0.62
    placed = []
    for y, text, color in items:
        y_text = max(y, placed[-1][0] + gap) if placed else y
        placed.append((y_text, text, color, y))
    for y_text, text, color, y in placed:
        ax.plot([FORECAST_X + 0.3, FORECAST_X + 0.45], [y, y_text], color=color, linewidth=0.9)
        ax.annotate(text, (FORECAST_X + 0.5, y_text), xytext=(0, 0), textcoords="offset points", ha="left", va="center",
                    color=color, fontsize=10.5, bbox=BOX)
    ax.set_xlabel("Declared family coordinate x")
    ax.set_ylabel("Interaction contrast (constructed)")
    ax.set_title("Registered line, interval and the result", fontsize=11.5)

    metrics = {
        "Fitted slope and intercept": f"{fmt(slope, 3)}, {fmt(intercept, 2)}",
        "Registered point forecast at x = 4": fmt(forecast, 2),
        "Registered interval": f"{fmt(low, 6)} to {fmt(high, 6)}",
        "Observed at x = 4": fmt(observed, 2),
        "Residual against the registered forecast": fmt(residual, 2),
        "Inside the registered interval": "yes" if inside else "no",
    }
    if commitment == "refit":
        metrics["Refit forecast after the result"] = fmt(fitted4, 3)
        metrics["Residual against the refit"] = fmt(residual4, 3)
    if commitment == "posthoc":
        metrics["Interval written after the result"] = f"{fmt(forecast - post_half, 2)} to {fmt(forecast + post_half, 2)}"
        metrics["Contains the observed value"] = "yes, by construction"
    if inside:
        verdict = ("The observed value is inside the registered interval: one successful check of this declared forecast. It does not "
                   "prove the line or the error bound, and one hit does not show they will keep holding.")
    else:
        verdict = ("The observed value is outside the registered interval. Under the stipulated line and error bound that cannot happen, "
                   "so an assumption failed (the line, the bound, the family, or the measurement). The forecast stays "
                   "registered as made.")
    base = (
        f"Slope = [(1 - 2) x (0.10 - 0.20) + (3 - 2) x (0.29 - 0.20)] / 2 = 0.19 / 2 = {fmt(slope, 3)}, so the forecast at x = 4 "
        f"is {fmt(intercept, 2)} + {fmt(slope, 3)} x 4 = {fmt(forecast, 2)}. The weights (-2/3, 1/3, 4/3) add up in size to "
        f"2/3 + 1/3 + 4/3 = {fmt(weight_total, 4)}, so the inherited error is at most {fmt(weight_total, 4)} x {fmt(DELTA, 2)} = "
        f"{fmt(inherited, 6)}. Adding {fmt(DELTA, 2)} for the fourth observation gives {fmt(inherited, 6)} + {fmt(DELTA, 2)} = "
        f"{fmt(half, 6)}, so the interval runs from {fmt(low, 6)} to {fmt(high, 6)}. Residual = {fmt(observed, 2)} - "
        f"{fmt(forecast, 2)} = {fmt(residual, 2)}. {verdict}"
    )
    refit_calc = (f"slope = (-3 x {fmt(y1, 2)} - {fmt(y2, 2)} + {fmt(y3, 2)} + 3 x {fmt(observed, 2)}) / 10 = {fmt(slope4, 3)}; "
                  f"mean y = ({fmt(y1, 2)} + {fmt(y2, 2)} + {fmt(y3, 2)} + {fmt(observed, 2)}) / 4 = {fmt(mean4, 4)}; "
                  f"fitted value at x = 4 is {fmt(mean4, 4)} + 1.5 x {fmt(slope4, 3)} = {fmt(fitted4, 3)}")
    if commitment == "kept":
        extra = " The forecast and interval were fixed at step 6, before the result existed, so the comparison at step 8 is a test."
    elif commitment == "refit":
        extra = (f" Suppose the team now refits through all four points: {refit_calc}. The residual against the refit is "
                 f"{fmt(observed, 2)} - {fmt(fitted4, 3)} = {fmt(residual4, 3)}, smaller in size than the registered {fmt(residual, 2)}. "
                 "The refit always looks better because it was fitted to the result; it is a retrospective fit, not the registered forecast, "
                 "and nothing in the finished plot shows which happened.")
    else:
        extra = (f" Suppose the team now writes an interval after seeing the result: {fmt(forecast, 2)} +/- |{fmt(observed, 2)} - "
                 f"{fmt(forecast, 2)}| = {fmt(forecast, 2)} +/- {fmt(post_half, 2)}, from {fmt(forecast - post_half, 2)} to {fmt(forecast + post_half, 2)}. "
                 "It contains the observed value by construction, for any result, so it says nothing; the registered interval could have been missed.")
    interpretation = base + extra
    worked = [
        f"Fit a line to the three development points: slope {fmt(slope, 3)}, intercept {fmt(intercept, 2)}.",
        f"Forecast at x = 4: {fmt(intercept, 2)} + {fmt(slope, 3)} x 4 = {fmt(forecast, 2)}.",
        f"Interval half-width = ({fmt(weight_total, 4)} + 1) x {fmt(DELTA, 2)} = {fmt(half, 6)}, so {fmt(low, 6)} to {fmt(high, 6)}.",
        "Register the forecast and interval (step 6). Everything before the dashed line is committed.",
        f"Observed {fmt(observed, 2)}; residual = {fmt(observed, 2)} - {fmt(forecast, 2)} = {fmt(residual, 2)}; "
        + ("inside the registered interval." if inside else "outside the registered interval."),
    ]
    if commitment == "refit":
        worked.append(f"Refit after the result: fitted value at x = 4 is {fmt(mean4, 4)} + 1.5 x {fmt(slope4, 3)} = {fmt(fitted4, 3)}; "
                      f"residual {fmt(residual4, 3)}. Not a prediction.")
    elif commitment == "posthoc":
        worked.append(f"An interval written afterwards, {fmt(forecast, 2)} +/- {fmt(post_half, 2)}, covers {fmt(observed, 2)} by construction. Not a test.")
    alt = ("Left, the eight protocol steps with a dashed commitment boundary after step 6"
           + ("." if redone is None else f", with step {redone} marked as redone after step 7") +
           f". Right, a line fitted to three development points, the registered forecast {fmt(forecast, 2)} with its interval, and the observed value {fmt(observed, 2)} "
           + ("inside it." if inside else "outside it."))
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 3: Equation (3.3), smooth ability and an abrupt score

MEMBERS = np.arange(1, 10)  # nine members of a constructed family, in order of scale


def q_latent(m):
    return 0.05 + 0.03 * (np.asarray(m, dtype=float) - 1)


def q_linear(m):
    return 0.1 + 0.1 * (np.asarray(m, dtype=float) - 1)


def q_onset(m):
    return 1.0 / (1.0 + np.exp(-2.5 * (np.asarray(m, dtype=float) - 5)))


def q_flat(m):
    return np.full_like(np.asarray(m, dtype=float), 0.2)


PROFILES = {
    "latent": ("Latent progress below the threshold", q_latent, "q = 0.05 + 0.03 x (m - 1)"),
    "jump": ("Metric-created jump", q_linear, "q = 0.1 + 0.1 x (m - 1)"),
    "onset": ("Candidate capability onset", q_onset, "q = 1 / (1 + e^(-2.5 x (m - 5)))"),
    "none": ("No rise", q_flat, "q = 0.2"),
}


def passes(q, tau):
    return np.round(np.asarray(q, dtype=float), 9) >= tau


def q_text(profile, m):
    """The hand calculation of q at member m, written with that profile's formula."""
    value = float(PROFILES[profile][1](m))
    if profile == "latent":
        return f"q({m}) = 0.05 + 0.03 x {m - 1} = {fmt(value, 2)}"
    if profile == "jump":
        return f"q({m}) = 0.1 + 0.1 x {m - 1} = {fmt(value, 2)}"
    if profile == "onset":
        k = m - 5
        return (f"q({m}) = 1 / (1 + e^({fmt(-2.5 * k, 1)})) = 1 / (1 + {fmt(math.exp(-2.5 * k), 4)}) = {fmt(value, 3)}")
    return f"q({m}) = {fmt(value, 2)}"


def threshold_picture(profile="jump", tau=0.5):
    tau = float(tau)
    name, q_fn, _ = PROFILES[profile]
    q = q_fn(MEMBERS)
    verdict = passes(q, tau).astype(int)
    fine = np.linspace(1, 9, 161)
    first = int(MEMBERS[np.argmax(verdict)]) if verdict.any() else None
    steps_q = np.abs(np.diff(q))
    steps_v = np.abs(np.diff(verdict))

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(fine, q_fn(fine), color=PALETTE["teal"], linewidth=2)
    left.plot(MEMBERS, q, "o", color=PALETTE["teal"], markersize=6)
    left.axhline(tau, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    left.set_xlim(0.7, 9.3)
    left.set_ylim(-0.03, 1.08)
    label_point(left, 0.8, tau, f"threshold {fmt(tau, 2)}", color=PALETTE["grey"], dx=0, dy=5, ha="left", va="bottom").set_bbox(BOX)
    label_point(left, 0.8, 1.06, "q, graded", color=PALETTE["teal"], dx=0, dy=0, ha="left", va="top").set_bbox(BOX)
    left.set_xlabel("Family member m (increasing scale)")
    left.set_ylabel("Success probability q")
    left.set_title("The graded coordinate", fontsize=11.5)

    right.step(MEMBERS, verdict, where="post", color=PALETTE["navy"], linewidth=2)
    right.plot(MEMBERS, verdict, "s", color=PALETTE["navy"], markersize=7)
    right.set_xlim(0.7, 9.3)
    right.set_ylim(-0.15, 1.2)
    right.set_yticks([0, 1], ["0 (fail)", "1 (pass)"])
    if first is None:
        label_point(right, 5, 0.5, "never passes in this range", color=PALETTE["navy"], dx=0, dy=0, ha="center", va="center").set_bbox(BOX)
    else:
        label_point(right, first, 1, f"first pass at m = {first}", color=PALETTE["navy"], dx=-8, dy=-14,
                    ha="right" if first > 4 else "left", va="top").set_bbox(BOX)
    right.set_xlabel("Family member m (increasing scale)")
    right.set_ylabel("Reported verdict")
    right.set_title("The thresholded score", fontsize=11.5)

    metrics = {
        "Profile": name,
        "Threshold": fmt(tau, 2),
        "First member that passes": "none in this range" if first is None else f"m = {first}",
        "Largest one-step change in q": fmt(float(steps_q.max()), 3),
        "Largest one-step change in the verdict": fmt(float(steps_v.max()), 0),
    }
    if first is None:
        last = int(MEMBERS[-1])
        calc = (f"{q_text(profile, last)}, the highest in the range. Gap to the threshold = {fmt(float(q[-1]), 2)} - {fmt(tau, 2)} = "
                f"{signed(float(q[-1]) - tau, 2)}, which is negative, so the verdict is 0 at every member.")
        if profile == "latent":
            meaning = ("The model improves under the graded measure but never reaches the cutoff, so a forecast fitted to the "
                       "flat verdict would say nothing is predictable. The graded coordinate has the signal.")
        else:
            meaning = ("Neither coordinate rises. This is a result about this task, family and range, not a statement about "
                       "what is possible.")
    else:
        before = first - 1
        gap = float(q[first - 1] - q[before - 1]) if before >= 1 else 0.0
        calc = (f"{q_text(profile, before)} < {fmt(tau, 2)} gives 0, then {q_text(profile, first)} >= {fmt(tau, 2)} gives 1. "
                f"The score jumps by 1 while q changed by {fmt(q[first - 1], 3)} - {fmt(q[before - 1], 3)} = {fmt(gap, 3)}.")
        if profile == "jump":
            meaning = ("q rises by the same small step at every member, so the sudden event belongs mostly to the scoring rule, "
                       "not to the model. A fit to the verdict would project a step at a particular scale, which is a claim "
                       "about where the cutoff sits.")
        else:
            meaning = ("Here q itself rises sharply over the same members as the score. This is the case that deserves "
                       "mechanism tests, and even a sharp rise in measured behavior is not by itself proof of a phase transition.")
    interpretation = f"Equation (3.3) with threshold {fmt(tau, 2)}: {calc} {meaning}"
    if first is not None and abs(float(q[first - 1]) - tau) < 1e-9:
        interpretation += " The passing member reaches the threshold exactly, and Equation (3.3) counts that as a pass because it uses at least."
    if first is None:
        worked = [f"{q_text(profile, int(MEMBERS[-1]))}, the highest q in the range.",
                  f"Compare with the threshold {fmt(tau, 2)}: {fmt(float(q[-1]), 2)} < {fmt(tau, 2)}, so the verdict is 0.",
                  "The same holds at every smaller member, so the verdict never changes."]
    else:
        worked = [f"{q_text(profile, before)}, below the threshold {fmt(tau, 2)}: verdict 0.",
                  f"{q_text(profile, first)}, at least the threshold {fmt(tau, 2)}: verdict 1.",
                  f"The verdict jumps by 1; q changed by {fmt(float(q[first - 1]) - float(q[before - 1]), 3)} between the two members.",
                  f"Largest one-step change in q over the range: {fmt(float(steps_q.max()), 3)}."]
    alt = ("Left, the smooth success probability q over nine family members with a dashed threshold. Right, the pass or fail verdict, "
           + ("which never passes." if first is None else f"which first passes at member {first}."))
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 4: Equation (3.2), declaring the family before the outcomes are seen

DATASETS = {
    "default": {"dx": [1.0, 2.0, 3.0], "dy": [0.2, 0.3, 0.4], "tx": [4.0, 5.0],
                "outcomes": {"extended": [0.5, 0.6], "faster": [0.8, 0.95], "flattening": [0.45, 0.48]}},
    "transfer": {"dx": [1.0, 2.0, 4.0], "dy": [0.0, 0.69314718056, 1.38629436112], "tx": [8.0, 16.0],
                 "outcomes": {"extended": [2.07944154168, 2.77258872224], "faster": [2.5, 3.5], "flattening": [1.8, 2.0]}},
}
OUTCOME_LABELS = {"extended": "As the data continued", "faster": "Faster than that", "flattening": "Flattening off"}


def frozen(family, data, test_y):
    d = DATASETS[data]
    return evaluate({"development_x": d["dx"], "development_y": d["dy"], "test_x": d["tx"], "test_y": list(test_y),
                     "family": family})["metrics"]


def curve(family, out, xs):
    f = np.log if family == "log" else (lambda v: v)
    return out["intercept"] + out["slope"] * f(xs)


def fx(x):
    return fmt(x, 4) if abs(x - round(x)) > 1e-9 else str(int(round(x)))


def family_picture(data="default", family="linear", outcome="faster"):
    d = DATASETS[data]
    dx, dy, tx = d["dx"], d["dy"], d["tx"]
    test_y = d["outcomes"][outcome]
    other = "log" if family == "linear" else "linear"
    out = frozen(family, data, test_y)
    alt = frozen(other, data, test_y)
    forecast = out["predictions"]
    residuals = [o - p for o, p in zip(test_y, forecast)]  # observed minus forecast, as in the chapter
    bias = sum(residuals) / len(residuals)
    rmse = out["test_rmse"]
    best = family if rmse <= alt["test_rmse"] + 1e-9 else other
    xs = np.linspace(1, tx[-1], 160)
    span = tx[-1] - 0.7
    x_text = tx[-1] + 0.08 * span

    fig, ax = new_figure(height=4.3)
    ax.plot(xs, curve(other, alt, xs), color=PALETTE["grey"], linestyle=":", linewidth=1.8)
    ax.plot(xs, curve(family, out, xs), color=PALETTE["teal"], linewidth=2)
    ax.plot(dx, dy, "o", color=PALETTE["ink"], markersize=8)
    for x, p, o in zip(tx, forecast, test_y):
        ax.plot([x, x], [p, o], color=PALETTE["gold"], linewidth=2.2)
    ax.plot(tx, forecast, "s", color=PALETTE["gold"], markersize=9)
    ax.plot(tx, test_y, "D", color=PALETTE["navy"], markersize=8)
    other_end = float(curve(other, alt, np.array([tx[-1]]))[0])
    lo = 0.1 if data == "default" else -0.9
    top = max(max(test_y), max(forecast), other_end, 0.6 if data == "default" else 3.0) + (0.14 if data == "default" else 0.45)
    ax.set_xlim(0.7, tx[-1] + 0.53 * span)
    ax.set_ylim(lo, top)
    label_point(ax, dx[0], dy[0], "development", color=PALETTE["ink"], dx=6, dy=-12, ha="left", va="top")
    if abs(test_y[1] - forecast[1]) < 0.05 * (top - lo) / 0.7:
        items = [((test_y[1] + forecast[1]) / 2, "forecast = observed", PALETTE["ink"])]
    else:
        items = [(test_y[1], "observed", PALETTE["navy"]), (forecast[1], "frozen forecast", PALETTE["gold"])]
    items.append((other_end, f"{other} family", PALETTE["grey"]))
    items.sort()
    gap = 0.107 * (top - lo)
    placed = []
    for y, text, color in items:
        y_text = max(y, placed[-1][0] + gap) if placed else y
        placed.append((y_text, text, color, y))
    for y_text, text, color, y in placed:
        ax.plot([tx[-1] + 0.018 * span, tx[-1] + 0.07 * span], [y, y_text], color=color, linewidth=0.9)
        ax.annotate(text, (x_text, y_text), xytext=(0, 0), textcoords="offset points", ha="left", va="center", color=color,
                    fontsize=10.5, bbox=BOX)
    ax.set_xlabel("Declared scale x")
    ax.set_ylabel("Score (constructed)")
    ax.set_title(f"Declared family: {family}. Forecast frozen before the outcomes", fontsize=11.5)

    t0, t1 = fx(tx[0]), fx(tx[1])
    od = 2 if data == "default" else 4  # observed values are printed to four decimals on the log-shaped data
    metrics = {
        "Declared family": family,
        "Fitted slope and intercept": f"{fmt(out['slope'], 4)}, {fmt(out['intercept'], 4)}",
        f"Frozen forecast at {t0} and {t1}": f"{fmt(forecast[0], 3)}, {fmt(forecast[1], 3)}",
        f"Observed at {t0} and {t1}": f"{fmt(test_y[0], od)}, {fmt(test_y[1], od)}",
        "Residuals, observed minus forecast": f"{fmt(residuals[0], 3)}, {fmt(residuals[1], 3)}",
        "Test RMSE": fmt(rmse, 3),
        "Mean residual (bias)": fmt(bias, 3),
        f"RMSE of the {other} family, which was not declared": fmt(alt["test_rmse"], 3),
        "Family that fits best after the fact": best,
    }
    if family == "log":
        f4 = (f"{fmt(out['slope'], 4)} x ln({t0}) + {signed(out['intercept'], 4)} = {fmt(out['slope'], 4)} x {fmt(math.log(tx[0]), 4)} + "
              f"{signed(out['intercept'], 4)}")
    else:
        f4 = f"{fmt(out['slope'], 4)} x {t0} + {signed(out['intercept'], 4)}"
    calc = (f"Forecast at x = {t0} is {f4} = {fmt(forecast[0], 3)}. Residual at {t0} = {fmt(test_y[0], od)} - {fmt(forecast[0], 3)} = "
            f"{fmt(residuals[0], 3)}; at {t1} = {fmt(test_y[1], od)} - {fmt(forecast[1], 3)} = {fmt(residuals[1], 3)}. RMSE = "
            f"sqrt(({signed(residuals[0], 3)} x {signed(residuals[0], 3)} + {signed(residuals[1], 3)} x {signed(residuals[1], 3)}) / 2) = {fmt(rmse, 3)}.")
    if best == family:
        lesson = (f"The declared {family} family is also the better fit, so this time declaring it first cost nothing. "
                  "It would still not have been a prospective result had the family been picked after the outcomes.")
    else:
        lesson = (f"The {other} family would have fitted better (RMSE {fmt(alt['test_rmse'], 3)}). Switching to it now would make the "
                  "graph look better but would be a retrospective fit, not the registered forecast, which keeps its "
                  f"RMSE of {fmt(rmse, 3)}.")
    interpretation = f"{calc} {lesson}"
    dev_pairs = ", ".join(f"({fx(x)}, {fmt(y, 2) if data == 'default' else fmt(y, 4)})" for x, y in zip(dx, dy))
    worked = [
        f"Development points {dev_pairs}; the family is declared before any outcome: {family}.",
        f"Least squares on the development points: slope {fmt(out['slope'], 4)}, intercept {fmt(out['intercept'], 4)}.",
        f"Frozen forecasts: at {t0} = {fmt(forecast[0], 3)}; at {t1} = {fmt(forecast[1], 3)}.",
        f"Residuals, observed minus forecast: {fmt(residuals[0], 3)} and {fmt(residuals[1], 3)}.",
        f"RMSE = {fmt(rmse, 3)}; the {other} family would score {fmt(alt['test_rmse'], 3)}, which cannot change the registered forecast.",
    ]
    alt_text = (f"A {family} line fitted to three development points and extended to scales {t0} and {t1}, with the frozen forecast, the observed "
                f"outcome and the undeclared {other} curve; RMSE {fmt(rmse, 3)}.")
    return fig, metrics, interpretation, {"alt": alt_text, "steps": worked}




CHAPTER = {
    "number": 3,
    "title": "How to Predict Emergence",
    "subtitle": "A forecast counts as a prediction only if it was recorded before the result it describes, with an interval that can be missed.",
    "summary": (
        "These four demonstrations follow the chapter's forecasting contract. First, how far an extrapolated loss curve can be "
        "trusted and what an unrecorded difference between runs does to it. Second, the commitment boundary of the eight-step protocol "
        "with the chapter's own registered forecast and interval. Third, how a graded success probability becomes an abrupt score. "
        "Fourth, why the family must be declared before the outcomes are seen."
    ),
    "ask_skill": {
        "prompt": ("Fit a linear family to development scales 1, 2, 3 with scores 0.2, 0.3, 0.4 and forecast scales 4 and 5. Then score the "
                   "frozen forecast against outcomes 0.8 and 0.95 and report the RMSE and bias. Would refitting after seeing them repair the forecast?"),
    },
    "demos": [
        {
            "id": "C03-D01",
            "title": "Fit small runs, forecast a run that is not there yet",
            "question": "If a curve of the form in Equation (3.1) is fitted to small runs, how does the miss on a much larger run depend on how far away it is and on whether the runs share a recipe?",
            "equations": [EQ_LOSS],
            "symbols": (
                "L is loss, a graded measure of surprise, and C is training compute, scaled so the held-out run has C = 1. "
                "The constants a, b and c are fitted: b is negative, so loss falls as compute grows, and c is the level "
                "loss levels off at. The constructed true curve has a = 1.5, b = -0.15 and c = 1.0. Five measured runs "
                "span two powers of ten of compute; the first control sets how many powers of ten lie between the largest of "
                "them and the held-out run. The second control sets what the measured runs contain: exact values on the curve, a small "
                "wiggle, or a shift of 0.10 in the two largest runs that were trained differently in a way nobody recorded. The residual is observed minus forecast."
            ),
            "prediction": "With the wiggle of 0.04 (the default), set the distance to 4 powers of ten. Is the miss bigger or smaller than at 1 power of ten?",
            "prediction_options": ["Bigger at 4 powers of ten", "Smaller at 4 powers of ten", "The same at every distance"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "For this constructed wiggle the bars on the right grow with distance: the fitted a and c trade off against b, and the forecast a + c drifts.",
                "incorrect": "Choose the wiggle and compare the residual at 1 and at 4 powers of ten (the bars on the right): the miss grows with distance.",
            },
            "explanation": (
                "The exponent b is searched over a grid, and at each b the constants a and c are found by least squares; the "
                "best b is kept. With exact measurements the true curve is recovered. With a small wiggle the fit still "
                "looks good inside the measured range, but the fitted a and c trade off against the exponent b, so the "
                "forecast a + c at C = 1 shifts, and for this constructed pattern the shift grows with distance. An unrecorded difference between "
                "members is absorbed as if it were scale, which is why the family has to be documented before it is fitted."
            ),
            "application": (
                "When a team reports that a fitted curve predicted a bigger run, ask how far the held-out run sat from the "
                "largest run used in the fit, whether the runs really belong to one documented family, and whether the forecast was recorded first. "
                "A small miss across one power of ten and the same miss across four are different achievements."
            ),
            "assumptions": (
                "The true curve has exactly the form in Equation (3.1), which is assumed here and is not guaranteed for any "
                "real family; the book calls the relation measured, not derived. The wiggle and the shift are fixed constructed "
                "patterns, not random noise, and the exponent search covers b from -1.000 to -0.010 in steps of 0.001. The "
                "fitted a and c are rounded to three decimals before they are added. "
                "If the true curve had a different shape, the miss could be larger than shown."
            ),
            "check": "With exact measurements and a = 1.5, c = 1.0, what loss does the fit forecast at C = 1, and what is the residual at 3 powers of ten?",
            "answer": "Forecast = a x 1 + c = 1.5 + 1.0 = 2.5 because 1 to any power is 1. The observed value is also 2.5, so the residual is 2.5 - 2.5 = 0, at any distance.",
            "provenance": "Constructed example: a loss curve of the form in Equation (3.1) with constants defined for this reader. It is a schematic of the shape of the chapter's GPT-4 loss forecast and is not that report's data.",
            "source_section": "The forecast model",
            "source_anchor": "the-forecast-model",
            "controls": [
                {"key": "decades", "label": "Powers of ten between the largest fit run and the held-out run", "values": [1, 2, 3, 4], "default": 2},
                {"key": "runs", "label": "What the measured runs contain", "values": ["exact", "wiggle", "silent"], "default": "wiggle",
                 "value_labels": ["Exact values on the curve", "Wiggle of 0.04 up or down", "Two largest runs trained differently (unrecorded, +0.10)"]},
            ],
            "function": "extrapolation_picture",
            "misconception": {
                "title": "A small miss over a short range is the same achievement as over a long one",
                "text": ("The chapter says extrapolating from 1 billion to 2 billion parameters is a different achievement from extrapolating across four "
                         "orders of magnitude, and the two produce the same-looking plot; an honest report states the range as prominently as the residual."),
            },
            "scope_note": {
                "text": ("The GPT-4 result covers loss and one bounded HumanEval aggregate for one family."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C03-D02",
            "title": "The commitment boundary and the registered interval",
            "question": "Given three development measurements and a stated error bound, what point and interval does the team register, what does each possible result say, and what changes if the forecast is rewritten after the result is seen?",
            "equations": [EQ_SLOPE],
            "symbols": (
                "x is a declared family coordinate and the contrast is the measured interaction for the member at x. Three "
                "development members sit at x = 1, 2, 3. The slope and intercept come from a straight line fitted by least "
                "squares. The error bound is set at 0.02: the stipulated largest distance of any observation from one common true line. "
                "The residual is observed minus forecast. The first control is the observed contrast at x = 4; the second says whether the forecast "
                "stays as registered, is refitted through all four points after the result, or gets an interval written after the result."
            ),
            "prediction": "With the forecast kept as registered, an observed contrast of 0.36 is 0.03 below the forecast 0.39. Is it inside the interval?",
            "prediction_options": ["Inside", "Outside"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The interval runs from 0.323333 to 0.456667, so 0.36 is inside: one successful check, not a proof of the line.",
                "incorrect": "Set the observed value to 0.36 with the forecast kept: the interval is 0.39 plus or minus 0.066667, from 0.323333 to 0.456667, so it is inside.",
            },
            "explanation": (
                "The forecast at x = 4 is a weighted sum of the three development values with weights -2/3, 1/3 and 4/3. "
                "Each observation can be off by at most the bound, so the forecast can be off by the sum of the weights in "
                "size times the bound, plus one more bound for the new observation. Figure 3.2 shows where the line falls: steps 1 to 6 are committed before "
                "the answer exists, steps 7 and 8 can be written only afterwards. A forecast or an interval rewritten after step 7 can no longer lose."
            ),
            "application": (
                "Write the point forecast and an interval with a stated construction before the held-out member exists. A "
                "point alone hides how much uncertainty the team knew it had, and an interval that is declared in advance "
                "can be missed, which is what makes a hit mean something."
            ),
            "assumptions": (
                "The guarantee is conditional: the true relation is a straight line and every observation is within the "
                "stipulated bound of it. The three development points do not prove either. This is a worst-case interval, not "
                "a claimed 95 percent coverage rate, and one hit does not establish that the assumptions will keep holding. A nominal 95 percent "
                "procedure, unlike this bound, is allowed to miss."
            ),
            "check": "Keep the forecast as registered. The observed contrast is 0.46. What is the residual, and is it inside the interval?",
            "answer": "Residual = 0.46 - 0.39 = 0.07. The interval ends at 0.456667, so 0.46 is just outside it: an assumption needs investigating, not hiding.",
            "provenance": "Constructed example: the chapter's own worked forecast (points 1, 2, 3 with contrasts 0.10, 0.21, 0.29; interval half-width 0.066667 and the held-out result 0.43), with the other observed results and the after-the-fact choices defined for this reader.",
            "source_section": "A constructed forecast example",
            "source_anchor": "a-constructed-forecast-example",
            "controls": [
                {"key": "observed", "label": "Observed contrast at x = 4", "values": [0.30, 0.36, 0.43, 0.50], "default": 0.43},
                {"key": "commitment", "label": "What the team does after seeing the result", "values": ["kept", "refit", "posthoc"], "default": "kept",
                 "value_labels": ["Keeps the registered forecast", "Refits through all four points", "Writes an interval around the forecast"]},
            ],
            "function": "commit_picture",
            "misconception": {
                "title": "A refit that matches the result is a better forecast",
                "text": ("The chapter says that if the forecast changes after the held-out score becomes visible, the exercise stops being prospective: "
                         "it may still be a useful fit, but it is no longer a recorded prediction, and the distinction is invisible in the published numbers."),
            },
            "scope_note": {
                "text": ("Equation (3.2) is a proposal; the cited studies do not report that prospective interaction-contrast test."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C03-D03",
            "title": "Smooth ability, abrupt score",
            "question": "When does a sudden jump in a reported pass-or-fail score reflect a sudden change in the model, and when only the cutoff?",
            "equations": [EQ_PASS],
            "symbols": (
                "m numbers the members of a family in order of scale. q is the probability that one attempt by member m "
                "succeeds, a smooth quantity on the left. The threshold (tau) is a cutoff chosen in advance. The verdict "
                "on the right is 1 when q is at least tau and 0 otherwise. The four profiles are constructed curves for q."
            ),
            "prediction": "Choose the metric-created jump and compare the left and right panels. By how much does q change at the step where the score jumps from 0 to 1?",
            "prediction_options": ["By 1, as much as the score", "By 0.1, a small step like every other", "By 0.5"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "q rises by 0.1 at every member (0.4 to 0.5 at the jump), so the sudden event belongs to the cutoff, not to the model.",
                "incorrect": "Choose the metric-created jump at threshold 0.50: q goes from 0.40 to 0.50, a step of 0.1 like every other, while the verdict jumps by 1.",
            },
            "explanation": (
                "Equation (3.3) turns the graded q into one bit. A small change in q next to the threshold produces a "
                "change of one whole point in the reported score. The same flip can accompany a gentle rise in q or a sharp "
                "one, so the thresholded score alone cannot say which story it is."
            ),
            "application": (
                "For any new family, record q beside the thresholded verdict and read the pair. If only the verdict is "
                "kept, a flat early stretch can be mistaken for no progress, and a jump can be mistaken for a change inside the model."
            ),
            "assumptions": (
                "q is treated as known; in practice it is estimated from repeated attempts and carries sampling error. The "
                "four curves are constructed illustrations, and a graded measure does not guarantee smooth capability "
                "in an arbitrary model. A sharp rise in q is evidence of concentrated change in measured behavior, not proof of a phase transition."
            ),
            "check": "Take the metric-created jump with q = 0.1 + 0.1 x (m - 1) and a threshold of 0.65. Which member is the first to pass?",
            "answer": "q(7) = 0.1 + 0.1 x 6 = 0.70 >= 0.65 and q(6) = 0.1 + 0.1 x 5 = 0.60 < 0.65, so member 7 is the first to pass.",
            "provenance": "Constructed example: four success-probability curves and two thresholds defined for this reader to match the chapter's four profiles. No real model is measured.",
            "source_section": "Smooth ability, abrupt score",
            "source_anchor": "smooth-ability-abrupt-score",
            "controls": [
                {"key": "profile", "label": "Profile of the success probability", "values": ["latent", "jump", "onset", "none"], "default": "jump",
                 "value_labels": [PROFILES[k][0] for k in ("latent", "jump", "onset", "none")]},
                {"key": "tau", "label": "Threshold", "values": [0.5, 0.8], "default": 0.5},
            ],
            "function": "threshold_picture",
            "misconception": {
                "title": "A sudden score jump is a sudden change inside the model",
                "text": ("The chapter says a metric-created jump is real as a change in the reported result, but it is not evidence of sudden internal "
                         "reorganization, and a sharp rise in q is not by itself proof of a phase transition."),
            },
            "scope_note": {
                "text": ("Nothing here establishes a universal threshold or a maximum amount of cooperation."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C03-D04",
            "title": "Declare the family before the outcomes arrive",
            "question": "Why does it matter that the shape of the fitted relation is fixed before the held-out results are visible?",
            "equations": [EQ_GAMMA],
            "symbols": (
                "In this demonstration the measured score for member m is the constructed number on the vertical axis, and the "
                "declared feature is the scale x, used directly (the straight-line family) or as ln(x), the natural "
                "logarithm of x (the log family). The fitted line is the function f_psi in Equation (3.2), where psi stands for "
                "the line's fitted intercept and slope, and the plotted score stands in for the quantity Gamma_m on the left "
                "of that equation. The leftover epsilon_m is the "
                "residual, observed minus forecast. RMSE is the square root of the mean squared residual. The laboratory "
                "uses the same observed-minus-forecast convention. The first control picks the development data: a straight "
                "rise forecast at scales 4 and 5, or log-shaped data forecast at scales 8 and 16."
            ),
            "prediction": "Declare the straight-line family and let the outcomes flatten off (0.45, 0.48). Which family would fit better after the fact, and does that change the registered forecast?",
            "prediction_options": ["The log family fits better, and the registered forecast is unchanged",
                                   "The log family fits better, so the forecast should be replaced",
                                   "The straight line fits better"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The log family has the smaller RMSE after the fact, but switching now would be a retrospective fit; the registered forecast keeps its own RMSE.",
                "incorrect": "Declare the straight line and choose flattening off: the metrics show the log family with the smaller RMSE, yet the registered forecast stays as made.",
            },
            "explanation": (
                "The line or curve is fitted to the three development members only and then frozen. The outcomes at the test scales "
                "score it and never change its coefficients. A family picked after seeing the outcomes can "
                "always look at least as good, because that choice spends the evidence. With log-shaped development data the log family forecasts "
                "exactly and the straight line overshoots the continued outcomes (3.218 and 6.783 against 2.079 and 2.773)."
            ),
            "application": (
                "Before a held-out result exists, write down the family, the transformation and the rule for choosing among "
                "several shapes, and file that with the forecast. Afterwards report the residual whether or not it is flattering."
            ),
            "assumptions": (
                "Three development points and two test points, with only two candidate shapes. Both families fit three points "
                "reasonably well, which is exactly why the choice between them is a free parameter worth declaring. The "
                "demonstration cannot detect a family chosen in private after the outcomes; that is a matter of procedure. The outcomes other than the "
                "laboratory's own are defined for this reader."
            ),
            "check": "Declare the log family on the first data set and let the outcomes flatten off. What is the frozen forecast at x = 4?",
            "answer": "The log fit has slope 0.1780 and intercept 0.1937, so the forecast is 0.1780 x ln(4) + 0.1937 = 0.1780 x 1.3863 + 0.1937 = 0.440, close to the observed 0.45.",
            "provenance": "Constructed example: the laboratory's development points (1, 0.2), (2, 0.3), (3, 0.4) with test scales 4 and 5, and its log-shaped transfer data (1, 0), (2, 0.6931), (4, 1.3863) with test scales 8 and 16; the outcomes other than the transfer case's continuation are defined for this reader.",
            "source_section": "The eight-step protocol",
            "source_anchor": "the-eight-step-protocol",
            "controls": [
                {"key": "data", "label": "Development data", "values": ["default", "transfer"], "default": "default",
                 "value_labels": ["Straight rise: (1, 0.2), (2, 0.3), (3, 0.4)", "Log-shaped: (1, 0), (2, 0.69), (4, 1.39)"]},
                {"key": "family", "label": "Family declared in advance", "values": ["linear", "log"], "default": "linear",
                 "value_labels": ["Straight line in x", "Straight line in ln(x)"]},
                {"key": "outcome", "label": "Outcomes revealed afterwards", "values": ["extended", "faster", "flattening"], "default": "faster",
                 "value_labels": [OUTCOME_LABELS[k] for k in ("extended", "faster", "flattening")]},
            ],
            "function": "family_picture",
            "scope_note": {
                "text": ("Equation (3.2) is a proposal; the cited studies do not report that prospective interaction-contrast test. "
                         "The worked forecast numbers are constructed."),
                "source_section": "What this does not settle",
            },
            "misconception": {
                "title": "Choosing the best family afterwards is a normal analytic decision with no cost",
                "text": ("The chapter says each such move is a normal analytic decision, yet each one quietly spends some of the evidence that the "
                         "relationship is real rather than fitted, and the finished plot looks the same either way."),
            },
        },
    ],
}
