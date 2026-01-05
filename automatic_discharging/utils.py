import os
from gurobipy import GRB
from datetime import datetime

def collect_tight_configs(conf_constr, eps=1e-6):
    tight_by_k = {}

    for k, neigh, c in conf_constr:
        if abs(c.Slack) < eps:
            tight_by_k.setdefault(k, []).append(neigh)

    return tight_by_k


def save_tight_configs(tight_by_k, serial, out_dir="tight"):
    os.makedirs(out_dir, exist_ok=True)

    for k, neighs in tight_by_k.items():
        fname = os.path.join(out_dir, f"{k}-vertex_{serial}.txt")
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
    serial = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    print(f"Status        : {status}")
    print(f"Serial        : {serial}")

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
        save_tight_configs(tight_by_k, serial, out_dir)
        print(f"\nSaved to '{out_dir}/'")


def pretty_print_rules(x, eps=1e-9, out_dir="tight", fname="rules.txt"):
    """
    Print and save discharging rules in a clean aligned table.
    x : dict[(k, d)] -> gurobi Var
    """
    # Read values and clean tiny numbers
    rules = []
    for (k, d), var in x.items():
        val = var.X
        if abs(val) < eps:
            val = 0.0
        rules.append((k, d, val))

    # Sort by (k, d)
    rules.sort()

    # Compute column widths
    k_width = max(len(str(k)) for k, _, _ in rules)
    d_width = max(len(str(d)) for _, d, _ in rules)
    v_width = max(len(f"{v:.6f}") for _, _, v in rules)

    # Prepare lines
    lines = []
    lines.append("=" * 50)
    lines.append(" Discharging Rules")
    lines.append("=" * 50)
    lines.append(
        f"{'from k':>{k_width + 6}}"
        f"{'to d':>{d_width + 8}}"
        f"{'charge':>{v_width + 10}}"
    )
    lines.append("-" * 50)

    for k, d, v in rules:
        lines.append(
            f"{k:>{k_width + 6}d}"
            f"{d:>{d_width + 8}d}"
            f"{v:>{v_width + 10}.6f}"
        )

    lines.append("=" * 50)

    # Print
    print("\n".join(lines))

    # Save
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fname)
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"\nSaved to '{path}'")
