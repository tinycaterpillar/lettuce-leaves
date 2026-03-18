from sage.all import *
import os
import random
import sys
import argparse

from utils import draw, setup_logger, load_graphs, encode, get_meta_data
from solvers import reachable_at_least_k

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log_ex", filename=f"log{os.getpid()}.log")

    path = "data/list_179_graphs.g6"
    graphs_lis = load_graphs(path)

    G = graphs_lis[args.i]
    n = G.order()
    min_degree = min(G.degree())
    max_degree = max(G.degree())
    num_2 = sum(1 for d in G.degree() if d == 2)
    num_3 = sum(1 for d in G.degree() if d == 3)

    logger.info(f"Test {args.i}th graph in {path}: {encode(G)}")
    logger.info(f"meta data: \n{get_meta_data(path)}")
    logger.info(
        f"graph of order {n} s.t.\n"
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
            # draw(G, S=S, layout="spring", name=f"init {init}")

        if G.is_vertex_transitive(): sys.exit()

    if flag: logger.info(f"[END]")