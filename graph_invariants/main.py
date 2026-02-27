from sage.all import *
import os
import random

from utils import draw, setup_logger, parse_adjacency_matrix
from generators import get_antidirected_path, bitmask_to_sage_graph, get_oriented_path, bitmask_to_direction_string
from solvers import find_subgraph_with_vertex

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    A = """[0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]
        [1 0 0 0 0 0 0 0 0 0 0 0 0 1 1]
        [1 0 0 0 0 0 0 0 0 0 0 0 0 1 1]
        [1 0 0 0 0 0 0 0 0 0 0 0 0 1 1]
        [0 0 0 0 0 0 0 0 0 0 1 1 1 0 0]
        [0 0 0 0 0 0 0 0 0 0 1 1 1 0 0]
        [0 0 0 0 0 0 0 0 0 0 1 1 1 0 0]
        [0 1 1 1 0 0 0 0 0 0 0 0 0 0 0]
        [0 1 1 1 0 0 0 0 0 0 0 0 0 0 0]
        [0 1 1 1 0 0 0 0 0 0 0 0 0 0 0]
        [0 0 0 0 0 0 0 1 1 1 0 0 0 0 0]
        [0 0 0 0 0 0 0 1 1 1 0 0 0 0 0]
        [0 0 0 0 0 0 0 1 1 1 0 0 0 0 0]
        [0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]
        [0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]"""
    D = DiGraph(matrix(parse_adjacency_matrix(A)))
    n = D.order()
    k = min(min(D.in_degree()), min(D.out_degree()))
    logger.info(f"Test graph with min semidegree {k}:\n{D.adjacency_matrix().str()}")
    length = 2*k-1

    v = 13
    D_ = D.copy()
    D_.delete_vertex(v)
    k_ = min(min(D_.in_degree()), min(D_.out_degree()))
    
    length_ = length-1
    for op in get_oriented_path(length_):
        p = find_subgraph_with_vertex(D, bitmask_to_sage_graph(op, length_), 1).__next__()
        draw(D, p, name=bitmask_to_direction_string(op, length_))
        
