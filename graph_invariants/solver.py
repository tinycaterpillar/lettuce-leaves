import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195
import tempfile
import subprocess

from utils import parse_kissat_output

class ChromaticNumberSAT:
    """
    Input: simple graph G
    Output: chromatic number χ(G)
    """
    def __init__(self, graph: nx.Graph, solver=Cadical195):
        self.G = graph
        self.V = sorted(graph.nodes())
        self.pool = IDPool()
        self.solver = solver
        self.solver_path = "./external_program/kissat"

    def var(self, v, i):
        return self.pool.id(("c", v, i))

    def _build_cnf_for_k(self, k: int) -> CNF:
        self.pool = IDPool()
        cnf = CNF()

        # ensure vars exist
        for v in self.V:
            for i in range(k):
                _ = self.var(v, i)

        # (1) exactly one color per vertex
        for v in self.V:
            lits = [self.var(v, i) for i in range(k)]
            enc = CardEnc.equals(lits=lits, bound=1, top_id=self.pool.top)
            self.pool.top = enc.nv
            cnf.extend(enc.clauses)

        # (2) proper coloring constraints
        for u, v in self.G.edges():
            for i in range(k):
                cnf.append([-self.var(u, i), -self.var(v, i)])

        return cnf
    
    def _external_solver(self, cnf, quick):
        assert self.solver_path, "Please set self.solver_path to the path of an external solver"
        
        with tempfile.NamedTemporaryFile(suffix=".cnf") as tmp:
            cnf.to_file(tmp.name)
            tmp.flush()

            res = subprocess.run(
                [self.solver_path, tmp.name],
                capture_output=True, text=True
            )

            sat, model = parse_kissat_output(res.stdout, quick)
            return sat, model

    def _solve_k(self, k: int, external, quick):
        cnf = self._build_cnf_for_k(k)

        if external: return self._external_solver(cnf, quick)
            
        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()
            if not sat:
                return False, None
            model = set(s.get_model())
            coloring = [] if quick else self._extract_coloring(k, model)
            return True, coloring

    def _extract_coloring(self, k: int, model: set[int]) -> dict:
        coloring = {}
        for v in self.V:
            for i in range(k):
                if self.var(v, i) in model:
                    coloring[v] = i
                    break
        return coloring

    @staticmethod
    def greedy_upper_bound(G: nx.Graph) -> int:
        col = nx.coloring.greedy_color(G)
        return 1 + max(col.values())

    @staticmethod
    def clique_lower_bound(G: nx.Graph) -> int:
        clique = nx.algorithms.approximation.max_clique(G)
        return len(clique)

    def chromatic_number(self, external=True, quick=False):
        n = len(self.V)
        if n == 0:
            return 0, {}

        # bounds
        lo = max(1, self.clique_lower_bound(self.G))
        hi = min(n, self.greedy_upper_bound(self.G))

        best_k, best_coloring = None, None
        while lo <= hi:
            mid = (lo + hi) // 2
            ok, coloring = self._solve_k(mid, external=external, quick=quick)
            if ok:
                best_k, best_coloring = mid, coloring
                hi = mid - 1
            else:
                lo = mid + 1

        return best_k, best_coloring


if __name__ == "__main__":
    pass    