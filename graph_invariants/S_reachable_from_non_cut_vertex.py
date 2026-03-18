from sage.all import *
import os
import random
import sys

from utils import draw, setup_logger, decode
from solvers import reachable_at_least_k


if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    g6 = "C^"
    G = decode(g6)

    n = G.order()
    min_degree = min(G.degree())
    max_degree = max(G.degree())
    num_2 = sum(1 for d in G.degree() if d == 2)
    num_3 = sum(1 for d in G.degree() if d == 3)

    logger.info(
        f"graph of order {n} s.t.\n"
        f"g6 {g6}\n"
        f"mindegree {min_degree}\n"
        f"maxdegree {max_degree}\n"
        f"# 2-vertices {num_2}\n"
        f"# 3-vertices {num_3}"
    )

    flag = True
    for init in G.vertices():
        S = reachable_at_least_k(G, init, max_degree)

        if len(S) < n-1:
            flag = False
            logger.info(
                f"[COUNTER] init={init}, reachable_size={len(S)}, "
                f"reachable={list(S)}"
            )
            draw(G, S=S, layout="spring", name=f"init {init}")

        if G.is_vertex_transitive(): sys.exit()

    if flag: logger.info(f"[END]")