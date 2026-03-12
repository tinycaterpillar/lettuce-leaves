from sage.all import *
import os
import random

from utils import draw, setup_logger, parse_adjacency_matrix, decode
from generators import get_antidirected_path, bitmask_to_sage_graph, get_oriented_path, bitmask_to_direction_string
from solvers import find_subgraph_isomorphism, find_directed_path_with_start_vertex


def get_start_vertex(P):
    ret = []
    for v in P.vertices():
        if P.degree(v) != 1: continue
        ret.append(v)
    return ret


if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")
    
    g6 = "L???F~}~f{^o~_"
    G = decode(g6)
    draw(G)
    # A = """[0 0 1 1 0 1 0 0 0 0 0 0]
    #     [1 0 0 0 0 0 0 1 1 0 0 0]
    #     [0 1 0 0 0 0 0 0 0 1 1 0]
    #     [0 1 0 0 0 0 0 0 0 1 1 0]
    #     [1 0 1 1 0 0 0 0 0 0 0 0]
    #     [0 1 0 0 1 0 0 0 0 0 0 1]
    #     [1 0 1 1 0 0 0 0 0 0 0 0]
    #     [0 0 0 0 1 1 0 0 0 0 0 1]
    #     [0 0 0 0 1 1 0 0 0 0 0 1]
    #     [0 0 0 0 0 0 1 1 1 0 0 0]
    #     [0 0 0 0 0 0 1 1 1 0 0 0]
    #     [0 0 0 0 0 0 1 0 0 1 1 0]"""
    # D = DiGraph(matrix(parse_adjacency_matrix(A)))
    # n = D.order()
    # k = 3
    # length = 2*k-1
    # p = find_directed_path_with_start_vertex(D, bitmask_to_sage_graph(0, length), 0).__next__()
    # # draw(D, p, layout="spring")    
    # min_degree = min(G.degree())
    # n = G.order()
    # length = 2*min_degree
    # P = graphs.PathGraph(length+1)
    # flag = True
    # start = set()
    # try:
    #     for p in find_subgraph_isomorphism(G, P):
    #         start.update(get_start_vertex(p))
    #         if len(start) == n: break
    # except MemoryError:
    #         logger.exception("[MEMORY_ERROR] during subgraph isomorphism")
    #         sys.exit()
    
    # if len(start) != n:
    #     tmp = set(range(n)) - start
    #     logger.info(f"[COUNTER] There is no directed path which has a start vertex in {tmp}, total {len(tmp)}")
    # else:
    #     logger.info(f"Any vertex can be a start vertex of a directed path of length 2k-1")
    