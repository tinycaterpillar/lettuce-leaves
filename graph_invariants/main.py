from sage.all import *
import os

from utils import draw, setup_logger, parse_adjacency_matrix
from generators import get_antidirected_path, bitmask_to_sage_graph, get_oriented_path, bitmask_to_direction_string
from solvers import find_subgraph_isomorphism

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    A = """[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0]
[0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0]
[0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0]
[0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0]
[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1]
[0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0]
[1 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]
[1 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]
[1 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]
[1 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0]
[0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0]
[0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0]
[0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0]"""
    D = DiGraph(matrix(parse_adjacency_matrix(A)))
    n = D.order()
    k = min(min(D.in_degree()), min(D.out_degree()))
    logger.info(f"Test graph with min semidegree {k}:\n{D.adjacency_matrix().str()}")
    length = 2*k

    ap = get_antidirected_path(length)
    p = find_subgraph_isomorphism(D, bitmask_to_sage_graph(ap, length)).__next__()
    draw(D, p)
        
