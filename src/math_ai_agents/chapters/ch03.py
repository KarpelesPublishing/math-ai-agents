"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);x=vector(data["development_x"]);y=vector(data["development_y"]);tx=vector(data["test_x"]);ty=vector(data["test_y"])
    if len(x)!=len(y) or len(tx)!=len(ty) or len(x)<2:raise ValueError("aligned development and test pairs required")
    if set(x)&set(tx):raise ValueError("development and unseen test scales overlap")
    family=data.get("family","linear")
    if family not in ("linear","log"):raise ValueError("family must be linear or log")
    if family=="log" and min(x+tx)<=0:raise ValueError("log family requires positive scales")
    f=math.log if family=="log" else lambda a:a
    z=[f(v) for v in x];m=sum(z)/len(z);ym=sum(y)/len(y);den=sum((v-m)**2 for v in z)
    if den==0:raise ValueError("development scales need variation")
    slope=sum((a-m)*(b-ym) for a,b in zip(z,y))/den;intercept=ym-slope*m
    pred=[intercept+slope*f(v) for v in tx];errors=[p-t for p,t in zip(pred,ty)]
    return result({"family":family,"slope":slope,"intercept":intercept,"predictions":pred,"test_rmse":math.sqrt(sum(e*e for e in errors)/len(errors)),"test_bias":sum(errors)/len(errors)},[series("frozen forecast",pred,tx,"test scale","score"),series("unseen observation",ty,tx,"test scale","score"),series("forecast residual",errors,tx,"test scale","prediction minus observation")],"Only development observations fit the declared family. Test outcomes score the frozen forecast and never update its coefficients.",["Family selection is declared before the test is inspected.","Least squares describes the supplied development observations."],["Extrapolation validity and mechanism are not established by a good fit.","Protocol metadata is needed to establish real prospective separation."])
