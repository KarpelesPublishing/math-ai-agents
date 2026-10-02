"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);M=[vector(r,"cross-play probabilities",0,1) for r in data["matrix"]];k=len(M);weights=probs(data["partner_weights"])
    if not k or any(len(r)!=k for r in M) or len(weights)!=k:raise ValueError("square cross-play matrix and weights required")
    selfplay=sum(M[i][i] for i in range(k))/k;cross=sum(M[i][j] for i in range(k) for j in range(k) if i!=j)/(k*(k-1)) if k>1 else None
    expected=[dot(r,weights) for r in M];supervisor=probs(data["supervisor_weights"])
    if len(supervisor)!=k:raise ValueError("supervisor mixture dimension mismatch")
    revised=[dot(r,supervisor) for r in M]
    return result({"mean_self_play":selfplay,"mean_cross_play":cross,"joint_policy_correlation_loss":(None if cross is None or selfplay==0 else (selfplay-cross)/selfplay),"partner_mixture_values":expected,"supervisor_mixture_values":revised,"selected_policy":max(range(k),key=lambda i:expected[i]),"supervisor_selected_policy":max(range(k),key=lambda i:revised[i])},[series("self-play diagonal",[M[i][i] for i in range(k)],y_label="success probability"),series("partner transfer",expected,y_label="mixture success probability"),series("changed supervisor mixture",revised,y_label="mixture success probability")],"joint_policy_correlation_loss is Equation 19.2: (mean diagonal minus mean off-diagonal) divided by mean diagonal, computed here from the supplied matrix. Diagonal success measures coordination with matching partners. Off-diagonal entries and target weights determine transfer to other partners.",["Matrix cells use matched tasks, budgets, and success definitions.","Partner and supervisor weights are declared deployment mixtures."],["Changing counterparties can change the environment itself.","A supplied matrix does not establish stationarity or sampling precision."],M)
