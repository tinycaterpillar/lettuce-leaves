from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os

from utils import draw, setup_logger, load_graphs
from generators import orientation_with_min_semidegree, bitmask_to_sage_graph, bitmask_to_direction_string
from solvers import find_subgraph_isomorphism

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    path = "data/list_1662_graphs.g6"
    graphs = load_graphs(path)

    G = graphs[10]
    logger.info(f"Test graph: {G.graph6_string()}")
    min_degree = min(G.degree())
    D = orientation_with_min_semidegree(G, min_degree//2)
    k = min(min(D.in_degree()), min(D.out_degree()))
    length = 2*k-1
    for p in range(1<<length):
        cnt = len(list(find_subgraph_isomorphism(D, bitmask_to_sage_graph(p, length))))
        logger.info(f"op {bitmask_to_direction_string(p, length)}, {cnt}")