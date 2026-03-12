from sage.all import *

def find_subgraph_isomorphism(G_sage, P_sage):
    assert G_sage.is_directed() == P_sage.is_directed(), "Both graphs must have the same directed type"

    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    return it


def find_subgraph_with_vertex(G_sage, P_sage, target_vertex):
    deg_seq = P_sage.degree_sequence()
    # check P_sage is a path
    if len(deg_seq) == 2:
        assert deg_seq[0] == 0, "P_sage is not a path"
    else: 
        assert deg_seq[-1] == 1 and deg_seq[-2] == 1 and deg_seq[0] == 2, "P_sage is not a path"

    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    
    for sub in it:
        if target_vertex in sub.vertices() and sub.degree(target_vertex) == 1:
            yield sub


def find_directed_path_with_start_vertex(G_sage, P_sage, start_vertex):
    deg_seq = P_sage.degree_sequence()
    # check P_sage is a path
    if len(deg_seq) == 2:
        assert deg_seq[0] == 0, "P_sage is not a path"
    else: 
        assert deg_seq[-1] == 1 and deg_seq[-2] == 1 and deg_seq[0] == 2, "P_sage is not a path"
        assert max(max(P_sage.in_degree(v), P_sage.out_degree(v)) for v in P_sage.vertices()) == 1, "P_sage is not a directed path"

    it = G_sage.subgraph_search_iterator(P_sage, induced=False)
    for sub in it:
        if start_vertex in sub.vertices() and sub.out_degree(start_vertex) == 1 and sub.in_degree(start_vertex) == 0:
            yield sub


if __name__ == "__main__":
    P = DiGraph([(0,1),(1,2)])
    # print(P.degree_sequence())
    print(P.in_degree(1), P.out_degree(1))