import os
import gurobipy as gp
from gurobipy import GRB
from itertools import product
from tqdm import tqdm

from utils import pretty_print_and_save
from key import params

CONF_DIR = "active"
REDUCIBLE_DIR = "reducible"
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

print(f"Loaded {len(reducible)} reducible configurations")

# ---------- load active configurations ----------
configs = []
skipped = 0

for fn in tqdm(os.listdir(CONF_DIR), desc="Loading configuration files"):
    if not fn.endswith("-vertex.txt"):
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

print(f"Skipped {skipped} reducible configurations")

# ---------- model ----------
# Create an environment with your WLS license
env = gp.Env(params=params)

# Create the model within the Gurobi environment
m = gp.Model(env=env)
alpha = m.addVar(lb=-GRB.INFINITY, name="alpha")
m.setObjective(alpha, GRB.MAXIMIZE)

# ---------- memory / performance parameters ----------
# # Soft memory limit (GB) — set a few GB below total RAM (12.7GB here)
# m.setParam(GRB.Param.SoftMemLimit, 12)

# # Use Dual Simplex for LPs to reduce memory usage
# m.setParam(GRB.Param.Method, 1)

# # Use half of the available CPU threads
# m.setParam(GRB.Param.Threads, 1)

# # Keep presolve enabled and force sparsify reduction
# m.setParam(GRB.Param.Presolve, 2)
# m.setParam(GRB.Param.PreSparsify, 2)

# variables: only k >= d
x = {}
for k, d in tqdm(product(DEGS, repeat=2), total=len(DEGS) ** 2, desc="Creating variables"):
    if k < d: continue
    x[(k, d)] = m.addVar(lb=-GRB.INFINITY, name=f"x_{{{k}->{d}}}")
m.update()

# x_{k→d}: charge sent from a k-vertex to a d-vertex.
def get_x(k, d):
    """x_{k->d} with antisymmetry. k>=d in storage."""
    if k >= d:
        return x[(k, d)]
    else:
        return -x[(d, k)]

# ---------- configuration constraints ----------
FIXED_K = 11
for (k, d), var in x.items():
    if k != FIXED_K: continue

    if d <= 5:
        # R1: 11 -> d sends (6-d)/d
        val = (6 - d) / d
    else:
        # no charge sent from 11-vertex to d >= 6
        val = 0
    m.addConstr(var == val)

conf_constr = []
for k, neigh in tqdm(configs, desc="Adding configuration constraints"):
    c = m.addConstr(k - alpha - gp.quicksum(get_x(k, neigh[i]) for i in range(k)) >= 0)
    conf_constr.append((k, neigh, c))

# ---------- solve ----------
m.optimize()

pretty_print_and_save(m, alpha, conf_constr)