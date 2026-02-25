from sage.all import *

def find_subgraph_isomorphism(G_sage, P_sage):
    assert G_sage.is_directed() and P_sage.is_directed(), "Only directed graphs are supported"

    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    return it


def find_subgraph_with_vertex(G_sage, P_sage, target_vertex):
    deg_seq = P_sage.degree_sequence()
    # check P_sage is a path
    if len(deg_seq) == 1:
        assert deg_seq[0] == 1, "P_sage is not a path"
    elif len(deg_seq) == 2:
        assert deg_seq[0] == 1 and deg_seq[1] == 2, "P_sage is not a path"
    else: 
        assert deg_seq[-1] == 1 and deg_seq[-2] == 1 and deg_seq[0] == 2, "P_sage is not a path"

    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    
    for sub in it:
        if target_vertex in sub.vertices() and sub.degree(target_vertex) == 1:
            yield sub


if __name__ == "__main__":
    P = graphs.PathGraph(3)
    print(P.degree_sequence())