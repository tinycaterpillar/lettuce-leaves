import os
import gurobipy as gp
from gurobipy import GRB
from itertools import product
from tqdm import tqdm

from utils import pretty_print_and_save, pretty_print_rules, CONF_DIR, REDUCIBLE_DIR
from key import params


def solve(verbose=True):
    DEGS = list(range(3, 12))

    # ---------- load reducible configurations ----------
    reducible = set()

    for fn in os.listdir(REDUCIBLE_DIR):
        if not fn.endswith("-vertex.txt"):
            continue
        k = int(fn.split("-")[0])
        with open(os.path.join(REDUCIBLE_DIR, fn)) as f:
            for line in f:
                if line.strip():
                    cfg = tuple(map(int, line.split()))
                    reducible.add((k, cfg))

    if verbose:
        print(f"Loaded {len(reducible)} reducible configurations")

    # ---------- load active configurations ----------
    configs = []
    skipped = 0

    it = os.listdir(CONF_DIR)
    if verbose:
        it = tqdm(it, desc="Loading configuration files")

    for fn in it:
        if not fn.endswith(".txt"):
            continue
        if "-vertex_" not in fn:
            continue
        k = int(fn.split("-vertex_")[0])
        with open(os.path.join(CONF_DIR, fn)) as f:
            for line in f:
                if not line.strip():
                    continue
                cfg = tuple(map(int, line.split()))
                if (k, cfg) in reducible:
                    skipped += 1
                    continue
                configs.append((k, list(cfg)))

    print(f"Skipped {skipped} reducible configurations")

    # ---------- model ----------
    env = gp.Env(params=params)
    m = gp.Model(env=env)

    if not verbose:
        m.setParam(GRB.Param.OutputFlag, 0)

    alpha = m.addVar(lb=-GRB.INFINITY, name="alpha")
    m.setObjective(alpha, GRB.MAXIMIZE)

    # ---------- variables ----------
    x = {}

    it = product(DEGS, repeat=2)
    if verbose:
        it = tqdm(it, total=len(DEGS)**2, desc="Creating variables")

    for k, d in it:
        if k < d:
            continue
        x[(k, d)] = m.addVar(lb=-GRB.INFINITY, name=f"x_{{{k}->{d}}}")

    m.update()

    def get_x(k, d):
        return x[(k, d)] if k >= d else -x[(d, k)]

    # ---------- fixed rules ----------
    FIXED_K = 11
    for (k, d), var in x.items():
        if k != FIXED_K:
            continue
        if d <= 5:
            val = (6 - d) / d
        else:
            val = 0
        m.addConstr(var == val)

    # ---------- configuration constraints ----------
    conf_constr = []

    it = configs
    if verbose:
        it = tqdm(it, desc="Adding configuration constraints")

    for k, neigh in it:
        c = m.addConstr(
            k - alpha - gp.quicksum(get_x(k, neigh[i]) for i in range(k)) >= 0
        )
        conf_constr.append((k, neigh, c))

    # ---------- solve ----------
    m.optimize()

    if m.Status != GRB.OPTIMAL:
        if verbose:
            print("No optimal solution available.")
        return None

    pretty_print_and_save(m, alpha, conf_constr, verbose=verbose)
    pretty_print_rules(x, verbose=verbose)

    return alpha.X

if __name__ == "__main__":
    solve(verbose=True)