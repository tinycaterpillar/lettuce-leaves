from sage.all import *
import os
import random
import sys
import argparse

from utils import draw, setup_logger, load_graphs, encode, get_meta_data
from solvers import SpanningTreeSAT

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log_ex", filename=f"log{os.getpid()}.log")
    
    path = "data/list_1742_graphs.g6"
    graphs_lis = load_graphs(path)

    G = graphs_lis[args.i]
    g6 = encode(G)
    n = G.order()

    logger.info(f"Test {args.i}th graph in {path}: {encode(G)}")
    logger.info(f"meta data: \n{get_meta_data(path)}")

    T = G.blocks_and_cuts_tree()
    B, C = G.blocks_and_cut_vertices()
    leaf_blocks, C = set(), set(C)
    for v in T.vertices():
        if v[0] == 'C' or T.degree(v) != 1: continue
        leaf_blocks.update(v[1])

    S = leaf_blocks.intersection(C)
    G.delete_vertices(leaf_blocks-C)
    
    if G.order() > 2:
        sat, E = SpanningTreeSAT(G, S).solve(external=False)
        if sat: 
            logger.info(f"[NORMAL]")
            # draw(G, V=S, E=E, name=g6, folder="pictures")
        else:
            logger.info(f"[COUNTER]")    
    else:
        logger.info(f"[End] Too small")