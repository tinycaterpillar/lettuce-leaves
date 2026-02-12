from sage.all import *
import networkx as nx
from networkx.algorithms import isomorphism

def contains_subgraph(G_sage, H_sage):
    G_nx = nx.DiGraph(G_sage.to_dictionary())
    H_nx = nx.DiGraph(H_sage.to_dictionary())

    if G_sage.is_directed():
        matcher = isomorphism.DiGraphMatcher(G_nx, H_nx)
    else:
        matcher = isomorphism.GraphMatcher(G_nx, H_nx)

    if matcher.subgraph_is_isomorphic():
        return True, next(matcher.subgraph_isomorphisms_iter())
    return False, None


def contains_subgraph_through_vertex(G_sage, H_sage, v):
    G = nx.DiGraph(G_sage.to_dictionary())
    H = nx.DiGraph(H_sage.to_dictionary())

    v_in, v_out = G.in_degree(v), G.out_degree(v)

    for h in H.nodes():
        if H.in_degree(h) > v_in or H.out_degree(h) > v_out:
            continue

        for x in G.nodes():
            G.nodes[x]["must"] = (x == v)
        for x in H.nodes():
            H.nodes[x]["must"] = (x == h)

        matcher = isomorphism.DiGraphMatcher(
            G, H,
            node_match=lambda a, b: a["must"] == b["must"]
        )

        for mapping in matcher.subgraph_isomorphisms_iter():
            if mapping.get(h) == v:
                return True, mapping

    return False, None