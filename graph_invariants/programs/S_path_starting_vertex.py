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

    g6 = "SwCW?CB???_B??????G?Cw?oBa_?y_w@_"
    G = decode(g6)

    min_degree = min(G.degree())
    n = G.order()
    logger.info(f"graph of order {n} with mindegree {min_degree}")
    
    length = 2*min_degree
    P = graphs.PathGraph(length+1)
    flag = True
    start = set()
    try:
        for p in find_subgraph_isomorphism(G, P):
            start.update(get_start_vertex(p))
            if len(start) == n: break
    except MemoryError:
            logger.exception("[MEMORY_ERROR] during subgraph isomorphism")
            sys.exit()

    independence_number = G.independent_set(value_only=True)

    if len(start) != n:
        tmp = set(range(n)) - start
        logger.info(f"[COUNTER] There is no directed path which has a start vertex in {tmp}, total {len(tmp)}")
        # draw(G, S=tmp, layout='circular', name=g6, folder='pictures')
        draw(G, S=tmp, layout='spring', name=g6)
    else:
        logger.info(f"[END] Any vertex can be a start vertex of a directed path of length 2k-1")
