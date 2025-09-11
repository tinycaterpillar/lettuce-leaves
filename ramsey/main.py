import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195
from pysat.card import CardEnc
import tempfile
import subprocess
from itertools import combinations

from utils import show_graph_with_edge_colors, parse_kissat_output

class NRamsey:
    """ 
        NRamsey: Given integers n, t and f(later we fix t and f and seek the minimum such n), 
        does there exist an edge-coloring γ of the complete graph G(= K_n) s.t. 
        1. the clique number of the subgraph induced by color t is at most t-1 and 
        2. that of the subgraph induced by color f is at most f-1? 
    """
    def __init__(self, n: int, t: int, f: int, solver_path="./kissat", solver=Cadical195):
        self.n = n
        self.t = t
        self.f = f
        self.pool = IDPool()
        self.solver = solver
        self.base_cnf = CNF()
        self._build_base_cnf()
        self.solver_path = solver_path

    def color(self, u, v):  # edge uv를 T로 색칠
        a, b = (u, v) if u <= v else (v, u)
        return self.pool.id(("T", a, b))

    def _build_base_cnf(self):
        n, t, f = self.n, self.t, self.f

        # 변수 초기화
        for u in range(n):
            for v in range(u + 1, n):
                _ = self.color(u, v)

        # --- Clique Exclusion Constraints ---
        # forbid any T-clique of size t
        for subset in combinations(range(n), t):
            clause = [-self.color(u, v) for u, v in combinations(subset, 2)]
            self.base_cnf.append(clause)

        # forbid any F-clique of size f
        for subset in combinations(range(n), f):
            clause = [self.color(u, v) for u, v in combinations(subset, 2)]
            self.base_cnf.append(clause)

    def solve(self, Use_external=False):
        if Use_external:
            return self._external_solver(self.base_cnf)

        with self.solver(bootstrap_with=self.base_cnf.clauses) as s:
            sat = s.solve()
            if not sat:
                return False, None

            model = set(s.get_model())
            G = nx.complete_graph(self.n)
            for u in range(self.n):
                for v in range(u + 1, self.n):
                    G[u][v]["color"] = "T" if self.color(u, v) in model else "F"
            return True, G

    def _external_solver(self, cnf):
        assert self.solver_path, "Please set self.solver_path to the path of an external solver"

        with tempfile.NamedTemporaryFile(suffix=".cnf") as tmp:
            cnf.to_file(tmp.name)

            # BreakID → Kissat 파이프라인 실행
            p1 = subprocess.Popen(["./breakid", tmp.name], stdout=subprocess.PIPE)
            res = subprocess.run(
                [self.solver_path, "-q"],
                stdin=p1.stdout,
                capture_output=True, text=True
            )
            sat, model = parse_kissat_output(res.stdout)

            if not sat:
                return False, None

            G = nx.complete_graph(self.n)
            for u in range(self.n):
                for v in range(u + 1, self.n):
                    G[u][v]["color"] = "T" if self.color(u, v) in model else "F"
            return True, G

if __name__ == "__main__":
    sat, G = NRamsey(n=35, t=6, f=4).solve(Use_external=True)
    print("Is there a valid coloring?", sat)
    # if sat:
        # show_graph_with_edge_colors(G)
