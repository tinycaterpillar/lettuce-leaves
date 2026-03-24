from sage.all import *
import os
import random

from utils import draw, setup_logger, decode
from solvers import get_non_initial_vertices


def get_start_vertex(P):
    ret = []
    for v in P.vertices():
        if P.degree(v) != 1: continue
        ret.append(v)
    return ret


if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    g6 = "DFw"
    G = decode(g6)

    min_degree = min(G.degree())
    n = G.order()
    logger.info(f"graph of order {n} with mindegree {min_degree}")
    
    length = 2*min_degree
    non_init = get_non_initial_vertices(G, length)

    if non_init:
        logger.info(f"[COUNTER] There is no directed path which has a start vertex in {non_init}, total {len(non_init)}")
        # draw(G, S=non_init, name=g6, folder='pictures')
        draw(G, S=non_init, name=g6)
    else:
        logger.info(f"[END] Any vertex can be a initial vertex of a path of length 2δ")
