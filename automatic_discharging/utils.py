import os
from dataclasses import dataclass
import gurobipy
from gurobipy import GRB

CONF_DIR = "active"
PENDING_DIR = "pending"
REDUCIBLE_DIR = "reducible"
TIGHT_DIR = "tight"


@dataclass
class Constrints:
    k: int
    neigh: list
    c: gurobipy.Constr
    type: str   # "V" or "F"


def collect_bottleneck_configs(conf_constr, eps_slack=1e-6):
    tight = [cons for cons in conf_constr if abs(cons.c.Slack) < eps_slack]
    assert tight, "There is no tight constraint"

    best_pi = max(abs(cons.c.Pi) for cons in tight)

    return [cons for cons in tight if abs(abs(cons.c.Pi) - best_pi) < 1e-9]


def save_tight_config(bottlenecks, out_dir=TIGHT_DIR):
    assert bottlenecks, "bottleneck_list is empty"
    os.makedirs(out_dir, exist_ok=True)

    for b in bottlenecks:
        suffix = "vertex" if b.type == "V" else "face"
        fname = os.path.join(out_dir, f"{b.k}-{suffix}.txt")

        with open(fname, "w") as f:
            f.write(" ".join(map(str, b.neigh)) + "\n")



def clear_dir(dir_path):
    """Remove all files in a directory."""
    if not os.path.isdir(dir_path):
        return
    for fn in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, fn))


def pretty_print_and_save(m, alpha, conf_constr, verbose=True, out_dir=TIGHT_DIR):
    # collect
    bottlenecks = collect_bottleneck_configs(conf_constr)

    # ---- print summary ----
    if verbose:
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
            print(f"Bottleneck #  : {len(bottlenecks)}")
        else:
            print("No optimal solution available.")
            return

        print("="*60)

    # ---- save ----
    clear_dir(out_dir)
    save_tight_config(bottlenecks, out_dir)
    if verbose:
        print(f"\nSaved to '{out_dir}/'")


def pretty_print_rules(all_vars, alpha, eps=1e-9, verbose=True, out_dir=".", fname="rules.txt"):
    rules = []

    for name, x in all_vars.items():
        for (k, d), var in x.items():
            v = var.X
            if abs(v) < eps:
                v = 0.0
            rules.append((name, k, d, v))

    if not rules:
        if verbose:
            print("No rules to print.")
        return

    rules.sort(key=lambda t: (t[0], t[1], t[2]))

    lines = []
    lines.append("=" * 60)
    lines.append(f" Discharging Rules | Alpha: {alpha.X:.8f}")
    lines.append("=" * 60)
    lines.append(f"{'type':>6}{'from':>8}{'to':>8}{'charge':>14}")
    lines.append("-" * 60)

    for name, k, d, v in rules:
        lines.append(f"{name:>6}{k:>8}{d:>8}{v:>14.6f}")

    lines.append("=" * 60)

    if verbose:
        print("\n".join(lines))

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fname)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    if verbose:
        print(f"\nSaved to '{path}'")
