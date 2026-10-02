"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);u=vector(data["scores"],"scores")
    if len(u)!=4:raise ValueError("scores order must be 00,10,01,11")
    b=vector(data["budgets"],"budgets",0)
    if len(b)!=4:raise ValueError("four budgets required")
    comparable=all(math.isclose(v,b[0],abs_tol=1e-9) for v in b)
    g=u[3]-u[1]-u[2]+u[0];gain=u[3]-u[0]; isolated=[u[1]-u[0],u[2]-u[0]]
    fraction=g/gain if gain>0 and g>=0 and min(isolated)>=0 else None
    return result({"interaction":g,"positive_amount":max(0,g),"joint_gain":gain,"signed_share":g/gain if gain else None,"fraction_share":fraction,"budget_matched":comparable},[series("four observed cells",u,y_label="declared score"),series("additive decomposition",[u[0],*isolated,g],y_label="score contribution")],"The contrast is a decomposition on the chosen score scale. Unequal budgets prevent interpreting it as a matched component comparison." if not comparable else "Matched budgets support the specified four-cell comparison; they do not alone identify a mechanism.",["Cell order is neither, first only, second only, both.","Task, measurement, and all uncontrolled conditions must also match."],["A ratio outside the fraction domain is signed arithmetic, not a cooperation fraction.","No uncertainty is available from four means alone."])
