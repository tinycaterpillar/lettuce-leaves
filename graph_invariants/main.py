from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os

from utils import draw, setup_logger
from solvers import decode_oriented_path, find_subgraph_isomorphism, make_oriented_path

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    k = random.randint(3, 4)
    n = random.randint(2*k+1, 2*k+10)
    seed = random.randint(1, 1000)
    length = 2*k-1
    logger.info(f"k {k}, n {n}, seed {seed}")
    op = random.randint(0, (1<<length)-1)
    
    D = graphs.RandomRegular(2*k, n, seed=seed).eulerian_orientation()
    for op in range(1<<length):
        logger.info(f"op {decode_oriented_path(op, length)}, {len(list(find_subgraph_isomorphism(D, make_oriented_path(op, length))))}")
        # p = find_subgraph_with_vertex(D, make_oriented_path(op, length), 0).__next__()
        # draw(D, p, name=decode_oriented_path(op, length), folder=f"results/{n}_{k}_{seed}")

    
