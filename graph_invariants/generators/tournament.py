from sage.all import *
from pathlib import Path

def min_semidegree(D):
    return min(min(D.in_degree()), min(D.out_degree()))

def get_tournament(n, k):
    for T in digraphs.tournaments_nauty(Integer(n)):
        if min_semidegree(T) >= k:
            yield T

def save_digraphs(graphs, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        for g in graphs:
            f.write(g.canonical_label().dig6_string() + "\n")


if __name__ == "__main__":
    n = 10
    path = f"data/tournament_{n}.dig6"
    save_digraphs(get_tournament(n, k=3), path)
    print("saved:", path)    