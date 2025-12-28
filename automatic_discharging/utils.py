import os
from gurobipy import GRB

def collect_tight_configs(conf_constr, eps=1e-6):
    tight_by_k = {}

    for k, neigh, c in conf_constr:
        if abs(c.Slack) < eps:
            tight_by_k.setdefault(k, []).append(neigh)

    return tight_by_k


def save_tight_configs(tight_by_k, out_dir="tight"):
    os.makedirs(out_dir, exist_ok=True)

    for k, neighs in tight_by_k.items():
        fname = os.path.join(out_dir, f"{k}-vertex.txt")
        with open(fname, "w") as f:
            for neigh in neighs:
                f.write(" ".join(map(str, neigh)) + "\n")


def pretty_print_and_save(m, alpha, conf_constr, save=True, out_dir="tight"):
    # collect
    tight_by_k = collect_tight_configs(conf_constr)

    # ---- print summary ----
    status_map = {
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.TIME_LIMIT: "TIME_LIMIT"
    }

    print("\n" + "="*60)
    print(" Optimization Summary")
    print("="*60)

    status = status_map.get(m.Status, f"STATUS {m.Status}")
    print(f"Status        : {status}")

    if m.Status == GRB.OPTIMAL:
        print(f"Alpha         : {alpha.X:.8f}")
        print(f"Variables     : {m.NumVars}")
        print(f"Constraints   : {m.NumConstrs}")
    else:
        print("No optimal solution available.")
        return

    print("="*60)

    total = sum(len(v) for v in tight_by_k.values())
    print("\nTight configurations")
    print("-"*40)
    print(f"Total         : {total}")

    for k in sorted(tight_by_k):
        print(f"  k = {k:2d}     : {len(tight_by_k[k])}")

    # ---- save ----
    if save:
        save_tight_configs(tight_by_k, out_dir)
        print(f"\nSaved to '{out_dir}/'")

