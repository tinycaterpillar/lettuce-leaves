# how to test this file: run the following command in the project root
# python -m generators.orientation

from sage.all import *
from sage.numerical.mip import MixedIntegerLinearProgram

from utils import draw
from utils import load_graphs

def orientation_with_min_semidegree(G, k):
    """
    Return an orientation of an undirected simple graph G
    such that min in-degree >= k and min out-degree >= k.
    Raise ValueError if infeasible.
    """
    if G.is_directed():
        raise ValueError("Input graph must be undirected")

    # Necessary condition
    if min(G.degree()) < 2*k:
        raise ValueError("Minimum degree < 2k, infeasible")

    # Fix an ordering for each undirected edge {u,v}
    edges = [(min(u,v), max(u,v)) for u,v in G.edges(labels=False)]

    p = MixedIntegerLinearProgram()
    x = p.new_variable(binary=True)  # x[(u,v)] = 1 means u->v

    for v in G.vertices():
        outdeg = sum(
            x[(u,w)] if v == u else (1 - x[(u,w)])
            for (u,w) in edges if v in (u,w)
        )
        dv = G.degree(v)
        p.add_constraint(outdeg >= k)
        p.add_constraint(outdeg <= dv - k)  # indeg >= k

    p.set_objective(0)
    p.solve()

    sol = p.get_values(x)

    D = DiGraph()
    D.add_vertices(G.vertices())
    for u,w in edges:
        D.add_edge(u, w) if sol[(u,w)] > 0.5 else D.add_edge(w, u)

    return D

if __name__ == "__main__":
    path = "data/list_1662_graphs.g6"
    G = load_graphs(path)[0]
    k = min(G.degree()) // 2
    D = orientation_with_min_semidegree(G, k)

    draw(D)