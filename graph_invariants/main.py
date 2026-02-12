from sage.all import *
from itertools import product
from tqdm import tqdm
import random
import os

from utils import draw, setup_logger
from solvers import contains_subgraph_through_vertex

def oriented_path_iterator(length):
    for directions in product([0, 1], repeat=length):
        name = ''.join('→' if d == 0 else '←' for d in directions)
        G = DiGraph(
            [(i, i+1) if d == 0 else (i+1, i)
             for i, d in enumerate(directions)],
            name=name
        )
        yield G

def exp():
    k = random.randint(3, 5)
    n = random.randint(2*k+1, 20)
    seed = random.randint(1, 1000)
    logger.info(f"k {k}, n {n}, seed {seed}")
    length = 2*k-1


    D = graphs.RandomRegular(2*k, n, seed=seed).eulerian_orientation()
    for v in D.vertices():
        for p in oriented_path_iterator(length):
            if contains_subgraph_through_vertex(D, p, v): continue
            logger.info(f"[COUNTER] k {k}, n {n}, seed {seed}, p {p}, v {v}")

    logger.info(f"[Done] k {k}, n {n}, seed {seed}, p {p}")


if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    for i in range(100):
        exp()