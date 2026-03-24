from sage.all import *

from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195
import tempfile
import subprocess

# from utils import parse_kissat_output

class SpanningTreeSAT:
    """
    Input: A simple connected graph G with S ⊂ V(G)
    Output: A spanning tree T of G s.t. every leaf of T is in S
    """
    def __init__(self, G_sage, S=set(), solver=Cadical195):
        assert  G_sage.is_connected(), "G must be connected a"
        self.G = G_sage
        self.V = G_sage.vertices()
        self.E = [self._canon_edge(e) for e in self.G.edges(labels=False)]
        self.S = S
        self.pool = IDPool()
        self.solver = solver
        self.solver_path = "./external_program/kissat"

    def var(self, e):
        return self.pool.id(("chosen", e)) # c for choose

    def dist(self, v, t):
        return self.pool.id(("dist", v, t))
    
    def _canon_edge(self, e):
        u, v = e
        return (u, v) if u <= v else (v, u)

    def aux(self, a, b):
        return self.pool.id(("aux_and", a, b))

    def _build_cnf(self) -> CNF:
        self.pool = IDPool()
        cnf = CNF()
        n = len(self.V)

        # (1) every leaf of T is in S
        for v in self.V:
            if v in self.S: continue

            inc_v = [self.var(e) for e in self.E if v in e]
            if len(inc_v) < 2: return cnf
            enc = CardEnc.atleast(lits=inc_v, bound=2, encoding=1, top_id=self.pool.top)
            self.pool.top = enc.nv
            cnf.extend(enc.clauses)

        # (2) exactly n-1 edges
        lits = [self.var(e) for e in self.E]
        enc = CardEnc.equals(lits=lits, bound=len(self.V)-1, top_id=self.pool.top)
        self.pool.top = enc.nv
        cnf.extend(enc.clauses)

        # (3) connectedness
        # dist(v, t): v is reachable from root using at most t chosen edges
        root = self.V[0]
        cnf.append([self.dist(root, 0)])  # root is reachable at step 0
        for v in self.V:
            if v != root:
                cnf.append([-self.dist(v, 0)])  # no other vertex is reachable at step 0

        # monotonicity: dist(v,t) -> dist(v,t+1)
        for v in self.V:
            for t in range(n - 1):
                cnf.append([-self.dist(v, t), self.dist(v, t + 1)])

        # propagation:
        # dist(v,t+1) -> dist(v,t) or exists neighbor u with dist(u,t) and chosen(u,v)
        for v in self.V:
            for t in range(n - 1):
                clause = [-self.dist(v, t + 1), self.dist(v, t)]

                # assumes self.G.neighbors(v) is available
                for u in self.G.neighbors(v):
                    e = self._canon_edge((u, v))
                    x = self.var(e)

                    # y <-> (dist(u,t) and x)
                    y = self.aux(self.dist(u, t), x)

                    cnf.append([-y, self.dist(u, t)])
                    cnf.append([-y, x])
                    cnf.append([y, -self.dist(u, t), -x])

                    clause.append(y)

                cnf.append(clause)

        # every vertex must be reachable within n-1 steps
        for v in self.V:
            cnf.append([self.dist(v, n - 1)])
        
        return cnf
    
    def _external_solver(self, cnf):
        assert self.solver_path, "Please set self.solver_path to the path of an external solver"
        
        with tempfile.NamedTemporaryFile(suffix=".cnf") as tmp:
            cnf.to_file(tmp.name)
            tmp.flush()

            res = subprocess.run(
                [self.solver_path, tmp.name],
                capture_output=True, text=True
            )

            sat, model = parse_kissat_output(res.stdout)
            if not sat:
                return False, None
            return True, [e for e in self.E if self.var(e) in model]

    def solve(self, external=True):
        cnf = self._build_cnf()

        if external: return self._external_solver(cnf)
            
        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()
            if not sat:
                return False, None
            model = set(s.get_model())
            return True, [e for e in self.E if self.var(e) in model]


if __name__ == "__main__":
    g6 = "_?????????????????????????O??O?K??@???GG@???G?????B?C?A?@??_??ABF??G?A??OB??C?K??GCG"
    G = Graph(g6)
    sat, edges = SpanningTreeSAT(G).solve()