# pip install python-sat  (run once)
import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Glucose4  # replace with Kissat/CaDiCaL, etc. if desired


class KWildSAT:
    def __init__(self, graph: nx.MultiGraph):
        self.G = graph
        
        # 0) Pre-checks / collection
        self.V = list(graph.nodes())
        assert self.V, "empty graph"
        self.root = self.V[0]

        missing = [(u, v, k) for u, v, k, d in graph.edges(keys=True, data=True)
                   if ('color' not in d) or (d['color'] is None)]
        assert not missing, f"Every edge must have 'color'. Missing: {missing}"

        self.colors = sorted({d['color'] for _, _, _, d in graph.edges(keys=True, data=True)})
        self.E = list(graph.edges(keys=True))  # [(u,v,key), ...]

        # Collect undirected pairs per color
        pairs_by_color = {c: set() for c in self.colors}
        for u, v, k in graph.edges(keys=True):
            c = graph[u][v][k]['color']
            a, b = (u, v) if u <= v else (v, u)
            pairs_by_color[c].add((a, b))

        # 1) Variable pool & helper mappers
        self.pool = IDPool()

        def wid(e):  # wild(e): (u,v,key) → SAT var id
            u, v, k = e
            a, b = (u, v) if u <= v else (v, u)
            return self.pool.id(('wild', a, b, k))
        self.wid = wid

        def rid(c, u, v):  # reach(c,u,v), u!=v
            assert u != v
            return self.pool.id(('reach', c, u, v))
        self.rid = rid

        # 2) Build base CNF independent of k
        base = CNF()

        # (i) Real colored edges ⇒ immediate reachability
        for c in self.colors:
            for (a, b) in pairs_by_color[c]:
                base.append([self.rid(c, a, b)])
                base.append([self.rid(c, b, a)])

        # (ii) Wild edge ⇒ immediate reachability in every color
        for c in self.colors:
            for (u, v, k) in self.E:
                base.append([-self.wid((u, v, k)), self.rid(c, u, v)])
                base.append([-self.wid((u, v, k)), self.rid(c, v, u)])

        # (iii) Transitivity: (u→v ∧ v→w) ⇒ u→w
        for c in self.colors:
            for u in self.V:
                for v in self.V:
                    if u == v: 
                        continue
                    for w in self.V:
                        if w == u or w == v:
                            continue
                        base.append([-self.rid(c, u, v), -self.rid(c, v, w), self.rid(c, u, w)])

        # (iv) Connectivity: root reaches every vertex
        for c in self.colors:
            for v in self.V:
                if v != self.root:
                    base.append([self.rid(c, self.root, v)])

        self.cnf_base = base  # store base CNF

    def solve_for_k(self, k: int, solver_cls=Glucose4):
        """Solve using base clauses + add only the at-most-k cardinality constraint."""
        cnf = CNF()
        cnf.extend(self.cnf_base.clauses)

        wild_lits = [self.wid(e) for e in self.E]

        if k == 0:
            # Force all wild variables to False (no CardEnc needed)
            for lit in wild_lits:
                cnf.append([-lit])
        elif k < len(wild_lits):
            # Set top_id to avoid aux-var id collisions with existing variables
            amk = CardEnc.atmost(lits=wild_lits, bound=k, top_id=self.pool.top)
            cnf.extend(amk.clauses)
        # If k >= |E|, the constraint is tautological → no extra clauses

        with solver_cls(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()
            if not sat:
                return False, []
            model = set(s.get_model())
            wild_edges = [e for e in self.E if self.wid(e) in model]
            return True, wild_edges

    def find_min_k(self, max_k=None, solver_cls=Glucose4):
        """Binary search for the minimal k (upper bound defaults to |V|-1 here)."""
        lo, hi = 0, len(self.V) - 1
        ans_k, ans_W = None, []
        while lo <= hi:
            mid = (lo + hi) // 2
            ok, W = self.solve_for_k(mid, solver_cls=solver_cls)
            if ok:
                ans_k, ans_W = mid, W
                hi = mid - 1
            else:
                lo = mid + 1
        
        print(f"k={ans_k}, wild edges={ans_W}")
        return ans_k, ans_W


if __name__ == "__main__":
    G = nx.MultiGraph()
    G.add_edge(0, 1, color='red')
    G.add_edge(1, 2, color='red')
    G.add_edge(1, 3, color='red')
    G.add_edge(1, 3, color='red')
    G.add_edge(2, 3, color='blue')
    G.add_edge(3, 0, color='blue')

    KWildSAT(G).find_min_k()
