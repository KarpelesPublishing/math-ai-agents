"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);p=num(data["step_success"],"step success",0,1);n=count(data["steps"],hi=1000)
    conditional=vector(data["conditional_success"],"conditional probabilities",0,1)
    if len(conditional)!=n:raise ValueError("conditional_success must list one probability per step (its length must equal steps)")
    chooser=[probs(row,"chooser row") for row in data["chooser"]];tool=[probs(row,"tool row") for row in data["tool"]]
    k=len(chooser)
    if any(len(r)!=len(tool) for r in chooser) or any(len(r)!=k for r in tool):raise ValueError("chooser and tool dimensions incompatible")
    kernel=[[sum(chooser[i][a]*tool[a][j] for a in range(len(tool))) for j in range(k)] for i in range(k)]
    state=probs(data["initial"])
    if len(state)!=k:raise ValueError("initial state dimension mismatch")
    occupancy=[state[:]]
    for _ in range(n):state=[sum(state[i]*kernel[i][j] for i in range(k)) for j in range(k)];occupancy.append(state[:])
    ablations=[]
    def multiply(left,right):
        return [[sum(left[i][a]*right[a][j] for a in range(len(right))) for j in range(len(right[0]))] for i in range(len(left))]
    for assembly in data.get("assemblies",[]):
        assembly_name=name(assembly["name"]); budget=num(assembly["budget"],"assembly resource allowance",0);depth=count(assembly["steps"],hi=1000)
        factors=[]
        for factor in ("observation","memory","retrieval"):
            matrix=[probs(row,factor+" row") for row in assembly[factor]]
            if len(matrix)!=k or any(len(row)!=k for row in matrix):raise ValueError("Assembly context maps must use the declared state dimension")
            factors.append(matrix)
        effect=[probs(row,"assembly tool row") for row in assembly["tool"]]
        if len(effect)!=len(tool) or any(len(row)!=k for row in effect):raise ValueError("Assembly tool dimension mismatch")
        assembled=factors[0]
        for factor in [*factors[1:],chooser,effect]:assembled=multiply(assembled,factor)
        distribution=probs(data["initial"])
        for _ in range(depth):distribution=[sum(distribution[i]*assembled[i][j] for i in range(k)) for j in range(k)]
        ablations.append({"assembly":assembly_name,"budget":budget,"steps":depth,"kernel":assembled,"terminal_distribution":distribution})
    matched_budget=len({row["budget"] for row in ablations})<=1 if ablations else None
    same_depth=len({row["steps"] for row in ablations})<=1 if ablations else None
    extra_series=[series("assembled terminal state-zero probability",[row["terminal_distribution"][0] for row in ablations],x_label="assembly index (see table)",y_label="probability")] if ablations else []
    return result({"assemblies":ablations,"assembly_budgets_matched":matched_budget,"assembly_depths_matched":same_depth,"composite_kernel":kernel,"terminal_distribution":state,"independent_all_success":p**n,"shared_condition_all_success":p,"chain_rule_all_success":math.prod(conditional)},[series("independent trajectory success",[p**i for i in range(n+1)],x_label="step count",y_label="completion probability"),series("shared condition trajectory success",[1]+[p]*n,x_label="step count",y_label="completion probability"),series("state zero occupancy",[s[0] for s in occupancy],x_label="transition count",y_label="probability")]+extra_series,"The frozen chooser and tool jointly define the state kernel. Equal marginal step success can coexist with sharply different trajectory reliability.",["Kernel factors use the declared state and action boundary.","Independent and shared-condition cases are different constructed joint distributions.","Chain-rule inputs condition each success on previous successes."],["Marginal rates cannot be inserted into the conditional chain rule without justification.","No measured agent reliability is inferred from these constructions.","Observation, memory and retrieval maps are declared finite context transformations; they do not measure a real memory implementation.","Resource allowance equality is necessary for a matched ablation, not evidence of equal consumed work."],ablations)
