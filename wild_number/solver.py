import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Glucose4  # replace with Kissat/CaDiCaL, etc. if desired

from utils import show_graph
import pdb # debugger

class KWildSAT:
    """
        K-wild(NP-complete):
            Given a edge-colored multigraph G and an integer k,  
            does there exist an edge set W with |W| ≤ k such that,  
            for every color c, the subgraph induced by W ∪ {edges of color c}  
            contains a spanning tree of G?
    """
    def __init__(self, graph: nx.MultiGraph, solver=Glucose4):
        self.G = graph
        self.V = sorted(graph.nodes())
        self.E = list(graph.edges(keys=True))  # [(u,v,key), ...]
        self.colors = sorted(set(nx.get_edge_attributes(graph, "color").values()))
        self.pool = IDPool()
        self.solver=solver
        self.wild_lits = []
        self.cnf_base = self._build_base()

        assert len(self.V) > 1, "G must not be trivial"
        assert nx.is_connected(self.G), "G must be connected"

        missing = [(u, v, key) for u, v, key, d in graph.edges(keys=True, data=True)
                   if ('color' not in d) or (d['color'] is None)]
        assert not missing, f"Every edge must have 'color'. Missing: {missing}"


    def wild(self, u, v, key):
        a, b = (u, v) if u <= v else (v, u)
        return self.pool.id(('wild', a, b, key))


    def dist(self, c, v, t): # dist(s, v) in color c <= t where s is some starting point
        return self.pool.id(('dist', c, v, t))


    def tseitin(self, a, b): # tseitin(a, b) <=> a and b
        # tseitin(dist(c, u, t), wild(u, v, key)) == tseitin(wild(u, v, key), dist(c, u, t))
        return self.pool.id(('tseitin', min(a,b), max(a,b))) 


    # Build base CNF independent of k
    def _build_base(self):
        # init
        for (u, v, key) in self.E: # 이 부분 최적화 더 가능
            self.wild_lits.append(self.wild(u, v, key))

        for c in self.colors:
            for v in self.V:
                for t in range(len(self.V)):
                    _ = self.dist(c, v, t)

        base = CNF()
        n = len(self.V)

        # Connectivity
        for c in self.colors:
            # Exactly-one starting point Clause: For each color c, there is only one starting point
            am1 = CardEnc.equals(lits=[self.dist(c, v, 0) for v in self.V], bound=1, encoding=1, top_id=self.pool.top)
            self.pool.top = am1.nv  # update top_id
            base.extend(am1.clauses)

            # Monotonicity Clause: If dist(c, v, t) is true, then dist(c, v, t+1) is true
            for v in self.V:
                for t in range(n-1):
                    base.append([-self.dist(c, v, t), self.dist(c, v, t+1)])

            # Reachability propagation Clause: If dist(c, v, t+1) is true, then
            # dist(c, v, t) or
            # there is a color-c reachable neighbor u of v s.t. dist(c, u, t) or
            # there is a wild-edge reachable neighbor u of v s.t. dist(c, u, t)
            for v in self.V:
                for t in range(n-1):
                    tmp = [-self.dist(c, v, t+1), self.dist(c, v, t)]

                    for _, u, key, data in self.G.edges(v, keys=True, data=True):
                        # color-c neighbors
                        if data['color'] == c:
                            tmp.append(self.dist(c, u, t))
                        # wild neighbors
                        else:
                            # Tseitin: y ↔ (dist(c,u,t) ∧ wild(u,v,key))
                            y = self.tseitin(self.dist(c, u, t), self.wild(u, v, key))
                            tmp.append(y)

                            base.append([-y, self.dist(c, u, t)])
                            base.append([-y, self.wild(u, v, key)])
                            base.append([y, -self.dist(c, u, t), -self.wild(u, v, key)])
                    base.append(tmp)

            # Connectivity Clause: for each color c, the graph G must be color-c connected
            for v in self.V:
                base.append([self.dist(c, v, n-1)])

        return base


    def solve_for_k(self, k: int):
        cnf = CNF()
        cnf.extend(self.cnf_base.clauses)
        
        if k == 0:
            for lit in self.wild_lits: cnf.append([-lit])
        elif k < len(self.wild_lits):
            amk = CardEnc.atmost(lits=self.wild_lits, bound=k, top_id=self.pool.top)
            self.pool.top = amk.nv  
            cnf.extend(amk.clauses)

        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()
            if not sat: return False, []

            model = set(s.get_model())
            wild_set = [(u, v, key) for (u, v, key) in self.E if self.wild(u, v, key) in model]

            return True, wild_set

    def find_min_k(self):
        """Binary search for the minimal k"""
        lo, hi = 0, len(self.V) - 1
        ans_k, ans_w = None, None
        while lo <= hi:
            mid = (lo + hi) // 2
            ok, w = self.solve_for_k(mid)
            if ok:
                ans_k, ans_w = mid, w
                hi = mid-1
            else:
                lo = mid+1

        return ans_k, ans_w

    # Debugging: Decode a single literal into human-readable form
    def decode_clause(self, lit):
        obj = self.pool.obj(abs(lit))
        sign = "" if lit > 0 else "¬"
        if obj is None:  # auxiliary variables
            return f"{sign}<aux:{abs(lit)}>"
        else:
            return f"{sign}{obj}"

    # Debugging: Decode CNF into human-readable form
    def decode_cnf(self, cnf):
        for i, clause in enumerate(cnf.clauses):
            readable = [self.decode_clause(lit) for lit in clause]
            print(f"Clause {i}: {' ∨ '.join(readable)}")

    # Debugging: Simplify CNF under a set of assumptions and print the resulting clauses
    def simplify_cnf_with_assumptions(self, cnf: CNF, assumptions):
        simplified = CNF()
        assumptions = set(assumptions)
        flag = False
        for clause in cnf.clauses:
            if any(lit in assumptions for lit in clause): continue
            else:
                new_clause = [lit for lit in clause if -lit not in assumptions]
                if len(new_clause) == 1 and -new_clause[0] not in assumptions:
                    assumptions.add(new_clause[0])
                    flag = True
                else:
                    simplified.append(new_clause)

        if flag:
            self.simplify_cnf_with_assumptions(simplified, assumptions)
        else:
            print("simplify_cnf_with_assumptions: ")
            self.decode_cnf(simplified)


if __name__ == "__main__":
    G = nx.MultiGraph()
    G.add_edges_from([
        (2, 3, {'color': 'A'}),
        (3, 4, {'color': 'A'}),

        (1, 2, {'color': 'B'}),
        (1, 7, {'color': 'B'}),
        (0, 7, {'color': 'B'}),
        (0, 5, {'color': 'B'}),
        (5, 6, {'color': 'B'}),

        (0, 1, {'color': 'C'}),
        (0, 3, {'color': 'C'}),
        (0, 4, {'color': 'C'}),

        (0, 2, {'color': 'D'}),
        (0, 6, {'color': 'D'}),
        (6, 7, {'color': 'D'}),
        (4, 5, {'color': 'D'}),
    ])

    show_graph(G)
    ans_k, ans_w = KWildSAT(G).find_min_k()

    print(ans_k)
    show_graph(G, ans_w)

