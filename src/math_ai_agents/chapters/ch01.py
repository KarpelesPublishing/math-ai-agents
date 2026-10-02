"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data); xs=vector(data["scales"],"scales"); scores=vector(data["scores"],"scores",0,1)
    if len(xs)!=len(scores) or any(b<=a for a,b in zip(xs,xs[1:])):raise ValueError("aligned, strictly increasing scales required")
    threshold=num(data["threshold"],"threshold",0,1); binary=[int(s>=threshold) for s in scores]
    jumps=[binary[i]-binary[i-1] for i in range(1,len(binary))]
    slopes=[(scores[i]-scores[i-1])/(xs[i]-xs[i-1]) for i in range(1,len(scores))]
    return result({"thresholded_scores":binary,"crossing_count":sum(j!=0 for j in jumps),"max_raw_slope":max(slopes,default=0)},[series("continuous score",scores,xs,"scale","score"),series("thresholded score",binary,xs,"scale","pass flag")],"A jump in the thresholded curve may come from the scoring rule even when the supplied continuous scores change gradually.",["The same task, output boundary, and environment apply across scales."],["This diagnostic neither identifies a neural mechanism nor proves a phase transition."],{"local_slopes":slopes})
