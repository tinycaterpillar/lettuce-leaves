import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195  # replace with Kissat/CaDiCaL, etc. if desired
import random

class KIndependent:
    """
        K-independent(NP-complete):
            Given a bichromatic complete graph G whose edges are colored with T and F, and an integer k, 
            does there exist a monochromatic subgraph in color F spanned by at least k vertices?
    """
    def __init__(self, graph: nx.MultiGraph, solver=Cadical195):
        self.G = graph
        self.V = sorted(graph.nodes())
        self.E = list(graph.edges(keys=True))  # [(u,v,key), ...]
        self.pool = IDPool()
        self.solver=solver
        self._check_edge_colors()
        self.cnf_base = self._build_base()

    def select(self, v):
        return self.pool.id(("select", v))

    def _build_base(self):
        # init
        for v in self.V:
            _ = self.select(v)

        base = CNF()

        # Non-adjacent Clause: the two endpoints of a B-colored edge cannot both be selected
        for (u, v, key) in self.E:
            if self.G[u][v][key]['color'] == 'A': continue
            base.append([-self.select(u), -self.select(v)])

        return base

    def solve_for_k(self, k: int):
        cnf = CNF()
        cnf.extend(self.cnf_base.clauses)

        # At-least Clause
        lits = [self.select(u) for u in self.V]
        alk = CardEnc.atleast(lits=lits, bound=k, top_id=self.pool.top)
        self.pool.top = alk.nv         
        cnf.extend(alk.clauses)

        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()

            if not sat: return False, []

            model = set(s.get_model())
            tmp = [u for u in self.V if self.select(u) in model]
            W = [(u, v, key) for (u, v, key) in self.E if u in tmp and v in tmp]
            return True, W
    
    def find_max_k(self):
        lo, hi = 1, len(self.V)
        ans_k, ans_w = None, None
        while lo <= hi:
            mid = (lo+hi)//2
            ok, w = self.solve_for_k(mid)
            if ok:
                ans_k, ans_w = mid, w
                lo = mid + 1
            else:
                hi = mid - 1

        return ans_k, ans_w
    
    def _check_edge_colors(self):
        true_count = 0
        false_count = 0

        for u, v, k, data in self.G.edges(keys=True, data=True):
            color = data.get("color", None)
            if color not in (True, False):
                raise ValueError(
                    f"엣지 ({u}, {v}, key={k})의 color 속성이 True/False가 아닙니다: {color}"
                )
            if color is True:
                true_count += 1
            else:  # color is False
                false_count += 1

        print(f"True: {true_count}, False: {false_count}")


if __name__ == "__main__":
    G = nx.read_graph6("graph_36_4_6.g6")
    G = nx.MultiGraph(G)

    # ans_k, ans_w = KIndependent(G).find_max_k()
    # print(ans_k)
    # show_graph(G, ans_w)