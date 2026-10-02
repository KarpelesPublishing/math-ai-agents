"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);M=[[flag(v,"bank success") for v in row] for row in data["success_matrix"]];weights=probs(data["task_weights"]);selected=data["selected_candidates"];allowed=[flag(v,"deployment allowed") for v in data["deployment_allowed"]];p=num(data["independent_candidate_success"],"candidate success",0,1);k=len(M)
    if not k or any(len(r)!=len(weights) for r in M) or len(selected)!=len(weights) or len(allowed)!=len(weights):raise ValueError("candidate by task matrix and task vectors must align")
    chosen=[count(i,"selected candidate",0,k-1) for i in selected];oracle=[any(M[i][t] for i in range(k)) for t in range(len(weights))];actual=[M[chosen[t]][t] for t in range(len(weights))];deployed=[a and b for a,b in zip(actual,allowed)];coverage=[]
    for j in range(1,k+1):coverage.append(sum(weights[t]*any(M[i][t] for i in range(j)) for t in range(len(weights))))
    return result({"bank_oracle_coverage":dot(weights,oracle),"actual_selection_success":dot(weights,actual),"deployment_success":dot(weights,deployed),"oracle_task_flags":oracle,"selection_task_flags":actual,"deployment_task_flags":deployed},[series("observed finite bank coverage",coverage,list(range(1,k+1)),"candidate bank size","task-weighted coverage"),series("independent constructed saturation",[1-(1-p)**i for i in range(1,k+1)],list(range(1,k+1)),"independent candidates","coverage probability")],"Oracle coverage asks whether some candidate solves each task. Actual selection and deployment filtering can only reduce that finite-bank ceiling.",["Bank contents and task distribution are fixed.","Selection is supplied per task; oracle selection is not assumed achievable.","Independent saturation is a separate constructed sampling law."],["The bank ceiling is not a universal agent limit or a forecast of future models.","Unobserved tasks and candidate classes remain outside the bound."])
