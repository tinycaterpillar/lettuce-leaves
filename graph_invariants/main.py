from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os

from utils import draw, setup_logger
from generators import get_alternating_path, bitmask_to_sage_graph, bitmask_to_direction_string
from solvers import find_subgraph_isomorphism, find_subgraph_with_vertex

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    k = random.randint(3, 10)
    n = random.randint(2*k+1, 2*k+100)
    seed = random.randint(1, 1000)
    length = 2*k-1
    logger.info(f"k {k}, n {n}, seed {seed}")
    ap = get_alternating_path(length)
    
    D = graphs.RandomRegular(2*k, n, seed=seed).eulerian_orientation()
    flag = True
    for v in D.vertices():
        try:
            p = find_subgraph_with_vertex(D, bitmask_to_sage_graph(ap, length), v).__next__()
            # draw(D, p, name=bitmask_to_direction_string(ap, length)+f" with vertex {v}")
        except StopIteration:
            flag = False
            logger.info(f"no alternating path with vertex {v}")
    if flag:
        logger.info("alternating path exists for all vertices")

    
  

    
