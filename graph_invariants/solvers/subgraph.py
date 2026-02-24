from sage.all import *

def find_subgraph_isomorphism(G_sage, P_sage):
    assert G_sage.is_directed() and P_sage.is_directed(), "Only directed graphs are supported"

    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    return it


def find_subgraph_with_vertex(G_sage, P_sage, target_vertex):
    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    
    for sub in it:
        if target_vertex in sub.vertices() and sub.degree(target_vertex) == 1:
            yield sub