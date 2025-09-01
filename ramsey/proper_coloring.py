import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195  # replace with Kissat/CaDiCaL, etc. if desired
import random
from collections import defaultdict as dd

from backup.utils_for_independent import show_graph

class KProperColoring:
    """
        K-proper-vertex coloring(NP-complete):
            Given a bichromatic complete graph G whose edges are colored either T or F, and an integer k, 
            does there exist a proper k-coloring c s.t. the two endpoints of every T-colored edge receive differnt colors?
    """
    def __init__(self, graph: nx.MultiGraph, solver=Cadical195):
        self.G = graph
        self.V = sorted(graph.nodes())
        self.E = list(graph.edges(keys=True))  # [(u,v,key), ...]
        self.pool = IDPool()
        self.solver=solver

    def color(self, v, i): # color the vertex v as i
        return self.pool.id(("color", v, i))

    def solve_for_k(self, k: int):
        # init
        self.pool = IDPool()
        for v in self.V:
            for i in range(k):
                _ = self.color(v, i)

        cnf = CNF()

        # Exactly-one Clause
        for v in self.V:
            lits = [self.color(v, i) for i in range(k)]
            eq1 = CardEnc.equals(lits=lits, bound=1, top_id=self.pool.top)
            self.pool.top = eq1.nv         
            cnf.extend(eq1.clauses)

        # Non-adjacent Clause
        for (u, v, key) in self.E:
            if G[u][v][key]['color'] == 'F': continue
            for i in range(k):
                cnf.append([-self.color(u, i), -self.color(v, i)])

        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()

            if not sat: return False, None

            model = set(s.get_model())
            self.assign_colors(k, model)
            return True, model
    
    def find_min_k(self):
        lo, hi = 1, len(self.V)
        ans_k, ans_model = None, None
        while lo <= hi:
            mid = (lo+hi)//2
            ok, model = self.solve_for_k(mid)
            if ok:
                ans_k, ans_model = mid, model
                hi = mid - 1
            else:
                lo = mid + 1

        self.assign_colors(ans_k, ans_model)
        return ans_k, ans_model
    
    def assign_colors(self, k: int, model: set[int]) -> dict:
        for v in self.V:
            for i in range(k):
                if self.color(v, i) in model:
                    self.G.nodes[v]["color"] = i
                    break


if __name__ == "__main__":
    G = nx.complete_graph(8, create_using=nx.MultiGraph)
    
    random.seed(123)
    numb = 5
    edges = list(G.edges(keys=True))
    B_edges = random.sample(edges, numb)
    for u, v, k in G.edges(keys=True): G[u][v][k]['color'] = 'T'
    for u, v, k in B_edges: G[u][v][k]['color'] = 'F'

    ans_k, ans_w = KProperColoring(G).find_min_k()
    show_graph(G)