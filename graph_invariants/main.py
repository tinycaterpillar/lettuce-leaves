from sage.all import *
import os
import random

from utils import draw, setup_logger, parse_adjacency_matrix
from generators import get_antidirected_path, bitmask_to_sage_graph, get_oriented_path, bitmask_to_direction_string
from solvers import find_subgraph_isomorphism, find_directed_path_with_start_vertex


def get_start_vertex(P):
    for v in P.vertices():
        if P.in_degree(v) != 0: continue
        if P.out_degree(v) != 1: continue
        return v
    raise RuntimeError("No start vertex found")


if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")
    
    A = """[0 0 1 1 0 1 0 0 0 0 0 0]
        [1 0 0 0 0 0 0 1 1 0 0 0]
        [0 1 0 0 0 0 0 0 0 1 1 0]
        [0 1 0 0 0 0 0 0 0 1 1 0]
        [1 0 1 1 0 0 0 0 0 0 0 0]
        [0 1 0 0 1 0 0 0 0 0 0 1]
        [1 0 1 1 0 0 0 0 0 0 0 0]
        [0 0 0 0 1 1 0 0 0 0 0 1]
        [0 0 0 0 1 1 0 0 0 0 0 1]
        [0 0 0 0 0 0 1 1 1 0 0 0]
        [0 0 0 0 0 0 1 1 1 0 0 0]
        [0 0 0 0 0 0 1 0 0 1 1 0]"""
    D = DiGraph(matrix(parse_adjacency_matrix(A)))
    n = D.order()
    k = 3
    length = 2*k-1
    p = find_directed_path_with_start_vertex(D, bitmask_to_sage_graph(0, length), 0).__next__()
    # draw(D, p, layout="spring")    
        
    length = 2*k-1
    start = set()
    try:
        for p in find_subgraph_isomorphism(D, bitmask_to_sage_graph(0, length)):
            start.add(get_start_vertex(p))
            if len(start) == n: break
    except StopIteration:
        logger.info("[COUNTER] No directed path of length 2k-1 found")
    
    if len(start) != n:
        logger.info(f"[COUNTER] There is no directed path which has a start vertex in {set(range(n)) - start}")
    else:
        logger.info(f"Any vertex can be a start vertex of a directed path of length 2k-1")
    