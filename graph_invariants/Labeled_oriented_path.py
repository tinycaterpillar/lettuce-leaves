from sage.all import *
import os
import argparse

from utils import draw, setup_logger, parse_adjacency_matrix, get_meta_data, load_graphs
from generators import bitmask_to_sage_graph, get_oriented_path, bitmask_to_direction_string, orientation_with_min_semidegree
from solvers import find_subgraph_isomorphism

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=int, required=True)   # graph index
args = parser.parse_args()

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    path = "data/list_660_graphs.g6"
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
    for op in get_oriented_path(length):
        try:
            cnt = len(list(find_subgraph_isomorphism(D, bitmask_to_sage_graph(op, length))))
            logger.info(f"op {bitmask_to_direction_string(op, length)}, {cnt}")
            # draw(D, p, name=bitmask_to_direction_string(op, length))
        except MemoryError:
            logger.exception("[MEMORY_ERROR] during subgraph isomorphism")
            sys.exit()
    logger.info("[END]")
        
