"""Independent plotted-coordinate checks for every reader state in Chapters 1–14.

The production functions supply the figures under test. Expected coordinates
come from declared teaching constants, analytic formulas, explicit enumeration,
or independent arithmetic helpers in the chapter tests. Production metrics are
never used as expected values. Decorative connectors are not mathematical data.
"""
from __future__ import annotations

from functools import lru_cache
import importlib.util
import itertools
import math
from pathlib import Path
import sys
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LAB = Path(__file__).resolve().parent.parent
for _path in (LAB / "src", LAB / "tools/readers/engine"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


@lru_cache(None)
def load(n, tests=False):
    path = LAB / (f"tests/test_readers_ch{n:02}.py" if tests else f"tools/readers/chapters/ch{n:02}.py")
    spec = importlib.util.spec_from_file_location(f"plot_oracle_{'test' if tests else 'reader'}_{n}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entropy(p):
    return 0.0 if p in (0, 1) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def information_value(b, observation, rewards):
    """Unnormalized observation/action enumeration avoids copying Bayes' code."""
    now = max(sum(x * r for x, r in zip(b, row)) for row in rewards)
    future = sum(max(sum(b[s] * observation[s][o] * row[s] for s in range(len(b)))
                     for row in rewards) for o in range(len(observation[0])))
    return future - now


@lru_cache(None)
def random_walk_oracle():
    """Forward lambda-return targets, independent of production trace equations.

    Both repeated presentation and the per-episode update use frozen values.
    Repeated presentation solves visitwise target identities; one presentation
    accumulates forward target errors before updating at the episode boundary.
    """
    rng = np.random.default_rng(0)
    sets = []
    for _ in range(100):
        train = []
        for _ in range(10):
            s, sequence = 3, []
            while s not in (0, 6):
                sequence.append(s - 1)
                s += 1 if rng.random() < 0.5 else -1
            train.append((sequence, float(s == 6)))
        sets.append(train)
    lambdas = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    truth = np.array([1/6, 2/6, 3/6, 4/6, 5/6])
    results = {"repeated": {}, "once": {}}
    for lam in lambdas:
        errors, training = [], []
        for train in sets:
            matrix, rhs = np.zeros((5, 5)), np.zeros(5)
            visited = sorted({s for sequence, _ in train for s in sequence})
            for sequence, terminal in train:
                coefficients, constant = np.zeros(5), terminal
                for t in reversed(range(len(sequence))):
                    s = sequence[t]
                    if t < len(sequence) - 1:
                        coefficients = lam * coefficients
                        coefficients[sequence[t + 1]] += 1 - lam
                        constant *= lam
                    matrix[s, s] += 1
                    matrix[s] -= coefficients
                    rhs[s] += constant
            values = np.full(5, 0.5)
            values[visited] = np.linalg.solve(matrix[np.ix_(visited, visited)], rhs[visited])
            errors.append(float(np.sqrt(np.mean((values - truth) ** 2))))
            training.append(float(np.sqrt(np.mean([(values[s] - terminal) ** 2
                            for sequence, terminal in train for s in sequence]))))
        results["repeated"][lam] = {"error": float(np.mean(errors)), "train": float(np.mean(training)),
                                    "se": float(np.std(errors) / 10)}
        alternatives = []
        for alpha in [round(i * 0.05, 2) for i in range(13)]:
            errors = []
            for train in sets:
                values = np.full(5, 0.5)
                for sequence, terminal in train:
                    increments, target = np.zeros(5), terminal
                    for t in reversed(range(len(sequence))):
                        if t < len(sequence) - 1:
                            target = (1 - lam) * values[sequence[t + 1]] + lam * target
                        increments[sequence[t]] += target - values[sequence[t]]
                    values += alpha * increments
                errors.append(float(np.sqrt(np.mean((values - truth) ** 2))))
            alternatives.append((float(np.mean(errors)), alpha, float(np.std(errors) / 10)))
        error, alpha, se = min(alternatives)
        results["once"][lam] = {"error": error, "alpha": alpha, "se": se}
    return results


class ReaderPlotOracles(unittest.TestCase):
    def equal(self, actual, expected):
        np.testing.assert_allclose(np.asarray(actual, float), np.asarray(expected, float), rtol=1e-10, atol=1e-11)

    def line(self, ax, x, y):
        """Find the specified mathematical data line independently of its color."""
        x, y = np.asarray(x, float), np.asarray(y, float)
        for line in ax.lines:
            lx, ly = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
            if lx.shape == x.shape and ly.shape == y.shape and np.allclose(lx, x, rtol=1e-10, atol=1e-11) and np.allclose(ly, y, rtol=1e-10, atol=1e-11):
                return
        self.fail(f"Missing independently computed curve: x={x.tolist()[:8]}, y={y.tolist()[:8]}")

    def relation(self, ax, fn, minimum_points=10):
        for line in ax.lines:
            x = np.asarray(line.get_xdata(), float)
            y = np.asarray(line.get_ydata(), float)
            if len(x) >= minimum_points and np.allclose(y, np.asarray([fn(v) for v in x]), rtol=1e-10, atol=1e-11):
                return
        self.fail("No plotted line satisfies the independently derived relation")

    def heights(self, ax, values):
        self.equal([p.get_height() for p in ax.patches], values)

    def opaque_label_inside_figure(self, fig, label):
        patch=label.get_bbox_patch()
        self.assertIsNotNone(patch)
        self.assertEqual(tuple(patch.get_facecolor()),(1,1,1,1))
        renderer=fig.canvas.get_renderer()
        box=label.get_window_extent(renderer)
        frame=fig.bbox
        self.assertGreaterEqual(box.x0,frame.x0)
        self.assertGreaterEqual(box.y0,frame.y0)
        self.assertLessEqual(box.x1,frame.x1)
        self.assertLessEqual(box.y1,frame.y1)

    def test_ch09_d03_signed_drops_and_labels_are_visible_in_every_state(self):
        module = load(9)
        demo = module.CHAPTER["demos"][2]
        for values in itertools.product(*(control["values"] for control in demo["controls"])):
            controls = {control["key"]: value for control, value in zip(demo["controls"], values)}
            with self.subTest(controls=controls):
                fig, *_ = module.consistency_picture(**controls)
                try:
                    fig.canvas.draw()
                    axis = fig.axes[0]
                    for bar in axis.patches:
                        endpoints = [bar.get_y(), bar.get_y() + bar.get_height()]
                        self.assertGreaterEqual(min(endpoints), axis.get_ylim()[0])
                        self.assertLessEqual(max(endpoints), axis.get_ylim()[1])
                    renderer = fig.canvas.get_renderer()
                    for label in axis.texts:
                        box = label.get_window_extent(renderer)
                        self.assertGreaterEqual(box.y0, axis.bbox.y0)
                        self.assertLessEqual(box.y1, axis.bbox.y1)
                    for bar, label in zip(axis.patches[:2], axis.texts[:2]):
                        if bar.get_height() < 0:
                            self.assertLess(label.get_position()[1], bar.get_y() + bar.get_height())
                finally:
                    plt.close(fig)

    def test_ch13_d02_outcome_labels_mask_mean_line_in_every_state(self):
        module=load(13);demo=module.CHAPTER["demos"][1]
        for values in itertools.product(*(c["values"] for c in demo["controls"])):
            kw={c["key"]:v for c,v in zip(demo["controls"],values)}
            with self.subTest(controls=kw):
                fig,*_=module.retrieve_picture(**kw)
                try:
                    fig.canvas.draw()
                    labels=fig.axes[1].texts
                    self.assertEqual(len(labels),4)
                    for label in labels:
                        self.opaque_label_inside_figure(fig,label)
                        self.assertGreater(label.get_zorder(),fig.axes[1].lines[0].get_zorder())
                finally:plt.close(fig)

    def test_ch14_d02_curve_descriptions_mask_curve_in_every_state(self):
        module=load(14);demo=module.CHAPTER["demos"][1]
        for values in itertools.product(*(c["values"] for c in demo["controls"])):
            kw={c["key"]:v for c,v in zip(demo["controls"],values)}
            with self.subTest(controls=kw):
                fig,*_=module.bound_picture(**kw)
                try:
                    fig.canvas.draw()
                    labels=[t for t in fig.axes[1].texts if t.get_text() in
                            ("largest possible value R/(1-gamma)","value-error bound")]
                    self.assertEqual(len(labels),1 if kw["case"]=="transfer" else 2)
                    for label in labels:self.opaque_label_inside_figure(fig,label)
                    left_labels=fig.axes[0].texts
                    self.assertEqual(len(left_labels),1 if kw["case"]=="transfer" else 3)
                    for label in left_labels:self.opaque_label_inside_figure(fig,label)
                finally:plt.close(fig)

    def check(self, chapter, demo, kw, fig, metrics, interpretation):
        axes = fig.axes
        if chapter == 1:
            if demo == 1:
                xs, ys = ([1,2,3,4,5], [.42,.46,.49,.52,.56]) if kw["dataset"] == "gradual" else ([10,20,40,80],[.1,.3,.6,.8])
                self.line(axes[0], xs, ys)
                self.line(axes[1], xs, [int(v >= kw["cutoff"]) for v in ys])
            elif demo == 2:
                law = [.45,.35,.20] if kw["law"] == "chapter" else [.30,.30,.40]
                self.heights(axes[0], law)
                accepted = 0 if kw["evaluator"] == "only_a" else 2
                if kw["decoder"] == "attempts":
                    self.line(axes[1], range(1,21), [1-(1-law[accepted])**i for i in range(1,21)])
                else:
                    weights = law if kw["decoder"] == "sample" else [float(i == law.index(max(law))) for i in range(3)]
                    self.heights(axes[1], [v * (i == accepted) for i,v in enumerate(weights)])
            elif demo == 3:
                for n in [5,20,40,100]: self.relation(axes[0], lambda q,n=n:q**n)
                q0,q1 = {"low":(.9,.95),"high":(.95,.99),"wide":(.9,.99)}[kw["step"]]
                n=kw["length"]
                self.heights(axes[1], [1+n*round(q1/q0-1,4),(q1/q0)**n])
            else:
                # This is a categorical diagram, not a numerical curve.
                labels=" ".join(t.get_text() for ax in axes for t in ax.texts)
                for word in ["Scale axis","Metric","Predictor"]: self.assertIn(word.lower(),labels.lower())
        elif chapter == 2:
            if demo == 1:
                cells={"table":(.2,.3,.25,.8),"additive":(.2,.3,.25,.35),"second":(.2,.55,.5,.7),"workbench":(.4,.52,.49,.58)}[kw["case"]]
                if kw["case"]=="workbench" and kw["run"]=="doubled":cells=(*cells[:3],.73)
                if kw["run"]=="cubed":cells=tuple(v**3 for v in cells)
                b,p,i,j=cells
                self.heights(axes[1],[b,p-b,i-b,j-p-i+b,j])
                self.equal([p.get_y() for p in axes[1].patches],[0,b,p,p+i-b,0])
            elif demo == 2:
                b=kw["baseline_b"]
                self.equal([p.get_width() for p in axes[0].patches],[.2,.6,b,.8-b])
                expected=[.45,.77-b] if kw["method"]=="four" else [.25,.77-2*b]
                self.heights(axes[1],expected)
            elif demo == 3:
                self.relation(axes[1],lambda x:.45*(1-x))
            else:
                se=.4/math.sqrt(kw["trials"])
                self.heights(axes[0],[se,math.sqrt(2)*se,2*se])
                # Errorbar horizontal segments carry the actual interval endpoints.
                segments=[s for c in axes[1].collections for s in c.get_segments()]
                for half in (1.96*2*se,1.96*math.sqrt(2)*se):
                    self.assertTrue(any(np.allclose(s[:,0],[kw["true_contrast"]-half,kw["true_contrast"]+half]) for s in segments))
        elif chapter == 3:
            if demo == 1:
                self.relation(axes[0],lambda x:1.5*10**(-.15*x)+1)
                # The independent chapter test's closed-form exponent grid fit.
                b,a,c,forecast=load(3,True).Chapter3ReaderTests().independent_forecast(kw["decades"],kw["runs"])
                # This reader deliberately plots its three-decimal reported constants.
                a,c=round(a,3),round(c,3)
                self.relation(axes[0],lambda x:a*10**(b*x)+c)
                residuals=[]
                for d in range(1,5):
                    _,ad,cd,_=load(3,True).Chapter3ReaderTests().independent_forecast(d,kw["runs"])
                    residuals.append(2.5-round(ad,3)-round(cd,3))
                self.heights(axes[1],residuals)
                self.line(axes[0],[0],[2.5])
            elif demo == 2:
                self.relation(axes[1],lambda x:.01+.095*x)
                self.line(axes[1],[4],[.39])
                self.line(axes[1],[4],[kw["observed"]])
                for c in axes[1].collections:
                    segments=c.get_segments()
                    if any(len(s)==2 and np.allclose(s[:,1],[.39-1/15,.39+1/15]) for s in segments):break
                else:self.fail("Registered interval not plotted at exact endpoints")
            elif demo == 3:
                funcs={"latent":lambda m:.05+.03*(m-1),"jump":lambda m:.1+.1*(m-1),"onset":lambda m:1/(1+math.exp(-2.5*(m-5))),"none":lambda m:.2}
                fn=funcs[kw["profile"]]
                self.line(axes[0],range(1,10),[fn(m) for m in range(1,10)])
                self.line(axes[1],range(1,10),[int(fn(m)>=kw["tau"]) for m in range(1,10)])
            else:
                dx,dy=([1,2,3],[.2,.3,.4]) if kw["data"]=="default" else ([1,2,4],[0,.69314718056,1.38629436112])
                for family in ["linear","log"]:
                    slope,intercept=load(3,True).Chapter3ReaderTests.fit(family,dx,dy)
                    self.relation(axes[0],lambda x,s=slope,b=intercept,f=family:b+s*(math.log(x) if f=="log" else x))
        elif chapter == 4:
            if demo == 1:
                if kw["denied"]=="none":raw=[1,3,4,4];allowed=raw
                elif kw["denied"]=="review_release":raw=[1,3,4,4];allowed=[1,3,3,3]
                elif kw["denied"]=="draft_review":raw=[1,3,4,4];allowed=[1,2,2,2]
                else:raw=[1,2,3];allowed=[1,1,1]
                self.line(axes[1],range(len(raw)),raw);self.line(axes[1],range(len(allowed)),allowed)
            elif demo == 2:
                self.relation(axes[1],lambda p:0 if p<=.5 else 1-((1-p)/p)**2)
                def finite(p):
                    r=1.0
                    for _ in range(4):r=1-(1-p*r)**2
                    return r
                self.relation(axes[1],finite)
            elif demo == 3:
                d=kw["children"]
                self.relation(axes[0],lambda p:1-(1-p*(1-(1-p)**d))**d)
                self.relation(axes[0],lambda p:p*p)
                self.relation(axes[1],lambda p:d*d*p*p)
            else:
                p=.95*.98*kw["grant"]*.8
                self.equal([bar.get_width() for bar in axes[0].patches],[.95,.95*.98,.95*.98*kw["grant"],p])
                self.relation(axes[1],lambda n:(1-p**kw["steps"])**n)
        elif chapter == 5:
            if demo == 1:
                r=kw["request"];blind=(1-r)/2;informed=.9*.85+.1*.1
                success=[blind]*6
                if kw["calls"]==2:
                    success[3]=blind+r*blind;success[4]=blind+r*informed
                    if kw["rejection"]=="blind":success[5]=blind+r*blind
                # Stacked bars: group each row's first two successful segments.
                widths=[p.get_width() for p in axes[0].patches]
                self.equal([sum(widths[i:i+2]) for i in range(0,24,4)],success)
                self.equal([sum(widths[i:i+4]) for i in range(0,24,4)],[1]*6)
            elif demo == 2:
                helper=load(5,True)
                kernel=helper.Chapter5ReaderTests.kernel(kw["system"])
                self.equal(axes[1].images[0].get_array(),kernel)
                for name,start in helper.START.items():
                    matrix=helper.Chapter5ReaderTests.kernel(name);values=[start]
                    for _ in range(30):values.append(values[-1]*matrix[0][0]+(1-values[-1])*matrix[1][0])
                    self.line(axes[0],range(31),values)
            elif demo == 3:
                self.relation(axes[0],lambda p:1-entropy(p))
                a=kw["accuracy"];blind=.3;informed=a*.85+(1-a)*.1
                self.equal([p.get_width() for p in axes[1].patches],[blind,blind,blind+.4*blind,blind+.4*informed])
            else:
                if kw["case"]=="transfer":
                    curves=[[1, .9,.9*.8,.9*.8*.7],[1,.99,.99*.96,.99*.96*.91],[1,.9,.9,.9],[1,.9,.9**2,.9**3]]
                    for values in curves:self.line(axes[0],range(4),values)
                else:
                    p={"p95":.95,"p99":.99,"p999":.999}[kw["case"]]
                    for handling in ["none","retry","shared"]:
                        q=1-(1-p)**2 if handling=="retry" else p
                        self.line(axes[0],range(101),[1]+([q]*100 if handling=="shared" else [q**n for n in range(1,101)]))
        elif chapter == 6:
            if demo == 1:
                u={"book":(0,-400),"lab":(-50,-100),"transfer":(-12,-24)}[kw["table"]][kw["worse"]=="worse"]
                expected=load(6,True).expected_utilities(kw["table"],u)
                for i,v in enumerate(expected):self.line(axes[0],[v],[len(expected)-1-i])
            elif demo == 2:
                self.relation(axes[0],lambda price:97-price)
            elif demo == 3:
                if kw["gamble"]=="petersburg":
                    funcs=[lambda n:sum(2**(-k)*math.sqrt(2**k) for k in range(1,int(n)+1)),lambda n:float(n),lambda n:sum(2**k for k in range(1,int(n)+1))]
                    for fn in funcs:self.relation(axes[0],fn)
                else:
                    probability=.5 if kw["gamble"]=="half" else .8
                    ce={"sqrt":100*probability**2,"linear":100*probability,"square":100*math.sqrt(probability)}[kw["shape"]]
                    level=probability
                    self.line(axes[0],[ce],[level]);self.line(axes[0],[100*probability],[level])
            else:
                wrong,decline=kw["wrong"],kw["decline"]
                self.relation(axes[0],lambda p:p+(1-p)*wrong)
                # Uniform calibrated confidence grid: risk = coverage / 4.
                self.relation(axes[1],lambda coverage:coverage/4)
        elif chapter == 7:
            if demo == 1:
                for g in [.5,.9,.95,.99]:self.relation(axes[0],lambda t,g=g:100*g**t)
            elif demo == 2:
                rel,ver,c,g={"book":(85,97,5,1),"tie":(85,97,12,1),"wb1":(80,95,6,.9),"wb3":(80,95,6,.75)}[kw["scenario"]]
                vals=[(0,3)]
                if kw["stage"]>=1:vals.append((ver,2))
                if kw["stage"]==2:vals.extend([(rel,1),(-c+g*ver,0)])
                for v,y in vals:self.line(axes[0],[v],[y])
            elif demo == 3:
                a,c,big=(2,-1,6) if kw["model"]=="prep" else (1,0,4)
                self.line(axes[0],[1,2,3],[a]*3)
                self.line(axes[0],[1,2,3],[c,c+kw["discount"]*big,c+kw["discount"]*big])
            else:
                g=kw["discount"]
                T=lambda v:[max(85+g*v[2],-5+g*v[1]),97+g*v[2],g*v[2]]
                v=[0,0,0]
                for _ in range(kw["stage"]):v=T(v)
                self.heights(axes[0],v+T(v)+T(T([0,0,0])))
        elif chapter == 8:
            if demo == 1:
                T=np.array([[.1,.9,0,0],[.1,0,.9,0],[0,.1,0,.9],[0,0,.1,.9]])
                if kw["case"] in ("move1","move2"):
                    b=np.array([1/3,1/3,0,1/3]);likelihood=np.array([1,1,0,1])
                    if kw["case"]=="move2":b=b@T*likelihood;b/=sum(b)
                elif kw["case"]=="default":b=np.array([.5,.5]);T=np.eye(2);likelihood=np.array([.9,.1])
                else:b=np.array([.8,.2]);T=np.array([[.7,.3],[.2,.8]]);likelihood=np.array([.2,.7])
                pred=b@T;post=pred*likelihood;post/=sum(post)
                expected=list(b)
                if kw["stage"]>=1:expected+=list(pred)
                if kw["stage"]==2:expected+=list(post)
                self.heights(axes[0],expected)
            elif demo == 2:
                tp,fp={"run03":(1,.03),"run30":(1,.3),"sensor":(.9,.1),"aliased":(.5,.5)}[kw["kernel"]]
                self.relation(axes[0],lambda p:p*tp/(p*tp+(1-p)*fp))
            elif demo == 3:
                rows={"alpha":[(4,1),(0,3)],"auth":[(4,-12),(0,0)],"fmt":[(4,-12),(0,0)],"detour":[(100,0),(97,97)]}[kw["setting"]]
                for a,b in rows:self.relation(axes[0],lambda p,a=a,b=b:a*p+b*(1-p))
                self.relation(axes[0],lambda p:max(a*p+b*(1-p) for a,b in rows))
            else:
                obs,rewards={"tool":([[.9,.1],[.15,.85]],[[10,-40],[0,0]]),"default":([[.9,.1],[.1,.9]],[[10,-10],[-10,10]]),"changed":([[.5,.5],[.5,.5]],[[10,-10],[-10,10]]),"transfer":([[.8,.2],[.3,.7]],[[5,-4],[0,2]])}[kw["case"]]
                self.relation(axes[0],lambda p:information_value([p,1-p],obs,rewards))
        elif chapter == 9:
            if demo == 1:
                # Independently calculated g records after the selected expansion.
                tables={"fig91":[[0,3,7],[0,3,6,5],[0,3,6,5],[0,3,6,5]],"zero":[[0,1,1],[0,1,1,10],[0,1,1,10,25],[0,1,1,10,25]],"flow":[[0,1],[0,1,3],[0,1,3,7],[0,1,3,7]]}
                gs=tables[kw["trace"]][kw["step"]-1]
                hs=[2,1,1,0] if kw["trace"]=="flow" else [0]*len(gs)
                expected=[]
                for g,h in zip(gs,hs):
                    expected.append(g)
                    if h>0:expected.append(h)
                self.heights(axes[0],expected)
            elif demo == 2:
                g={"tworoute":1,"notebook":2,"transfer":2}[kw["case"]]
                self.relation(axes[0],lambda h:g+h)
            elif demo == 3:
                self.heights(axes[0],[kw["h_start"]-kw["h_upper"],kw["h_start"]-5,6,3])
                self.heights(axes[1],[6+kw["h_upper"],8])
            else:
                e_i,e_z,calls=(3,3,4) if kw["graph"]=="workflow" else (2,3,4)
                self.heights(axes[1],[200*e_i,200*e_z,kw["price"]*calls,0])
        elif chapter == 10:
            if demo == 1:
                patches=axes[0].patches
                for x in range(1,9):
                    actual=sum(1 for p in patches if abs(p.get_y()+p.get_height()/2-x)<1e-10 and not p.get_hatch())
                    expected=0 if x<kw["min_records"] else (x-kw["stop_at"] if 0<kw["stop_at"]<x else x)
                    self.assertEqual(actual,expected)
            elif demo == 2:
                g,n=kw["gamma"],kw["duration"]
                self.heights(axes[1],[g**t for t in range(5)]+[g**n,g])
            elif demo == 3:
                length=6+(3 if kw["source"]=="changed" else 0)
                expected=max(length,kw["audit_minutes"]) if kw["mode"]=="parallel" else length+kw["audit_minutes"]
                actual=max(p.get_x()+p.get_width() for p in axes[0].patches)
                self.assertAlmostEqual(actual,expected)
            else:
                g=kw["gamma"]
                if kw["case"]=="transfer":values=[4*g+8*g**2,0]
                else:
                    count={"none":3,"two":2,"one":1}[kw["case"]]
                    values=[sum(g**t*r for t,r in enumerate([-1,-1,8][:count]))+(g**3*2 if count==3 else 0),1]
                for x,v in zip([0,1.9],values):self.line(axes[0],[x-.25,x+.25],[v,v])
        elif chapter == 11:
            if demo == 1:
                means,seed,base={"book":([.78,.90],11,1000),"default":([.4,.7],7,120),"swapped":([.7,.4],7,120),"three":([.2,.5,.8],19,90)}[kw["world"]]
                rounds=base*(10 if kw["scale"]=="ten" else 1)
                self.line(axes[0],range(1,rounds+1),[(max(means)-sorted(means)[-2])*t for t in range(1,rounds+1)])
                self.line(axes[0],range(1,rounds+1),[(max(means)-sum(means)/len(means))*t for t in range(1,rounds+1)])
                expected=[]
                for policy in ["greedy","ucb","thompson"]:expected+=load(11,True).replay(means,rounds,seed,policy)[0]
                self.equal([p.get_width() for p in axes[1].patches[:len(expected)]],expected)
            elif demo == 2:
                c=kw["c"];s=kw["situation"]
                if s in ("p4","p5"):
                    pulls=4 if s=="p4" else 5;counts=[0,0];wins=[0,0]
                    for pull in range(1,pulls):
                        a=counts.index(0) if 0 in counts else max(range(2),key=lambda i:wins[i]/counts[i]+c*math.sqrt(math.log(pull-1)/counts[i]))
                        wins[a]+=(1-counts[a]%2) if a==0 else counts[a]%2;counts[a]+=1
                    t=pulls-1;means=[wins[i]/counts[i] for i in range(2)]
                else:t,counts,means=(20,[18,2],[14/18,0]) if s=="trap" else (100,[80,20],[.7,.6])
                self.heights(axes[0],[v for i in range(2) for v in [means[i],c*math.sqrt(math.log(t)/counts[i])]])
            elif demo == 3:
                p,a=kw["prior"],kw["accuracy"]
                masses=[p*a+(1-p)*(1-a),p*(1-a)+(1-p)*a]
                posterior=[p*a/masses[0],p*(1-a)/masses[1]]
                before=entropy(p);after=sum(q*entropy(b) for q,b in zip(masses,posterior))
                self.heights(axes[0],[before,after,before-after]);self.heights(axes[1],[100*b for b in posterior])
            else:
                shift=kw["shift"];values=[75+shift,90+shift,85+shift]
                self.heights(axes[0],[v for y in values for v in [y,92]])
        elif chapter == 12:
            if demo == 1:
                helper=load(12,True);case=kw["case"];initial=helper.RUNS[case]["v"]
                o,d,tr=helper.values_after(case,kw["passes_done"]);shown=helper.RUNS[case]["states"][:-1]
                expected=[o[s]-initial[s] for s in shown]+[d[s]-initial[s] for s in shown]
                if helper.RUNS[case]["lam"]>0:expected += [tr[s]-initial[s] for s in shown]
                self.equal([p.get_height() for p in axes[0].patches[:len(expected)]],expected)
            elif demo == 2:
                b=(kw["ones_in_b_only"]+kw["a_final"])/8
                self.heights(axes[0],[kw["a_final"],b,b,b])
            elif demo == 3:
                lam=kw["lam"];self.heights(axes[0],[(1-lam)*lam**k for k in range(7)]+[lam**7])
                oracle=random_walk_oracle()[kw["protocol"]]
                lambdas=[0,.1,.3,.5,.7,.9,1]
                self.line(axes[1],lambdas,[oracle[l]["error"] for l in lambdas])
                if kw["protocol"]=="repeated":self.line(axes[1],lambdas,[oracle[l]["train"] for l in lambdas])
                self.assertAlmostEqual(float(metrics["Random-walk error at this lambda"]),oracle[lam]["error"],delta=.00051)
                if kw["protocol"]=="once":
                    self.assertEqual(float(metrics["Best step size at this lambda"]),oracle[lam]["alpha"])
                    best=min(lambdas,key=lambda l:oracle[l]["error"])
                    self.assertIn(f"{oracle[best]['se']:.3f}",interpretation)
                else:self.assertIn(f"{oracle[1]['se']:.3f}",interpretation)
            else:
                self.heights(axes[0],[-.02,kw["successor"],-.2,-.02+kw["successor"]-.2])
                self.heights(axes[1],[.6,.4,.5+.5*kw["alpha"]-.1])
        elif chapter == 13:
            if demo == 1:
                rewards=[-.05,0,1] if kw["stream"]=="release" else [1,2]
                returns=[sum(kw["gamma"]**(k-t)*rewards[k] for k in range(t,len(rewards))) for t in range(len(rewards))]
                self.heights(axes[0],rewards+returns);self.heights(axes[1],[.4,1.2*kw["tool_mask"]])
            elif demo == 2:
                self.relation(axes[0],lambda phi:.55+.2/(1+math.exp(-phi)))
                p=1/(1+math.exp(-kw["phi"]));v=.55+.2*p
                gs=[]
                for action,ret in [(0,0),(0,1),(1,-.05),(1,.95)]:
                    b=0 if kw["baseline"]=="none" else (v if kw["baseline"]=="expected" else (.75 if action else .55))
                    gs.append((1-p if action else -p)*(ret-b))
                self.heights(axes[1],gs)
            elif demo == 3:
                cases={"default":([1,2],[.9,.2],[0,0],[3,11],.08,120),"changed":([2,1],[.9,.2],[0,0],[3,11],.08,120),"transfer":([0,1],[0,1],[2,0],[7,17],.1,100),"story":([.63,.73,.95],[.55,.8,0],[0,0,0],[3,11],.08,120)}
                rewards,success,pots,seeds,lr,n=cases[kw["scenario"]];n={"short":10,"case":n,"long":400}[kw["length"]]
                shaped=[a+b for a,b in zip(rewards,pots)]
                runs=[load(13,True).reinforce_final(shaped,seed,lr,n,trace=True) for seed in seeds]
                policies=[p for p,_ in runs]
                for _,history in runs:self.line(axes[0],range(1,n+1),history)
                self.heights(axes[1],[sum(success)/len(success)]+[sum(a*b for a,b in zip(p,success)) for p in policies])
            else:
                e,tr,d=kw["evidence_potential"],kw["retrieve_end_potential"],kw["direct_end_potential"]
                self.heights(axes[0],[-.05,1,-.05+e,1+tr-e]);self.heights(axes[1],[.55,.75,.55+d,.75+tr])
        else:
            if demo == 1:
                self.heights(axes[0],[2086,2060,1145,918,732])
                self.equal([p.get_height() for p in axes[1].patches[:5]],[193,196,868,1092,753])
            elif demo == 2:
                P,Q,r,H=load(14,True).case_kernels(kw["case"]);g=kw["discount"]
                eps=max(sum(abs(a-b) for a,b in zip(p,q))/2 for p,q in zip(P,Q));R=max(r)
                values=[load(14,True).recurrence_error(P,Q,r,g,h) for h in range(1,H+1)]
                # Zero at H=1 is omitted on a logarithmic axis.
                shown=[h for h in range(1,H+1) if values[h-1]>0] if eps else list(range(1,H+1))
                self.line(axes[0],shown,[values[h-1] for h in shown])
                self.line(axes[0],shown,[R*eps*h*(h-1)/2 for h in shown])
                self.relation(axes[1],lambda gamma:R/(1-gamma))
            elif demo == 3:
                truth=[.2,.3,.4,.5,.6,.9,.55,.45,.35,.25,.15,.1];model=list(truth);e=kw["error"]
                if kw["pattern"]=="shared":model=[x+e for x in truth]
                elif kw["pattern"]=="favorable":model[11]+=e
                else:model[5]-=e;model[4]+=e
                self.line(axes[0],range(1,13),truth);self.line(axes[0],range(1,13),model)
                self.heights(axes[1],[b-a for a,b in zip(truth,model)])
            else:
                R,gap={"r1":(1,.5),"r1small":(1,.2),"r10":(10,2)}[kw["scenario"]]
                self.relation(axes[0],lambda h:R*kw["error"]*h*(h-1),minimum_points=2)

    def chapter(self,n):
        module=load(n);count=0
        for j,demo in enumerate(module.CHAPTER["demos"],1):
            for values in itertools.product(*(c["values"] for c in demo["controls"])):
                kw={c["key"]:v for c,v in zip(demo["controls"],values)}
                with self.subTest(chapter=n,demo=j,controls=kw):
                    fig,metrics,interpretation,_=getattr(module,demo["function"])(**kw)
                    try:self.check(n,j,kw,fig,metrics,interpretation)
                    finally:plt.close(fig)
                count+=1
        self.assertGreater(count,0)


for _n in range(1,15):
    setattr(ReaderPlotOracles,f"test_chapter_{_n:02}_all_states",lambda self,n=_n:self.chapter(n))


if __name__=="__main__":unittest.main()
