"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);D=num(data["demand"],"demand",0.000001);cap=num(data["capacity"],"capacity",0.000001);c=num(data["constant_time"],"constant time",0);over=num(data["shortcut_overhead"],"shortcut overhead",0);toll=num(data["shortcut_toll"],"toll",0)
    # Symmetric nonatomic Braess network: outer routes x,x and shortcut z.
    def allocation(z):
        x=(D-z)/2;v=(x+z)/cap;outer=v+c;short=2*v+over
        return x,outer,short,2*x*outer+z*short
    z=max(0,min(D,2*cap*(c-over-toll)-D));x,outer,short,total=allocation(z)
    before=D*(D/(2*cap)+c)
    # Social optimum minimizes the exact convex quadratic over z in [0,D].
    zopt=max(0,min(D,cap*(c-over)-D));xo,oo,so,opt=allocation(zopt)
    grid=[D*i/100 for i in range(101)];social=[allocation(v)[3] for v in grid]
    return result({"without_shortcut_total_time":before,"equilibrium_shortcut_flow":z,"equilibrium_outer_flow_each":x,"equilibrium_social_time":total,"equilibrium_private_outer_time":outer,"equilibrium_private_shortcut_time":short+toll,"optimal_shortcut_flow":zopt,"optimal_social_time":opt,"price_of_anarchy":total/opt if opt else None,"braess_worsens":total>before+1e-12,"toll_revenue":z*toll},[series("social travel cost",social,grid,"shortcut flow","total traveler time")],"A new route can change private incentives and increase total delay. Tolls enter private cost; toll payments are excluded from travel-time social cost.",["Symmetric continuous flow, linear congestible edges, constant outer edges.","All travelers choose minimum private path cost at nonatomic equilibrium."],["This construction does not estimate a real workflow equilibrium.","Discrete teams and heterogeneous incentives need additional modeling."])
