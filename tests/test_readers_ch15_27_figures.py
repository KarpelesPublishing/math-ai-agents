"""Independent arithmetic checks of the actual artists in every late-chapter state.

The older reader tests check HTML numbers, worked steps and contracts. These checks
also inspect unrounded Matplotlib bars, curves, markers and diagram cells before
serialization. Expected values use arithmetic, finite enumeration and separately
declared teaching inputs; no production calculator supplies an expected result.
Control axes come from the authored interface so every selectable state is visited.
"""
from __future__ import annotations

import importlib.util
import itertools
import math
from pathlib import Path
import sys
import unittest

LAB = Path(__file__).resolve().parents[1]
for directory in (LAB / "tools/readers/engine", LAB / "src"):
    sys.path.insert(0, str(directory))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def chapter(number):
    spec = importlib.util.spec_from_file_location(
        f"late_chapter_plot_{number}", LAB / f"tools/readers/chapters/ch{number:02d}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def independent_fit(family):
    basis, interval = {
        "exp": (lambda k, p: math.exp(-k / p), (1.0, 400.0)),
        "hyp": (lambda k, p: 1.0 / (k + p), (0.01, 200.0)),
        "power": (lambda k, p: k ** (-p), (0.01, 3.0)),
    }[family]
    target = 0.15 / 0.08
    def residual(p):
        return (basis(10, p) - basis(25, p)) / (basis(25, p) - basis(50, p)) - target
    lo, hi = interval
    for _ in range(180):
        mid = (lo + hi) / 2
        if residual(lo) * residual(mid) <= 0:
            hi = mid
        else:
            lo = mid
    p = (lo + hi) / 2
    b = 0.15 / (basis(10, p) - basis(25, p))
    a = 0.63 + b * basis(50, p)
    return a, lambda k: a - b * basis(k, p)


class LateChapterFigureTests(unittest.TestCase):
    def equal(self, observed, expected):
        np.testing.assert_allclose(observed, expected, rtol=2e-10, atol=2e-12)

    def bars(self, ax, expected, horizontal=False, start=0):
        patches = ax.patches[start:start + len(expected)]
        self.assertEqual(len(patches), len(expected))
        self.equal([p.get_width() if horizontal else p.get_height() for p in patches], expected)

    def line(self, ax, index, formula):
        artist = ax.lines[index]
        x = np.asarray(artist.get_xdata(), dtype=float)
        y = np.asarray(artist.get_ydata(), dtype=float)
        self.equal(y, [formula(float(v)) for v in x])

    def cell(self, ax, x, y, word):
        texts = [t.get_text() for t in ax.texts
                 if np.allclose(t.get_position(), (x, y), rtol=0, atol=1e-10)]
        self.assertIn(word, texts, (x, y, word, texts))

    def run_chapter(self, number):
        mod = chapter(number)
        visited = 0
        for demo in mod.CHAPTER["demos"]:
            axes = [c["values"] for c in demo["controls"]]
            for values in itertools.product(*axes):
                kw = dict(zip([c["key"] for c in demo["controls"]], values))
                with self.subTest(demo=demo["id"], controls=kw):
                    result = getattr(mod, demo["function"])(**kw)
                    fig = result[0]
                    try:
                        getattr(self, f"check_{number}")(demo["id"][-2:], kw, fig)
                        for ax in fig.axes:
                            self.assertTrue(ax.get_xlabel() and ax.get_ylabel())
                            for artist in ax.lines:
                                self.assertTrue(np.isfinite(np.asarray(artist.get_xdata(), dtype=float)).all())
                                self.assertTrue(np.isfinite(np.asarray(artist.get_ydata(), dtype=float)).all())
                    finally:
                        plt.close(fig)
                visited += 1
        self.assertEqual(visited, sum(math.prod(len(c["values"]) for c in d["controls"])
                                     for d in mod.CHAPTER["demos"]))

    def test_ch15_all_selectable_figures(self): self.run_chapter(15)
    def test_ch16_all_selectable_figures(self): self.run_chapter(16)
    def test_ch17_all_selectable_figures(self): self.run_chapter(17)
    def test_ch18_all_selectable_figures(self): self.run_chapter(18)
    def test_ch19_all_selectable_figures(self): self.run_chapter(19)
    def test_ch20_all_selectable_figures(self): self.run_chapter(20)
    def test_ch21_all_selectable_figures(self): self.run_chapter(21)
    def test_ch22_all_selectable_figures(self): self.run_chapter(22)
    def test_ch23_all_selectable_figures(self): self.run_chapter(23)
    def test_ch24_all_selectable_figures(self): self.run_chapter(24)
    def test_ch25_all_selectable_figures(self): self.run_chapter(25)
    def test_ch26_all_selectable_figures(self): self.run_chapter(26)
    def test_ch27_all_selectable_figures(self): self.run_chapter(27)

    def test_reported_measurements_have_explicit_provenance(self):
        reported = {
            "C19-D01": "source-reported measurements with derived comparisons",
            "C19-D03": "source-reported measurements with derived comparisons",
            "C26-D03": "source-reported measurements and constructed comparisons",
        }
        for number in range(15, 28):
            for demo in chapter(number).CHAPTER["demos"]:
                if demo["id"] in reported:
                    self.assertEqual(demo["evidence_kind"], reported[demo["id"]])
                else:
                    self.assertNotIn("source-reported", demo.get("evidence_kind", ""))

    def check_15(self, d, k, f):
        a = f.axes
        if d == "01":
            records = {
                "chapter": [(2, 8, True), (2, 3, True), (2, 0, False), (2, 0, True)],
                "default": [(4, 8, True), (2, 3, True), (1, 100, False)],
                "changed": [(4, 8, True), (2, 3, True), (1, 100, False)],
                "transfer": [(1, 10, False), (3, 4, True)],
            }[k["case"]]
            self.bars(a[0], [value - k["lam"] * tokens if ok else 0
                             for tokens, value, ok in records], horizontal=True)
        elif d == "02":
            e = k["epsilon"]
            full, summary = {
                "worst": ([10, 6, 3], [10-e, 6+e, 3]),
                "dropped": ([-50, 6, 3], [10, 6, 3]),
                "default": ([4, 6], [3, 5]),
                "changed": ([4, 6], [6, 5]),
            }[k["summary"]]
            self.bars(a[0], full + summary)
            regret = max(max(full)-full[i] for i, v in enumerate(summary)
                         if v == max(summary))
            self.bars(a[1], [regret, 2*e], horizontal=True)
        elif d == "03":
            available = [i for i in (0, 1, 2)
                         if not (i == 0 and k["deletion"] == "all")
                         and not (i == 2 and k["authority"] == "unreachable")]
            sim = [0.98, 0.80, k["revocation_similarity"]]
            picks = [available[-1], max(available, key=lambda i: sim[i]),
                     2 if 2 in available else 3]
            self.equal([line.get_xdata()[0] for line in a[0].lines], picks)
            self.equal([line.get_ydata()[0] for line in a[0].lines], [2, 1, 0])
        else:
            p, lam = k["p_current"], k["lam"]
            self.bars(a[0], [8*p, lam, 8*p-lam])
            for i, penalty in enumerate((1, 2, 4)):
                self.line(a[1], i, lambda q, penalty=penalty: 8*q-penalty)

    def check_16(self, d, k, f):
        a = f.axes
        if d == "01":
            p = k["p"]
            self.line(a[0], 0, lambda n: 1-(1-p)**n)
            self.line(a[0], 1, lambda n: (1-(1-2*p)**n)/2)
            self.line(a[0], 2, lambda n: p)
            self.line(a[1], 0, lambda n: p*(1-p)**(n-1))
            self.line(a[1], 1, lambda n: max(1e-30, p*(1-2*p)**(n-1)))
            self.assertEqual(a[1].get_yscale(), "log")
        elif d == "02":
            p = 0.7 if k["setting"] == "transfer" else 0.4
            shared = k["setting"] == "shared"
            def coverage(n): return p if shared else 1-(1-p)**n
            def selected(n): return p if n == 1 else (coverage(n) if shared else coverage(n)*k["selector"])
            self.line(a[0], 0, coverage)
            self.line(a[0], 1, selected)
            counts = (1, 2, 4) if k["setting"] == "transfer" else (1, 2, 3, 5)
            self.bars(a[1], [selected(n) for n in counts])
        elif d == "03":
            q3, q4 = {"book": (0.73, 0.785), "strong": (0.95, 0.95),
                      "weak": (0.5, 0.5), "worse": (0.15, 0.15)}[k["selector"]]
            p = k["long_p"]
            self.bars(a[0], [p, .2, (1-.8**48)*q3, (1-(1-p)**12)*q4], horizontal=True)
        elif k["evidence"] == "observed":
            self.bars(a[0], [2, 3, 5]); self.bars(a[1], [0])
        else:
            self.bars(a[0], [1/.6, 1.5/.8, 2/.85])
            # First two lines are the deadline and required-rate threshold.
            for i, (t, p) in enumerate(((1, .6), (2, .8), (5, .85)), start=2):
                self.equal(a[1].lines[i].get_xdata(), [t]); self.equal(a[1].lines[i].get_ydata(), [p])

    def check_17(self, d, k, f):
        a = f.axes
        if d == "01":
            kind = k["kind"]
            expected = [100] + ([100]*3 if kind == "read" else [150]*3 if kind == "put"
                                else [0]*3 if kind == "delete" else [150]*3 if k["key"] == "stored"
                                else [150, 200, 250])
            self.bars(a[0], expected); self.bars(a[1], [1, 2, 3])
        elif d == "02":
            p, likelihood = k["prior"], k["silence_if_applied"]
            beta = likelihood*p/(likelihood*p+.5*(1-p))
            self.bars(a[0], [p, beta, 1-p, 1-beta])
            self.bars(a[1], [beta*k["c_dup"], (1-beta)*10, 1])
        elif d == "03":
            statuses = ["still in place"]*4
            if k["stage"] > 1:
                statuses = {"works": ["reported restored"]*4, "unavailable": ["still in place"]*4,
                            "partial": ["reported restored"]+["still in place"]*3,
                            "lost": ["unknown"]*4}[k["outcome"]]
            if k["stage"] == 3:
                statuses = ["verified restored" if s == "reported restored" else s for s in statuses]
            # Check the four status cells without treating reported restoration as verified restoration.
            actual = [t.get_text() for t in a[0].texts[:4]]
            expected_words = {"still in place": "Consequence still in place", "reported restored": "Undo applied, not yet verified",
                              "verified restored": "Verified restored", "unknown": "Not verified: the undo reply was lost"}
            self.assertEqual(actual, [expected_words[s] for s in statuses])
        else:
            # The authored six-step plan labels are verified by the independent reader suite.
            labels = [t.get_text() for t in a[0].texts]
            self.assertEqual(len(labels), 6)
            ready = k["evidence"] != "expired"
            self.assertEqual(labels[0], "true" if ready else "false")
            self.assertEqual(labels[1], "true" if k["step"] in ("merge", "delete") else "false")
            absent = k["evidence"] == "absent"
            self.assertEqual(labels[2], "true" if absent else "false")
            self.assertEqual(labels[3], "false")
            self.assertEqual(labels[-1], "true" if ready and "true" in labels[1:3] else "false")

    def check_18(self, d, k, f):
        a = f.axes
        if d == "01":
            p = k["belief_layout1"]
            if k["interface"] == "coordinate":
                expected = [p, 0, 1-p] if k["permission_check"] == "on" else [p, 1-p, 0]
            else:
                expected = [1, 0, 0] if k["interface"] == "semantic" else [p, 0, 1-p]
            self.bars(a[1], expected, horizontal=True)
        elif d == "02":
            prior = k["belief_layout2"]
            prob2 = prior if k["observation"] == "none" else 0 if k["observation"] == "layout1" else 1
            # Fixed coordinate is allowed only in layout 1; semantic request, metadata,
            # fresh screenshot and abstention survive either supported layout.
            for row in range(5):
                word = "survives" if row != 0 or prob2 == 0 else "removed"
                self.cell(a[0], 2.5, row+.5, word)
        elif d == "03":
            rate = .05 if k["scenario"] == "transfer" else .02
            self.line(a[1], 0, lambda t: math.exp(-rate*t))
            self.line(a[1], 1, lambda t: math.exp(-rate*t))
            self.line(a[1], 2, lambda t: math.exp(-rate*t))
        else:
            loss, p, cost = k["wrong_loss"], k["wrong_chance"], k["look_cost"]
            self.bars(a[0], [p*loss, cost]); self.line(a[1], 0, lambda q: q*loss)
            self.line(a[1], 1, lambda q: cost)

    def check_19(self, d, k, f):
        a = f.axes
        task_means = [(30.44,20.03), (23.06,9.06), (20.15,5.71), (147.34,146.89), (108.73,106.32)]
        losses = [(diag-off)/diag for diag, off in task_means]
        if d == "01":
            index = ["small2","small3","small4","gathering","pathfinding"].index(k["task"])
            if k["view"] == "means":
                self.bars(a[0], list(task_means[index])); self.bars(a[1], losses)
            elif index >= 3:
                self.bars(a[1], losses)
            else:
                vals = [[34.2,14.7,5.5], [62.5,27,8.2], [71.7,11.8,15]][index]
                self.bars(a[0], vals)
                self.bars(a[1], [30.44,28.20,20.03,26.63] if index == 0
                          else [36.5,54.3] if index == 1 else [59.9,56.7])
        elif d == "02":
            # Independently replay the three-action zero-sum cycle: B beats A, C beats B, A beats C.
            action = {"A":0,"B":1,"C":2}; mine = other = action[k["start"]]
            one_x, one_y, two_x, two_y = [], [], [0], [other]
            for t in range(1,k["updates"]+1):
                if t%2: mine=(other+1)%3; one_x.append(t); one_y.append(mine)
                else: other=(mine+1)%3; two_x.append(t); two_y.append(other)
            self.equal(a[0].lines[0].get_xdata(), two_x); self.equal(a[0].lines[0].get_ydata(), two_y)
            self.equal(a[0].lines[1].get_xdata(), one_x); self.equal(a[0].lines[1].get_ydata(), one_y)
            self.bars(a[1], [1]*k["updates"]); self.line(a[1],0,lambda t:0)
        elif d == "03":
            losses = [71.7,24.6,15.6,15]
            self.equal(a[0].lines[0].get_ydata(), losses)
            expected = losses if k["view"] == "loss" else [0,47.1,56.1,56.7] if k["view"] == "reduction" else [47.1,9,.6]
            self.bars(a[1], expected)
        else:
            matrix = [[.95,.2],[.4,.9]] if k["matrix"] == "two" else [[1,0,0],[.6,.6,.6],[0,0,1]]
            weights = ({"target":[.5,.5],"changed":[.9,.1],"tie":[.56,.44],"known":[1,0]} if len(matrix)==2
                       else {"target":[.2,.6,.2],"changed":[.5,0,.5],"tie":[.6,0,.4],"known":[1,0,0]})[k["mix"]]
            values = [sum(x*w for x,w in zip(row,weights)) for row in matrix]
            self.bars(a[1], [matrix[i][i] for i in range(len(matrix))]+values)
            self.equal(a[0].images[0].get_array(),matrix)

    def check_20(self, d, k, f):
        a = f.axes
        if d == "01":
            # Run-chain indistinguishability propagates lack of delivery knowledge one level each.
            n = k["delivered"]
            for level in range(1,6):
                holds = k["fact"] == "clock" or level < n
                self.cell(a[1], level, 0, "holds" if holds else "fails")
            self.cell(a[1],6.6,0,"holds" if k["fact"] == "clock" else "fails")
        elif d == "02":
            for run in range(4):
                ar, br = run//2 >= k["a_needs"], (run+1)//2 >= k["b_needs"]
                self.cell(a[0],run,2,"attacks" if ar else "holds")
                self.cell(a[0],run,1,"attacks" if br else "holds")
        elif d == "03":
            for run in range(4):
                if k["policy"] == "private":
                    self.cell(a[1],run,2,"releases" if run//2>=1 else "keeps")
                    self.cell(a[1],run,1,"takes" if (run+1)//2>=2 else "waits")
                else:
                    self.cell(a[1],run,2,"to B" if k["policy"] == "escrow_seen" else "to A")
        else:
            drop, r = k["drop"], k["rounds"]
            missed = 1-(1-drop)**2
            agreement = lambda n: 1-missed**n+drop**n
            ack = lambda n: 1 if drop==0 else 0
            self.bars(a[0],[agreement(r),1-missed**r,ack(r),missed**r-drop**r],horizontal=True)
            self.line(a[1],0,agreement); self.line(a[1],1,ack)

    @staticmethod
    def network(d, overhead=0, optimum=False):
        z = min(d,max(0,1-overhead-d)) if optimum else min(d,max(0,2*(1-overhead)-d))
        x=(d-z)/2
        return z, 2*(x+z)**2+2*x+overhead*z

    def check_21(self, d, k, f):
        a=f.axes
        if d=="01":
            demand=k["demand"]
            if k["network"]=="link":
                self.line(a[0],0,lambda z:(demand+z)/2+1)
                self.line(a[0],1,lambda z:demand+z)
                self.line(a[1],0,lambda z:2*((demand+z)/2)**2+demand-z)
            else:
                self.line(a[0],0,lambda q:1+q); self.line(a[0],1,lambda q:1+demand-q)
                self.line(a[1],0,lambda q:q*(1+q)+(demand-q)*(1+demand-q))
        elif d=="02":
            o=k["overhead"]
            self.line(a[0],0,lambda dem:self.network(dem,o)[1]/self.network(dem,o,True)[1])
            self.line(a[1],0,lambda dem:self.network(dem,o)[0]); self.line(a[1],1,lambda dem:self.network(dem,o,True)[0])
        elif d=="03":
            demand=k["demand"]
            z=min(demand,max(0,1-demand)) if k["rule"]=="marginal" else min(demand,max(0,2*(1-{"none":0,"toll":.5,"toll49":.49}.get(k["rule"],0))-demand))
            self.bars(a[1],[(demand-z)/2,(demand-z)/2,z])
            self.line(a[0],0,lambda q:q); self.line(a[0],1,lambda q:2*q); self.line(a[0],2,lambda q:1)
        else:
            rate=k["rate"]; eq=self.network(rate)[1]
            self.line(a[0],0,lambda dem:self.network(dem,optimum=True)[1])
            self.line(a[1],0,lambda g:1/g); self.line(a[1],1,lambda g:eq/self.network((1+g)*rate,optimum=True)[1])

    def check_22(self, d, k, f):
        a=f.axes
        if d=="01":
            pol={"table":[(8,.5),(12,1.5)],"workbench":[(7,.5),(11,2)],"transfer":[(20,.01),(-1,0)]}[k["case"]]
            self.bars(a[1],[r-k["penalty"]*risk for r,risk in pol],horizontal=True)
            # line 0 is the risk limit, line 1 joins the policy endpoints.
            for line,(reward,risk) in zip(a[0].lines[2:4],pol):
                self.equal(line.get_xdata(),[risk]); self.equal(line.get_ydata(),[reward])
        elif d=="02":
            g=k["discount"]
            self.line(a[1],0,lambda delta:math.sqrt(2*delta)*g*.1/(1-g)**2)
        elif d=="03":
            alpha=k["alpha"]
            self.line(a[0],0,lambda z:z+(.01*max(100-z,0)+.99*max(-z,0))/(1-alpha))
            remaining=k["budget"]
            expected=[]
            for charge in (.04,.05,.03,.05):
                expected.extend([remaining,charge])
                if charge<=remaining+1e-12:remaining-=charge
            self.bars(a[1],expected)
        else:
            risks=[.3,.05,.2,0]; rewards=[10,5,8,0]
            self.bars(a[1],[r-k["penalty"]*p for r,p in zip(rewards,risks)],horizontal=True)
            for line,r,p in zip(a[0].lines[1:],rewards,risks):
                self.equal(line.get_xdata(),[p]); self.equal(line.get_ydata(),[r])

    def check_23(self, d, k, f):
        a=f.axes
        if d=="01":
            parent=[1,1,1,k["grant"]=="browser",0,0]
            child=parent.copy()
            if k["grant"]=="narrow":child[2]=0
            # Every membership box has a hatch exactly when the capability is absent.
            self.assertEqual([p.get_hatch() is None for p in a[0].patches[:12]], [bool(x) for x in parent+child])
        elif d=="02":
            levels={"approved":[0,1,1],"claim":[0,0,0],"revoked":[0,1,0],"replaced":[0,1,0]}[k["scenario"]]
            self.equal(a[0].lines[0].get_ydata(),levels); self.equal(a[0].lines[1].get_ydata(),levels)
        elif d=="03":
            fields={"none":[True]*3,"version":[True,False,True],"recipient":[True,True,False],"document":[False,True,True]}[k["changed"]]
            for i,match in enumerate(fields):
                word="matches" if k["source"]=="laundered" or match else "differs"
                if k["source"]=="sentence":word="would match" if match else "would differ"
                self.cell(a[0],i+.5,0,word)
        else:
            attacks=[.05,.10,k["deputy"]]+([.45] if k["family"]=="four" else [])
            self.bars(a[0],attacks)
            expected={"default":[1,0,1,1],"changed":[1,2,1,0],"transfer":[0,0,1,1]}[k["trace"]]
            self.bars(a[1],expected,horizontal=True)

    def check_24(self, d, k, f):
        a=f.axes
        if d=="01":
            case,reading=k["case"],k["reading"]
            if case=="aged":
                if reading=="scores":self.bars(a[0],[.4,1,.52])
                elif reading=="gap":self.bars(a[0],[.4,.12])
                else:self.line(a[0],0,lambda s:.4+.6*s)
            elif reading=="scores":
                expected={"book":[.8,.73],"lab":[.5,.75],"transfer":[1,0]}[case]
                self.bars(a[0],expected)
                intervals=[]
                for rate in expected:
                    n=400 if case=="book" else 4 if case=="lab" else 1
                    if case=="book":
                        half=1.96*math.sqrt(rate*(1-rate)/n)
                        intervals.append([rate-half,rate+half])
                    else:
                        z=1.959963984540054
                        den=1+z*z/n
                        center=(rate+z*z/(2*n))/den
                        half=z*math.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/den
                        intervals.append([max(0,center-half),min(1,center+half)])
                observed=[col.get_segments()[0][:,1] for col in a[0].collections if hasattr(col,"get_segments")]
                self.equal(observed,intervals)
            elif case=="lab" and reading=="gap":
                self.line(a[0],0,lambda x:.25)
                for i,value in enumerate((0,1,0,0)):
                    self.equal(a[0].lines[2+2*i].get_ydata(),[0,value])
                    self.equal(a[0].lines[3+2*i].get_ydata(),[value])
            elif case=="lab" and reading=="weights":
                self.bars(a[0],[1,1,0,.5]); self.bars(a[1],[.5,.75,.1,.55])
            elif case=="book" and reading=="gap":
                observed=[col.get_segments()[0][:,0] for col in a[0].collections if hasattr(col,"get_segments")]
                expected=[]
                for n in (100,400,1600):
                    half=1.96*math.sqrt((.8*.2+.73*.27)/n)
                    expected.append([.07-half,.07+half])
                self.equal(observed,expected)
            elif case=="transfer":
                for row in range(2):
                    for col in range(2):
                        self.cell(a[0],col+.5,row+.5,"observed" if row+col==1 else "missing")
            else:
                self.assertTrue(any("undefined" in t.get_text().lower() or "missing" in t.get_text().lower() or "not" in t.get_text().lower()
                                    for ax in a for t in ax.texts))
        elif d=="02":
            scores=[.04,.09,.17,.30,.46,.58,.66,.71]
            self.equal(a[0].lines[0].get_ydata(),scores)
            self.line(a[0],1,lambda x:scores[int(x)-1])
            self.line(a[0],2,lambda x:k["threshold"])
            members={"all":list(range(1,9)),"odd":[1,3,5,7],"even":[2,4,6,8]}[k["tested"]]
            self.bars(a[1],[int(scores[m-1]>=k["threshold"]) for m in members])
        elif d=="03":
            margin=math.sqrt(math.log(k["tested"]/.05)/(2*k["tasks"]))
            expected=[]
            for rate in [.6,.68,.72,.74][:k["tested"]]:expected.extend([rate-margin,margin])
            self.bars(a[0],expected,horizontal=True)
        else:
            n=k["runs"]
            if k["bank"]=="recorded":
                subsets=list(itertools.combinations([1,1,1,0],n))
                all_=sum(all(s) for s in subsets)/len(subsets); any_=sum(any(s) for s in subsets)/len(subsets);mean=.75
            else:
                lo,hi={"0.50":(.5,.5),"0.20":(.2,.8),"0.10":(.1,.9)}[k["bank"]]
                all_=(lo**n+hi**n)/2; any_=1-((1-lo)**n+(1-hi)**n)/2; mean=.5
            self.bars(a[0],[all_,mean**n,any_,1-(1-mean)**n])

    def check_25(self, d, k, f):
        a=f.axes
        if d=="01":
            costs={"steady":[.80,.82,.81,.83,.82,.84,.83,.82],"creeping":[.80,.83,.86,.89,.92,.95,.98,1.01],
                   "spike":[.80,.81,.95,.82,.81,.80,.82,.81]}[k["trace"]]
            self.equal(a[0].lines[0].get_ydata(),costs)
            self.line(a[0],1,lambda t:.9 if k["rule"]=="declared" else 1)
        elif d=="02":
            case=k["case"]
            self.bars(a[0],[1] if case=="transfer" else [1,.75])
            base=[0,1] if case=="transfer" else [1,0,1,0]
            proposed=[1,1] if case=="transfer" else [1,1,1,0] if case=="changed" or k["chooser"]=="guard" else [1,0,1,0]
            for j,(b,c) in enumerate(zip(base,proposed)):
                self.cell(a[1],j+.5,2.5,"pass" if b else "fail")
                self.cell(a[1],j+.5,1.5,"pass" if c else "fail")
                self.cell(a[1],j+.5,.5,f"{c-b:+d}" if c!=b else "0")
        elif d=="03":
            def tail(n):
                # Exact fair-coin enumeration by binomial count, independent of production implementation.
                return sum(math.comb(int(n),s) for s in range(math.ceil(.625*n),int(n)+1))/2**int(n)
            self.line(a[0],0,lambda n:math.exp(-n*.25**2/2)); self.line(a[0],1,tail)
            covered=k["decisions"] if k["redesign"]=="never" else min(2,k["decisions"])
            if covered>1:self.line(a[0],5,lambda n:covered*math.exp(-n*.25**2/2))
        else:
            cost=.95 if k["others"]=="cost" else .8
            self.bars(a[0],[k["uplift"],cost])
            flags=[k["uplift"]>=.25,cost<=.9,k["others"]!="authority",k["others"]!="rollback"]
            flags.append(all(flags))
            self.assertEqual([p.get_hatch() is None for p in a[1].patches],flags)

    def check_26(self, d, k, f):
        a=f.axes
        if d=="01":
            counts={"chapter":[2],"low":[8,8,0,0],"high":[3,3,2,2]}[k["pool"]];n=k["subset"]
            subsets=list(itertools.combinations(range(10),n))
            exact=[sum(any(i<c for i in sub) for sub in subsets)/len(subsets) for c in counts]
            plug=[1-(1-c/10)**n for c in counts]
            self.bars(a[0],exact); self.bars(a[1],[sum(exact)/len(counts),sum(plug)/len(counts),sum(counts)/10/len(counts)])
            self.equal([line.get_ydata()[0] for line in a[0].lines],plug)
        elif d=="02":
            matrix,weights,chosen,oracle,denied={
                "diag":([[1,0,0],[0,1,0],[0,0,1]],[.2,.3,.5],[0,0,0],[0,1,2],[1,1,0]),
                "prefix":([[1,0,0],[0,1,0]],[.2,.3,.5],[0,0,0],[0,1,0],[1,1,0]),
                "xfer":([[1,1],[1,0]],[.5,.5],[1,1],[0,0],[1,0])}[k["bank"]]
            if k["selector"]!="notebook":chosen=oracle
            allowed=[1]*len(weights) if k["deploy"]=="all" else denied
            coverage=sum(w for t,w in enumerate(weights) if any(row[t] for row in matrix))
            selection=sum(w for t,w in enumerate(weights) if matrix[chosen[t]][t])
            deployed=sum(w for t,w in enumerate(weights) if matrix[chosen[t]][t] and allowed[t])
            expected=[coverage,selection]
            if coverage>selection:expected.append(coverage-selection)
            expected.append(deployed)
            if selection>deployed:expected.append(selection-deployed)
            self.bars(a[1],expected)
        elif d=="03":
            sel,cov={"codexs":(44.5,77.5),"codex12":(28.81,72.31),"near":(78,80),"low":(15,20)}[k["point"]]
            self.equal(a[0].lines[1].get_xdata(),[cov]); self.equal(a[0].lines[1].get_ydata(),[sel])
            if k["share"]>0:
                self.equal(a[0].lines[3].get_ydata(),[sel+k["share"]*(cov-sel)])
        else:
            fits={family:independent_fit(family) for family in ("exp","hyp","power")}
            for index,family in enumerate(("exp","hyp","power")):
                self.line(a[0],index*2,fits[family][1]); self.line(a[0],index*2+1,lambda x, fam=family:fits[fam][0])
            curve=fits["power" if k["family"]=="pow" else k["family"]][1]; selector=.6 if k["selector"]=="near" else .3
            self.bars(a[1],[curve(100)-.63,.63-selector])

    def check_27(self, d, k, f):
        a=f.axes
        if d=="01":
            model,expert={"chapter":(.78,.95),"general":(.78,.6),"bench":(.8,.95),"tie":(.78,.78)}[k["case"]]
            act=20*model-10; gross=20*expert-10
            self.bars(a[0],[expert,model],horizontal=True)
            self.bars(a[1],[act,k["timely"]*gross+(1-k["timely"])*2-1])
        elif d=="02":
            self.bars(a[0],[-1,.35*8.04-.65-1,2,.95*8.04-.05*4-k["hold_cost"]-1],horizontal=True)
        elif d=="03":
            lam,mu={"default":(4,3),"fast":(4,4),"transfer":(1,2)}[k["case"]]
            self.line(a[0],0,lambda fraction:1/(mu-lam*fraction))
            fraction=k["delegation_fraction"]
            stable=lam*fraction<mu
            mean=1/(mu-lam*fraction) if stable else math.inf
            tasks=[(False,True,True,.5)] if k["case"]=="transfer" else [(True,False,False,2),(False,True,True,2),(False,True,False,2)]
            for row,(autonomous,human,received,deadline) in enumerate(tasks):
                needs=not autonomous
                timely=stable and mean<=deadline
                released=autonomous or human and received and timely
                values=["no" if autonomous else "yes", "n/a" if autonomous else "yes" if human else "no",
                        "n/a" if autonomous else "yes" if received else "no",
                        "n/a" if autonomous else "yes" if timely else "no", "yes" if released else "no"]
                for col,word in enumerate(values):self.cell(a[1],col+.5,len(tasks)-row-.5,word)
        else:
            self.line(a[0],0,lambda q:10*q); self.line(a[0],1,lambda q:2)
            bad={"none":None,"late":1,"changed":2,"failed":3}[k["gap"]]
            for i in range(4):self.cell(a[1],i+.5,.5,"NOT\nauthorized" if i==bad else "fallback\nauthorized")


if __name__ == "__main__":
    unittest.main()
