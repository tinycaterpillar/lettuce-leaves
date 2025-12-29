import os
import gurobipy as gp
from gurobipy import GRB
from itertools import product
from tqdm import tqdm

from utils import pretty_print_and_save
from key import params

CONF_DIR = "active"
DEGS = list(range(3, 12))


# ---------- load configurations ----------
configs = []
for fn in tqdm(os.listdir(CONF_DIR), desc="Loading configuration files"):
    if not fn.endswith("-vertex.txt"):
        continue
    k = int(fn.split("-")[0])
    with open(os.path.join(CONF_DIR, fn)) as f:
        for line in f:
            if line.strip():
                configs.append((k, list(map(int, line.split()))))


# ---------- model ----------
# Create an environment with your WLS license
env = gp.Env(params=params)

# Create the model within the Gurobi environment
m = gp.Model(env=env)

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

alpha = m.addVar(lb=-GRB.INFINITY, name="alpha")

# variables: only a >= b and k >= d
x = {}
for k, d, a, b in tqdm(product(DEGS, repeat=4), total=len(DEGS) ** 4, desc="Creating variables"):
    if a < b or k < d: continue
    x[(k, a, b, d)] = m.addVar(lb=-GRB.INFINITY, name=f"x_{{{k};{a},{b}->{d}}}")
m.update()

# x_{k;a,b→d}: charge sent from a k-vertex to a d-vertex when they share two common neighbors of degrees a and b.
def get_x(k, a, b, d):
    """x_{k;a,b->d} with antisymmetry, assuming a>=b and k>=d in storage."""
    if a < b:
        a, b = b, a
    if k >= d:
        return x[(k, a, b, d)]
    else:
        return -x[(d, a, b, k)]

# ---------- configuration constraints ----------
FIXED_K = 11
for (k, a, b, d), var in x.items():
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
    c = m.addConstr(k - alpha
        - gp.quicksum(
            get_x(
                k,
                neigh[i - 1],
                neigh[(i + 1) % k],
                neigh[i]
            )
            for i in range(k)
        ) >= 0
    )
    conf_constr.append((k, neigh, c))

# ---------- solve ----------
m.optimize()

pretty_print_and_save(m, alpha, conf_constr, save=(alpha.X < 6))