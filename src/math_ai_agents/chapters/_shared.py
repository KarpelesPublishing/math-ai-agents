"""Small validation and output helpers, standard library only."""
import math
import random
import itertools
import heapq
from collections import defaultdict, deque

def check_tree(x):
    if isinstance(x, float) and not math.isfinite(x): raise ValueError("all numeric inputs must be finite")
    if isinstance(x, dict):
        for v in x.values(): check_tree(v)
    elif isinstance(x, (list, tuple)):
        for v in x: check_tree(v)

def num(x, name="value", lo=None, hi=None):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x): raise ValueError(name+" must be finite numeric")
    if lo is not None and x<lo or hi is not None and x>hi: raise ValueError(name+" outside permitted range")
    return float(x)

def count(x,name="count",lo=1,hi=10000):
    if type(x) is not int or not lo<=x<=hi: raise ValueError(name+" must be integer in permitted range")
    return x

def flag(x,name="flag"):
    if type(x) is not bool: raise ValueError(name+" must be boolean")
    return x

def probs(xs,name="probabilities"):
    if not isinstance(xs,list) or not xs: raise ValueError(name+" must be nonempty list")
    ys=[num(x,name,0,1) for x in xs]
    if not math.isclose(sum(ys),1,abs_tol=1e-9): raise ValueError(name+" must sum to one")
    return ys

def vector(xs,name="vector",lo=None,hi=None):
    if not isinstance(xs,list) or not xs: raise ValueError(name+" must be nonempty list")
    return [num(x,name,lo,hi) for x in xs]

def name(x):
    if not isinstance(x,str) or not x: raise ValueError("identifier must be nonempty string")
    return x

def series(label,y,x=None,x_label="case",y_label="value",x_ticklabels=None):
    out={"label":label,"x":list(range(len(y))) if x is None else list(x),"y":list(y),"x_label":x_label,"y_label":y_label}
    if x_ticklabels is not None:out["x_ticklabels"]=list(x_ticklabels)
    return out

def result(metrics,curves,interpretation,assumptions,limitations,tables=None):
    out={"metrics":metrics,"series":curves,"interpretation":interpretation,"assumptions":assumptions,"limitations":limitations}
    if tables is not None: out["tables"]=tables
    check_tree(out)
    return out

def dot(a,b):
    if len(a)!=len(b): raise ValueError("vector lengths must match")
    return sum(x*y for x,y in zip(a,b))

def wilson(successes,n,z=1.959963984540054):
    if not n:return None
    p=successes/n; q=1+z*z/n
    c=(p+z*z/(2*n))/q; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/q
    return [max(0,c-h),min(1,c+h)]
