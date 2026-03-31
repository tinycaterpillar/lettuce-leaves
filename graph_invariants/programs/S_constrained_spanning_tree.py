from sage.all import *
import os
import random

from utils import draw, setup_logger, decode, encode
from solvers import SpanningTreeSAT

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")
    
    g6 = "F?O|_"
    G = decode(g6)
    # draw(G)

    n = G.order()
    logger.info(f"graph of order {n}")

    T = G.blocks_and_cuts_tree()
    B, C = G.blocks_and_cut_vertices()
    leaf_blocks, C = set(), set(C)
    for v in T.vertices():
        if v[0] == 'C' or T.degree(v) != 1: continue
        leaf_blocks.update(v[1])

    S = leaf_blocks.intersection(C)
    G.delete_vertices(leaf_blocks-C)
    draw(G, V=S)

    # sat, E = SpanningTreeSAT(G, S).solve(external=False)
    # if sat:
    #     draw(G, V=S, E=E)
    # else:
    #     print("UNSAT")
