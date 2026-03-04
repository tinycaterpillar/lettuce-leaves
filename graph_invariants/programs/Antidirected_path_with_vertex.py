from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os
import argparse

from utils import draw, setup_logger, load_graphs
from generators import orientation_with_min_semidegree, bitmask_to_sage_graph, bitmask_to_direction_string, get_antidirected_path
from solvers import find_subgraph_isomorphism

def get_ends(P):
    ret = []
    for v in P.vertices():
        if P.degree(v) > 1: continue
        ret.append(v)
    return ret

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    path = "data/list_2000_graphs.g6"
    graphs = load_graphs(path)

    G = graphs[args.i]
    logger.info(f"Test {args.i}th graph in {path}: {G.graph6_string()}")
    min_degree = min(G.degree())
    n = G.order()
    D = orientation_with_min_semidegree(G, min_degree//2)
    k = min(min(D.in_degree()), min(D.out_degree()))
    logger.info(f"Orientation of {G.graph6_string()} with min semidegree {k}:\n{D.adjacency_matrix().str()}")
    
    length = 2*k-1
    ap = get_antidirected_path(length)
    ends = set()
    try:
        for p in find_subgraph_isomorphism(D, bitmask_to_sage_graph(ap, length)):
            ends.update(get_ends(p))
            if len(ends) == n: break
    except StopIteration:
        logger.info("[COUNTER] No antidirected path of length 2k-1 found")
    if len(ends) != n:
        logger.info(f"[COUNTER] There is no antidirtected path which has a endvertex in {set(range(n)) - ends}")
    else:
        logger.info(f"Any vertex can be an endvertex of a antidirected path")
    
