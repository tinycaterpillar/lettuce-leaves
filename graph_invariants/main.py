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

    k = random.randint(3, 5)
    n = random.randint(2*k+1, 2*k+1)
    seed = random.randint(1, 1000)
    length = 2*k-1
    logger.info(f"k {k}, n {n}, seed {seed}")
    ap = get_alternating_path(length)
    ap_rev = (((1<<length)-1)^ap)

    D = graphs.RandomRegular(2*k, n, seed=seed).eulerian_orientation()
    p1 = find_subgraph_with_vertex(D, bitmask_to_sage_graph(ap, length), 0).__next__()
    for p in range((1<<length)):
        try:
            p2 = find_subgraph_with_vertex(D, bitmask_to_sage_graph(p, length), 0).__next__()
            draw(D, [p1, p2])
        except StopIteration:
            flag = False
            logger.info(f"no alternating path with vertex {0}")

        
    

    
