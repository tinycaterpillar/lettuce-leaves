import os
import gurobipy as gp
from gurobipy import GRB
from itertools import product
from tqdm import tqdm

from utils import pretty_print_and_save, pretty_print_rules, CONF_DIR, REDUCIBLE_DIR, Constrints
from key import params

def load_reducible_configs(suffix):
    configs = set()
    for fn in os.listdir(REDUCIBLE_DIR):
        if not fn.endswith(suffix):
            continue
        k = int(fn.split("-")[0])
        with open(os.path.join(REDUCIBLE_DIR, fn)) as f:
            for line in f:
                if line.strip():
                    cfg = tuple(map(int, line.split()))
                    configs.add((k, cfg))
    return configs


def load_active_configs(suffix, reducible, verbose):
    configs = []
    skipped = 0

    files = os.listdir(CONF_DIR)
    if verbose:
        files = tqdm(files, desc=f"Loading {suffix} configs")

    for fn in files:
        if not fn.endswith(suffix):
            continue
        k = int(fn.split("-")[0])
        with open(os.path.join(CONF_DIR, fn)) as f:
            for line in f:
                if not line.strip():
                    continue
                cfg = tuple(map(int, line.split()))
                if (k, cfg) in reducible:
                    skipped += 1
                    continue
                configs.append((k, list(cfg)))
    return configs, skipped


def solve(verbose=True):
    # ---------- load reducible configurations ----------
    reducible_vertex = load_reducible_configs("-vertex.txt")
    reducible_face = load_reducible_configs("-face.txt")

    if verbose:
        print(f"Loaded {len(reducible_vertex)+len(reducible_face)} reducible configurations")

    # ---------- load active configurations ----------
    configs_vertex, skipped_vertex = load_active_configs("-vertex.txt", reducible_vertex, verbose=verbose)
    configs_face, skipped_face = load_active_configs("-face.txt", reducible_face, verbose=verbose)
                 
    print(f"Skipped {skipped_vertex+skipped_face} reducible configurations")

    # ---------- model ----------
    env = gp.Env(params=params)
    m = gp.Model(env=env)

    if not verbose:
        m.setParam(GRB.Param.OutputFlag, 0)

    alpha = m.addVar(lb=-GRB.INFINITY, name="alpha")
    m.setObjective(alpha, GRB.MAXIMIZE)

    # ---------- variables ----------
    vertices = [5, 6, 7, 8]
    faces = [3, 4]
    xFF, xVV, xFV = {}, {}, {}

    # face -> face
    for k in faces:
        for d in faces:
            if k < d:
                continue
            xFF[(k, d)] = m.addVar(lb=-GRB.INFINITY, name=f"xFF[{k},{d}]")

    # vertex -> vertex
    for k in vertices:
        for d in vertices:
            if k < d:
                continue
            xVV[(k, d)] = m.addVar(lb=-GRB.INFINITY, name=f"xVV[{k},{d}]")

    # face -> vertex (fix direction: F -> V)
    for k in faces:
        for d in vertices:
            xFV[(k, d)] = m.addVar(lb=-GRB.INFINITY, name=f"xFV[{k},{d}]")

    m.update()

    def get_FF(k, d):
        return xFF[(k, d)] if k >= d else -xFF[(d, k)]

    def get_VV(k, d):
        return xVV[(k, d)] if k >= d else -xVV[(d, k)]

    def get_FV(f, v):
        # f ∈ faces, v ∈ vertices
        return xFV[(f, v)]

    # ---------- fixed rules ----------
    FIXED_F = 4
    for (k, d), var in xFV.items():
        if k != FIXED_F:
            continue
        if d == 5:
            val = 1/2
        else:
            val = 0
        m.addConstr(var == val)

    FIXED_K = 8
    for (k, d), var in xVV.items():
        if k != FIXED_K:
            continue
        if d == 5:
            val = 1/5
        else:
            val = 0
        m.addConstr(var == val)

    # enforce diagonal = 0 for skew-symmetry
    for k in faces:
        m.addConstr(xFF[(k, k)] == 0, name=f"FF_diag0[{k}]")
    for k in vertices:
        m.addConstr(xVV[(k, k)] == 0, name=f"VV_diag0[{k}]")

    # ---------- configuration constraints ----------
    conf_constr = []

    # vertex-centered
    it = configs_vertex
    if verbose:
        it = tqdm(it, desc="Adding vertex configuration constraints")

    for k, neigh in it:
        assert len(neigh) == 2*k
        c = m.addConstr(
            k
            - alpha
            - gp.quicksum(
                -get_FV(neigh[i], k) if i % 2 == 0
                else get_VV(k, neigh[i])
                for i in range(2 * k)
            )
            >= 0
        )
        conf_constr.append(Constrints(k=k, neigh=neigh, c=c, type="V"))


    # face-centered
    it = configs_face
    if verbose:
        it = tqdm(it, desc="Adding face configuration constraints")

    for k, neigh in it:
        assert len(neigh) == 2*k
        c = m.addConstr(
            2*k
            - alpha
            - gp.quicksum(
                get_FF(k, neigh[i]) if i % 2 == 0
                else get_FV(k, neigh[i])
                for i in range(2 * k)
            )
            >= 0
        )
        conf_constr.append(Constrints(k=k, neigh=neigh, c=c, type="F"))

    # ---------- solve ----------
    m.optimize()

    if m.Status != GRB.OPTIMAL:
        if verbose:
            print("No optimal solution available.")
        return None

    pretty_print_and_save(m, alpha, conf_constr, verbose=verbose)
    pretty_print_rules({"FF": xFF, "VV": xVV, "FV": xFV}, alpha, verbose=verbose)

    return alpha.X

if __name__ == "__main__":
    solve(verbose=True)