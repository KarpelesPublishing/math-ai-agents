"""Chapter 12 reader tests: independent hand checks.

Every expected number is recomputed here from the chapter's own arithmetic:
the update rules are re-run pass by pass without the laboratory, the eight
episodes use the closed form, the lambda weights come from Equation (12.4), and
the random-walk panel is re-derived from the two theorems the chapter states
(the outcome rule settles on the average return of each state; the one-step
rule settles on the values of the empirical Markov chain). The reader is built
into a temporary directory, never the shared readers folder.
"""
from __future__ import annotations

import html
import importlib.util
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parent.parent
ENGINE = LAB / "tools" / "readers" / "engine"
CHAPTERS = LAB / "tools" / "readers" / "chapters"
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = ENGINE / "dom_harness.js"
PYTHON = LAB / ".venv" / "bin" / "python"
for p in (str(LAB / "src"), str(ENGINE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

spec = importlib.util.spec_from_file_location("reader_ch12", CHAPTERS / "ch12.py")
ch12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch12)


def run(i, **controls):
    d = ch12.CHAPTER["demos"][i]
    fig, metrics, text, extra = getattr(ch12, d["function"])(**controls)
    plt.close(fig)
    return metrics, text, extra


def states(i):
    d = ch12.CHAPTER["demos"][i]
    for combo in itertools.product(*[c["values"] for c in d["controls"]]):
        yield {c["key"]: v for c, v in zip(d["controls"], combo)}


# The four runs, written out here from the book and the workbook (not read from the module).
RUNS = {
    "book": dict(states=["s1", "s2", "s3", "s4", "end"], rewards=[0, 0, 0, 1], g=1.0, a=0.1, lam=0.0, terminal=True,
                 v={"s1": .5, "s2": .5, "s3": .5, "s4": .5, "end": 0.0}),
    "default": dict(states=["draft", "review", "done"], rewards=[0, 1], g=1.0, a=0.5, lam=0.8, terminal=True,
                    v={"draft": 0.0, "review": 0.0, "done": 0.0}),
    "changed": dict(states=["draft", "review", "done"], rewards=[0, 1], g=1.0, a=0.5, lam=0.8, terminal=False,
                    v={"draft": 0.0, "review": 0.0, "done": 2.0}),
    "transfer": dict(states=["a", "b", "c", "d"], rewards=[1, 0, 2], g=0.9, a=0.2, lam=0.0, terminal=True,
                     v={"a": 0.0, "b": 1.0, "c": 0.0, "d": 0.0}),
}


def one_pass(run_, outcome, onestep, trace):
    """One sequential pass of the three rules."""
    S, R, g, a, lam = run_["states"], run_["rewards"], run_["g"], run_["a"], run_["lam"]
    n = len(R)
    boot = 0.0 if run_["terminal"] else run_["v"][S[-1]]
    G = [0.0] * n
    acc = boot
    for t in reversed(range(n)):
        acc = R[t] + g * acc
        G[t] = acc
    for t in range(n):
        outcome[S[t]] += a * (G[t] - outcome[S[t]])
    for t in range(n):
        nxt = 0.0 if run_["terminal"] and t == n - 1 else onestep[S[t + 1]]
        onestep[S[t]] += a * (R[t] + g * nxt - onestep[S[t]])
    elig = {k: 0.0 for k in trace}
    for t in range(n):
        nxt = 0.0 if run_["terminal"] and t == n - 1 else trace[S[t + 1]]
        err = R[t] + g * nxt - trace[S[t]]
        elig[S[t]] += 1
        for k in trace:
            trace[k] += a * err * elig[k]
            elig[k] *= g * lam


def values_after(case, k):
    run_ = RUNS[case]
    o, d, tr = dict(run_["v"]), dict(run_["v"]), dict(run_["v"])
    for _ in range(k):
        one_pass(run_, o, d, tr)
    return o, d, tr


class Chapter12ReaderTests(unittest.TestCase):
    def test_structure(self):
        demos = ch12.CHAPTER["demos"]
        self.assertEqual([d["id"] for d in demos], ["C12-D01", "C12-D02", "C12-D03", "C12-D04"])
        sizes = []
        for d in demos:
            n = 1
            for c in d["controls"]:
                n *= len(c["values"])
            sizes.append(n)
        self.assertEqual(sizes, [12, 6, 8, 12])
        self.assertIn("prompt", ch12.CHAPTER["ask_skill"])
        self.assertEqual(demos[0]["stepper"], "passes_done")
        for d in demos:
            self.assertIn("misconception", d)

    def test_every_state_renders_with_steps_and_alt(self):
        for i in range(4):
            for kw in states(i):
                m, text, extra = run(i, **kw)
                self.assertTrue(m and text and extra["alt"] and 2 <= len(extra["steps"]) <= 8, (i, kw))
                for s in extra["steps"]:
                    self.assertLessEqual(len(s), 240, s)
                for bad in ("\u2014", "\u2013", "--"):
                    self.assertNotIn(bad, text + " ".join(extra["steps"]))

    def test_d01_every_rule_pass_by_pass(self):
        for case, k in itertools.product(RUNS, [1, 2, 3]):
            run_ = RUNS[case]
            o, d, tr = values_after(case, k)
            shown = run_["states"][:-1]
            m, _, _ = run(0, case=case, passes_done=k)
            # three decimals, four when a real move would otherwise print as no move
            f3 = lambda x, s: f"{x:.4f}" if (abs(x - run_["v"][s]) > 1e-12 and f"{x:.3f}" == f"{run_['v'][s]:.3f}") else f"{x:.3f}"
            self.assertEqual(m["Outcome rule, states in order"], ", ".join(f3(o[s], s) for s in shown))
            self.assertEqual(m["One-step rule, states in order"], ", ".join(f3(d[s], s) for s in shown))
            if run_["lam"] > 0:
                self.assertEqual(m["Trace rule (lambda 0.8), states in order"], ", ".join(f3(tr[s], s) for s in shown))
            moved = lambda v: sum(1 for s in shown if abs(v[s] - run_["v"][s]) > 1e-12)
            self.assertEqual(m["States moved (outcome / one-step)"], f"{moved(o)} / {moved(d)}")
        # the book's numbers: 0.5 + 0.1 (1 - 0.5) = 0.55 for all four; only state 4 moves under the one-step rule
        m, t, _ = run(0, case="book", passes_done=1)
        self.assertEqual(m["Outcome rule, states in order"], "0.550, 0.550, 0.550, 0.550")
        self.assertEqual(m["One-step rule, states in order"], "0.500, 0.500, 0.500, 0.550")
        self.assertEqual(m["States moved (outcome / one-step)"], "4 / 1")
        self.assertIn("0.5 + 0.1 x (1 - 0.5) = 0.55", t)
        # news travels back one state per pass under the one-step rule
        self.assertEqual(run(0, case="book", passes_done=2)[0]["States moved (outcome / one-step)"], "4 / 2")
        self.assertEqual(run(0, case="book", passes_done=3)[0]["States moved (outcome / one-step)"], "4 / 3")
        # notebook worked interpretation: outcome 0.5, 0.5; one-step 0, 0.5; trace 0.4, 0.5
        d1 = run(0, case="default", passes_done=1)[0]
        self.assertEqual((d1["Outcome rule, states in order"], d1["One-step rule, states in order"],
                          d1["Trace rule (lambda 0.8), states in order"]), ("0.500, 0.500", "0.000, 0.500", "0.400, 0.500"))
        # truncated: returns 3 and 3 (final estimate 2 kept), so the outcome rule gives 1.5 each
        c1, ct, _ = run(0, case="changed", passes_done=1)
        self.assertEqual(c1["Outcome rule, states in order"], "1.500, 1.500")
        self.assertIn("truncated", ct)
        # transfer: lambda 0, so no trace rule; one-step a = 0 + 0.2 (1 + 0.9 x 1 - 0) = 0.38
        t1 = run(0, case="transfer", passes_done=1)[0]
        self.assertFalse(any("Trace" in k for k in t1))
        self.assertEqual(t1["One-step rule, states in order"].split(", ")[0], "0.380")

    def test_d02_eight_episodes_by_hand(self):
        for kw in states(1):
            ones, a_final = kw["ones_in_b_only"], kw["a_final"]
            b_rewards = [a_final] + [1] * ones + [0] * (7 - ones)
            va = vb = 0.0
            for _ in range(20000):
                va, vb = va + 0.05 * (vb - va), vb + 0.05 * (sum(r - vb for r in b_rewards) / 8)
            m, _, _ = run(1, **kw)
            self.assertAlmostEqual(float(m["Value of B (both rules)"]), vb, places=3)
            self.assertAlmostEqual(float(m["Value of A, one-step rule"]), va, places=3)
            self.assertEqual(m["Value of A, outcome rule"], f"{float(a_final):.3f}")
            self.assertEqual(m["Value of B (both rules)"], f"{(ones + a_final) / 8:.3f}")
            self.assertEqual(m["Disagreement about A"], f"{abs((ones + a_final) / 8 - a_final):.3f}")
        m, _, _ = run(1, ones_in_b_only=6, a_final=0)
        self.assertEqual((m["Value of B (both rules)"], m["Value of A, outcome rule"], m["Value of A, one-step rule"]),
                         ("0.750", "0.000", "0.750"))
        self.assertEqual(run(1, ones_in_b_only=7, a_final=1)[0]["Disagreement about A"], "0.000")
        self.assertEqual(run(1, ones_in_b_only=3, a_final=0)[0]["Value of B (both rules)"], "0.375")

    def test_d03_lambda_weights_by_hand(self):
        for kw in states(2):
            lam = kw["lam"]
            w = [(1 - lam) * lam ** (k - 1) for k in range(1, 8)] + [lam ** 7]
            self.assertAlmostEqual(sum(w), 1.0, places=12)
            m, _, _ = run(2, **kw)
            self.assertEqual(m["Weight on the one-step target"], f"{w[0]:.4f}")
            self.assertEqual(m["Weight on the full return"], f"{w[-1]:.4f}")
            self.assertEqual(m["Weights add to"], "1.0000")
        m = run(2, lam=0.9, protocol="repeated")[0]
        self.assertEqual((m["Weight on the full return"], m["Weight on the one-step target"]), ("0.4783", "0.1000"))
        self.assertAlmostEqual(0.9 ** 7, 0.4782969, places=6)
        z = run(2, lam=0, protocol="repeated")[0]
        o = run(2, lam=1, protocol="repeated")[0]
        self.assertEqual((z["Weight on the one-step target"], z["Weight on the full return"]), ("1.0000", "0.0000"))
        self.assertEqual((o["Weight on the one-step target"], o["Weight on the full return"]), ("0.0000", "1.0000"))
        self.assertAlmostEqual(0.3 ** 7, 0.0002187, places=7)

    def test_d03_random_walk_from_the_two_theorems(self):
        """Replicate the panel's end points from closed forms: the outcome rule is the mean return of each state;
        the one-step rule is the value function of the empirical Markov chain."""
        rng = np.random.default_rng(0)
        true = np.arange(1, 6) / 6
        sets = []
        for _ in range(100):
            train = []
            for _ in range(10):
                s, seq = 3, []
                while True:
                    seq.append(s)
                    s += 1 if rng.random() < 0.5 else -1
                    if s in (0, 6):
                        train.append((seq, 1.0 if s == 6 else 0.0))
                        break
            sets.append(train)
        err_mc, err_td, train_mc, train_td = [], [], [], []
        for train in sets:
            visits = {}
            for seq, z in train:
                for s in seq:
                    visits.setdefault(s, []).append(z)
            mc = np.full(5, 0.5)
            for s, zs in visits.items():
                mc[s - 1] = np.mean(zs)
            # empirical Markov chain: counts of moves from each visited state
            n_state = {s: 0 for s in visits}
            to = {s: {} for s in visits}
            for seq, z in train:
                path = seq + [6 if z == 1.0 else 0]
                for a, b in zip(path[:-1], path[1:]):
                    n_state[a] += 1
                    to[a][b] = to[a].get(b, 0) + 1
            order = sorted(visits)
            idx = {s: i for i, s in enumerate(order)}
            M = np.eye(len(order))
            rhs = np.zeros(len(order))
            for s in order:
                for b, c in to[s].items():
                    if b in idx:
                        M[idx[s], idx[b]] -= c / n_state[s]
                    elif b == 6:
                        rhs[idx[s]] += c / n_state[s]
            td = np.full(5, 0.5)
            sol = np.linalg.solve(M, rhs)
            for s in order:
                td[s - 1] = sol[idx[s]]
            rms = lambda w: float(np.sqrt(np.mean((w - true) ** 2)))
            err_mc.append(rms(mc))
            err_td.append(rms(td))
            terr = lambda w: float(np.sqrt(np.mean([(w[s - 1] - z) ** 2 for seq, z in train for s in seq])))
            train_mc.append(terr(mc))
            train_td.append(terr(td))
        m = run(2, lam=0, protocol="repeated")[0]
        self.assertEqual(m["Random-walk error at lambda 0 and 1"], f"{np.mean(err_td):.3f} and {np.mean(err_mc):.3f}")
        self.assertEqual(m["Training-sample error at lambda 0 and 1"], f"{np.mean(train_td):.3f} and {np.mean(train_mc):.3f}")
        # the chapter's claims about this experiment
        self.assertGreater(np.mean(err_mc), np.mean(err_td))          # outcome rule last against the truth
        self.assertLess(np.mean(train_mc), np.mean(train_td))         # but best on the training sample
        # single presentation: best step size per lambda, replayed here for the two end points
        def once(train, lam, alpha):
            w = np.full(5, 0.5)
            for seq, z in train:
                e = np.zeros(5)
                dw = np.zeros(5)
                for t, s in enumerate(seq):
                    e = lam * e
                    e[s - 1] += 1
                    nxt = w[seq[t + 1] - 1] if t < len(seq) - 1 else z
                    dw += (nxt - w[s - 1]) * e
                w = w + alpha * dw
            return w
        rms = lambda w: float(np.sqrt(np.mean((w - true) ** 2)))
        for lam in (0.0, 1.0):
            best = min((np.mean([rms(once(tr, lam, a)) for tr in sets]), a) for a in [round(0.05 * i, 2) for i in range(13)])
            mm = run(2, lam=lam, protocol="once")[0]
            self.assertEqual(mm["Best step size at this lambda"], f"{best[1]:.2f}")
            self.assertEqual(mm["Random-walk error at this lambda"], f"{best[0]:.3f}")
        # Figure 12.2: the five true values are 1/6 to 5/6
        self.assertEqual([round(6 * v) for v in true], [1, 2, 3, 4, 5])

    def test_d04_td_error_and_lookahead_by_hand(self):
        for kw in states(3):
            succ, alpha = kw["successor"], kw["alpha"]
            m, _, _ = run(3, **kw)
            delta = -0.02 + succ - 0.20
            self.assertEqual(m["TD error delta"], f"{delta:.2f}")
            self.assertEqual(m["Sign"], "positive" if delta > 1e-12 else ("zero" if abs(delta) < 1e-12 else "negative"))
            self.assertEqual(m["Successor estimate that gives zero"], "0.22")
            y = 0.5 + alpha * (1 + 0 - 0.5)
            self.assertEqual(m["Continuation estimate after training"], f"{y:.3f}")
            self.assertEqual(m["Inspect after training"], f"{-0.1 + y:.3f}")
            inspect = -0.1 + y
            expect = "tie" if abs(inspect - 0.6) < 1e-9 else ("inspect" if inspect > 0.6 else "finish")
            self.assertEqual(m["Action chosen after training"], expect)
        # the book: 0.28 and -0.12; finish 0.6 against inspect 0.4, then 0.9 and 0.8 at step size 0.8
        self.assertEqual(run(3, successor=0.5, alpha=0.8)[0]["TD error delta"], "0.28")
        self.assertEqual(run(3, successor=0.1, alpha=0.8)[0]["TD error delta"], "-0.12")
        b = run(3, successor=0.5, alpha=0.8)[0]
        self.assertEqual((b["Continuation estimate after training"], b["Inspect after training"], b["Action chosen after training"]),
                         ("0.900", "0.800", "inspect"))
        self.assertEqual(run(3, successor=0.5, alpha=0.4)[0]["Action chosen after training"], "tie")
        self.assertEqual(run(3, successor=0.5, alpha=0.3)[0]["Action chosen after training"], "finish")
        self.assertEqual(run(3, successor=0.5, alpha=0.5)[0]["Action chosen after training"], "inspect")
        self.assertIn("-0.02 + 0.50 - 0.20 = 0.28", run(3, successor=0.5, alpha=0.8)[1].replace("(-0.02)", "-0.02"))

    def test_check_questions(self):
        self.assertAlmostEqual(0 + 0.5 * (1 - 0), 0.5)                 # D01 check: outcome rule gives draft 0.5
        self.assertEqual(run(0, case="default", passes_done=1)[0]["One-step rule, states in order"].split(", ")[0], "0.000")
        self.assertAlmostEqual(3 / 8, 0.375)                           # D02 check
        self.assertAlmostEqual(0.5 + 0.5 * 0.5, 0.75)                  # D04 check: step size 0.5
        self.assertAlmostEqual(-0.1 + 0.75, 0.65)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 12)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        for d in ch12.CHAPTER["demos"]:
            for tex in d["equations"]:
                self.assertIn(norm(html.unescape(tex)), allowed, d["id"])

    def test_text_rules(self):
        blob = json.dumps(ch12.CHAPTER, ensure_ascii=False)
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, blob)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, blob.lower())
        for d in ch12.CHAPTER["demos"]:
            self.assertIn("constructed", d["provenance"].lower())
            self.assertTrue(d["check"].endswith("?"))
        for i in (0, 2, 3):
            self.assertEqual(ch12.CHAPTER["demos"][i]["scope_note"]["source_section"], "What this does not settle")


