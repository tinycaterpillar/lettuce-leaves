from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os
import argparse

from utils import draw, setup_logger, load_graphs, get_meta_data
from generators import orientation_with_min_semidegree, bitmask_to_sage_graph, bitmask_to_direction_string, get_antidirected_path
from solvers import find_subgraph_isomorphism

def get_start_vertex(P):
    for v in P.vertices():
        if P.in_degree(v) != 0: continue
        if P.out_degree(v) != 1: continue
        return v
    raise RuntimeError("No start vertex found")

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log3", filename=f"log{os.getpid()}.log")

    path = "data/list_1775_graphs.g6"
    graphs = load_graphs(path)

    G = graphs[args.i]
    logger.info(f"Test {args.i}th graph in {path}: {G.graph6_string()}")
    logger.info(f"meta data: \n{get_meta_data(path)}")
    min_degree = min(G.degree())
    n = G.order()
    D = orientation_with_min_semidegree(G, min_degree//2)
    k = min(min(D.in_degree()), min(D.out_degree()))
    logger.info(f"Orientation of {G.graph6_string()} with min semidegree {k}:\n{D.adjacency_matrix().str()}")
    
    length = 2*k-1
    flag = True
    start = set()
    try:
        for p in find_subgraph_isomorphism(D, bitmask_to_sage_graph(0, length)):
            start.add(get_start_vertex(p))
            if len(start) == n: break
    except MemoryError:
            logger.exception("[MEMORY_ERROR] during subgraph isomorphism")
            sys.exit()
    
    if len(start) != n:
        logger.info(f"[COUNTER] There is no directed path which has a start vertex in {set(range(n)) - start}")
    else:
        logger.info(f"Any vertex can be a start vertex of a directed path of length 2k-1")
    