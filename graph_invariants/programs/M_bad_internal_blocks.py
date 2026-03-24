from sage.all import *
import os
import random
import argparse

from utils import draw, setup_logger, load_graphs, encode, get_meta_data
from solvers import is_bad_internal_block

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log_ex", filename=f"log{os.getpid()}.log")

    path = "data/list_1714_graphs.g6"
    graphs_lis = load_graphs(path)

    G = graphs_lis[args.i]
    

    logger.info(f"Test {args.i}th graph in {path}: {encode(G)}")
    logger.info(f"meta data: \n{get_meta_data(path)}")
    min_degree = min(G.degree())
    max_degree = max(G.degree())
    n = G.order()
    logger.info(f"graph of order {n} with mindegree {min_degree}, max_degree {max_degree}")
    
    X = [v for v in G.vertices() if G.degree(v) != max_degree]
    k = max_degree-2
    bad = is_bad_internal_block(G, X, k, is_vertex_transitive=G.is_vertex_transitive())

    if not bad and len(X) > 1:
        logger.info(f"[COUNTER] Not {k}-bad n={G.order()} X_size={len(X)}")
        # draw(G, S=X, name=g6)
    else:
        logger.info(f"[END] {k}-bad")
