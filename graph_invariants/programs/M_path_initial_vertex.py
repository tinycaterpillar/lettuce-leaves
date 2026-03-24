from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os
import sys
import argparse

from utils import draw, setup_logger, load_graphs, get_meta_data, encode
from solvers import get_non_initial_vertices

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
    logger = setup_logger(folder="log_ex", filename=f"log{os.getpid()}.log")

    path = "data/list_1737_graphs.g6"
    graphs_lis = load_graphs(path)

    G = graphs_lis[args.i]
    if G.is_vertex_transitive():
        logger.info(f"[END] Vertex transitive graph. Any vertex can be a initial vertex of a path of length 2δ")
        sys.exit()

    logger.info(f"Test {args.i}th graph in {path}: {encode(G)}")
    logger.info(f"meta data: \n{get_meta_data(path)}")
    min_degree = min(G.degree())
    n = G.order()
    logger.info(f"graph of order {n} with mindegree {min_degree}")
    
    length = 2*min_degree
    non_init = get_non_initial_vertices(G, length)
    
    if non_init:
        logger.info(f"[COUNTER] There is no directed path which has a start vertex in {non_init}, total {len(non_init)}")
    else:
        logger.info(f"[END] Any vertex can be a initial vertex of a path of length 2δ")
    