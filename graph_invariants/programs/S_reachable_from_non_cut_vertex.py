from sage.all import *
import os
import random
import sys

from utils import draw, setup_logger, decode
from solvers import reachable_at_least_k

if __name__ == "__main__":
    logger = setup_logger(folder="log", filename=f"log{os.getpid()}.log")

    g6 = "F?F~o"
    G = decode(g6)

    n = G.order()
    min_degree = min(G.degree())
    max_degree = max(G.degree())
    num_2 = sum(1 for d in G.degree() if d == 2)
    num_3 = sum(1 for d in G.degree() if d == 3)

    logger.info(
        f"graph of order {n} s.t.\n"
        f"g6 {g6}\n"
        f"mindegree {min_degree}\n"
        f"maxdegree {max_degree}\n"
        f"# 2-vertices {num_2}\n"
        f"# 3-vertices {num_3}"
    )

    cnt = 0
    for init in G.vertices():
        S = reachable_at_least_k(G, init, max_degree)

        if len(S) < n-1:
            cnt += 1
            reachable_str = "\n".join(
                f"  - v={v}, deg={G.degree(v)}" for v in sorted(S)
            )

            unreachable = [(v, G.degree(v)) for v in G.vertices() if v not in S]

            unreachable_str = "\n".join(
                f"  - v={v}, deg={d}" for v, d in unreachable
            )

            if G.degree(init) == max_degree:
                tag = "[MAX-DEGREE COUNTER]"
                sep = "=" * 60
            else:
                tag = "(counter)"
                sep = "-" * 40

            logger.info(
                f"\n{sep}\n"
                f"{tag} init={init}, deg={G.degree(init)}, reachable_size={len(S)}\n"
                f"reachable   :\n{reachable_str}\n"
                f"unreachable :\n{unreachable_str}\n"
                f"{sep}"
            )
            draw(G, S=S, layout="spring", name=f"init {init}")

        if G.is_vertex_transitive(): sys.exit()

    if cnt == 0: logger.info(f"[END]")
    else: logger.info(f"[COUNTER] {cnt}/{n}")