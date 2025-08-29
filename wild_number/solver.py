import tempfile
import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195  # replace with Kissat/CaDiCaL, etc. if desired
from collections import defaultdict as dd
import subprocess
import os

from utils import show_graph, parse_kissat_output, Dsu
import pdb # debugger

class KWildSAT:
    """
        K-wild(NP-complete):
            Given a edge-colored multigraph G and an integer k,  
            does there exist an edge set W with |W| ≤ k such that,  
            for every color c, the subgraph induced by W ∪ {edges of color c}  
            contains a spanning tree of G?
    """
    def __init__(self, graph: nx.MultiGraph, solver_path="./kissat", solver=Cadical195):
        self.G = graph
        self.V = sorted(graph.nodes())
        self.E = list(graph.edges(keys=True))  # [(u,v,key), ...]
        self.colors = sorted(set(nx.get_edge_attributes(graph, "color").values()))
        self.pool = IDPool()
        self.solver=solver
        self.wild_lits = []
        self.dsu = dd(lambda : Dsu(len(self.V)))
        self.solver_path = solver_path

        if not os.path.isfile(solver_path):
            raise FileNotFoundError(f"Solver not found: {solver_path}")

        if len(self.V) <= 1:
            raise ValueError("Graph must have more than one vertex (non-trivial graph required).")

        if not nx.is_connected(self.G):
            raise nx.NetworkXError("Graph must be connected.")

        missing = [(u, v, key) for u, v, key, d in graph.edges(keys=True, data=True) 
                   if ('color' not in d) or (d['color'] is None)]
        if missing:
            raise ValueError(f"Every edge must have a 'color' attribute. Missing: {missing}")

        for (u, v, key) in self.E:
            cur_c = graph[u][v][key]['color']
            self.dsu[cur_c].union(u, v)
        self.cnf_base = self._build_base()


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
        for (u, v, key) in self.E:
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
    
    def solve_for_k(self, k: int, Use_external=False):
        if k < self.clb(): return False, []

        cnf = CNF()
        cnf.extend(self.cnf_base.clauses)
        
        if k == 0:
            for lit in self.wild_lits: cnf.append([-lit])
        elif k < len(self.wild_lits):
            amk = CardEnc.atmost(lits=self.wild_lits, bound=k, top_id=self.pool.top)
            self.pool.top = amk.nv  
            cnf.extend(amk.clauses)
        
        if Use_external:
            return self._external_solver(cnf)

        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()

            if not sat: return False, []

            model = set(s.get_model())
            wild_set = [(u, v, key) for (u, v, key) in self.E if self.wild(u, v, key) in model]

            return True, wild_set

    def find_min_k(self, use_external=False):
        """Binary search for the minimal k"""
        lo, hi = self.clb(), min(len(self.V) - 1, self.cub())
        ans_k, ans_w = None, None
        while lo <= hi:
            mid = (lo + hi) // 2
            ok, w = self.solve_for_k(mid, use_external)
            if ok:
                ans_k, ans_w = mid, w
                hi = mid-1
            else:
                lo = mid+1

        return ans_k, ans_w

    def clb(self):
        return max(self.dsu[c].c - 1 for c in self.colors)
    
    def cub(self):
        return sum(self.dsu[c].c - 1 for c in self.colors)
    
    # return the dip number of given edge e
    def dip(self, u, v, key=None):
        return sum(self.dsu[c].find(u) != self.dsu[c].find(v) for c in self.colors)

    def _external_solver(self, cnf):
        assert self.solver_path, "Please set self.solver_path to the path of an external solver"

        # Create a temporary CNF file (auto-deleted after the 'with' block exits)
        with tempfile.NamedTemporaryFile(suffix=".cnf") as tmp:
            cnf.to_file(tmp.name)  # Write the CNF to the temporary file

            # Run external solver (quiet mode, no statistics)
            res = subprocess.run(
                [self.solver_path, "-q", tmp.name],
                capture_output=True, text=True
            )
            sat, model = parse_kissat_output(res.stdout)

            if not sat:
                return False, []
            else:
                # Decode the witness (set of "wild" edges)
                wild_set = [(u, v, key) for (u, v, key) in self.E if self.wild(u, v, key) in model]
                return True, wild_set

        
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

    ans_k, ans_w = KWildSAT(G).find_min_k()
    # ans_k, ans_w = KWildSAT(G).find_min_k(use_external=True)

    print(ans_k)
    show_graph(G, ans_w)


