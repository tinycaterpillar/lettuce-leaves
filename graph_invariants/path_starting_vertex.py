from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os
import argparse

from utils import draw, setup_logger, load_graphs, get_meta_data, encode
from generators import orientation_with_min_semidegree, bitmask_to_sage_graph, bitmask_to_direction_string, get_antidirected_path
from solvers import find_subgraph_isomorphism

def get_start_vertex(P):
    ret = []
    for v in P.vertices():
        if P.degree(v) != 1: continue
        ret.append(v)
    return ret

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    path = "data/list_488_graphs.g6"
    graphs_lis = load_graphs(path)

    G = graphs_lis[args.i]
    logger.info(f"Test {args.i}th graph in {path}: {encode(G)}")
    logger.info(f"meta data: \n{get_meta_data(path)}")
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
    
    if len(start) != n:
        tmp = set(range(n)) - start
        logger.info(f"[COUNTER] There is no directed path which has a start vertex in {tmp}, total {len(tmp)}")
        draw(G)
    else:
        logger.info(f"Any vertex can be a start vertex of a directed path of length 2k-1")
    