@unittest.skipUnless(PYTHON.is_file(), "laboratory .venv absent")
class Chapter12BuiltPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="reader-ch12-test-")
        r = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "12", "--out", cls.tmp], capture_output=True, text=True,
                           timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert r.returncode == 0, r.stdout + r.stderr
        cls.reader = Path(cls.tmp) / "12-trajectory-credit" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S).group(1))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_size_states_and_panels(self):
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 6, 8, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)
        for text in ("Ask the chapter skill", "What this does not settle", "Common wrong turn", "Your prediction", "Worked steps"):
            self.assertIn(text, self.page)
        self.assertGreaterEqual(len(re.findall(r'data-tex="', self.page)), 4)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        r = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        report = json.loads(r.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 38)


class Chapter12Patch2Tests(unittest.TestCase):
    def test_small_moves_print_with_four_decimals(self):
        m, text, _ = run(0, case="book", passes_done=3)
        self.assertEqual(m["One-step rule, states in order"].split(", ")[1], "0.5005")
        self.assertNotEqual(m["One-step rule, states in order"].split(", ")[1], "0.500")
        self.assertEqual(ch12.est_text(0.5005, 0.5), "0.5005")
        self.assertEqual(ch12.est_text(0.55, 0.5), "0.55")
        self.assertEqual(ch12.est_text(0.5, 0.5, strip=False), "0.500")

    def test_figure_axis_says_labels_are_new_estimates(self):
        d = ch12.CHAPTER["demos"][0]
        fig, *_ = ch12.trajectory_picture(case="book", passes_done=1)
        try:
            self.assertIn("bar labels give the new estimate", fig.axes[0].get_ylabel())
        finally:
            plt.close(fig)

    def test_d04_wording(self):
        low = run(3, successor=0.1, alpha=0.8)[1]
        self.assertIn("The estimate fell from 0.20 to 0.10", low)
        self.assertNotIn("did not rise enough", low)
        high = run(3, successor=0.8, alpha=0.8)[1]
        self.assertNotIn("Suppose the search itself was unhelpful", high)
        self.assertIn("Like the book's first search, this one was unhelpful", high)
        self.assertIn("The book's first search was unhelpful", run(3, successor=0.5, alpha=0.8)[1])
        for t in (low, high):
            self.assertNotIn("never changes which action caused any outcome", t)
            self.assertIn("does not say which action caused any outcome", t)

    def test_correct_prediction_is_not_always_first(self):
        self.assertNotEqual({d["prediction_answer"] for d in ch12.CHAPTER["demos"]}, {0})


if __name__ == "__main__":
    unittest.main()
