from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os

from utils import draw, setup_logger
from solvers import find_subgraph_with_vertex

def oriented_path_iterator(length):
    for directions in product([0, 1], repeat=length):
        name = ''.join('→' if d == 0 else '←' for d in directions)
        G = DiGraph(
            [(i, i+1) if d == 0 else (i+1, i)
             for i, d in enumerate(directions)],
            name=name
        )
        yield G


if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    k = random.randint(3, 6)
    n = random.randint(2*k+1, 2*k+5)
    seed = random.randint(1, 1000)
    k = 5; n = 12; seed = 311
    logger.info(f"k {k}, n {n}, seed {seed}")
    length = 2*k-1
    
    D = graphs.RandomRegular(2*k, n, seed=seed).eulerian_orientation()
    for v in D.vertices():
        sum = 0
        for p in oriented_path_iterator(length):
            cp = find_subgraph_with_vertex(D, p, v).__next__()
            if cp:
                sum += 1
        print(f"Vertex: {v}, sum: {sum}")
        logger.info(f"Vertex: {v}, sum: {sum}")
            
    