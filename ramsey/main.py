import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Glucose4  # replace with Kissat/CaDiCaL, etc. if desired
from itertools import combinations
import tempfile
import subprocess

from backup.utils_for_independent import show_graph, edges_in_clique, parse_kissat_output


class NRamsey:
    """
        NRamsey: 
        Given integers n, t and f(later we fix t and f and seek the minimum such n),
        does there exist an edge-coloring γ of the complete graph G(= K_n) s.t.
        1. the clique number of the subgraph induced by color t is at most t-1 and
        2. that of the subgraph induced by color f is at most f-1?
    """
    def __init__(self, solver=Glucose4):
        self.pool = IDPool()
        self.solver=solver
    
    def color(self, u, v): # color the edge uv as T
        a, b = (u, v) if u <= v else (v, u)
        return self.pool.id(("T", a, b))
    
    def select(self, u, i): # select(u, 1): select u as a T-colored Clique
        return self.pool.id(('select', u, i))

    def solve_for_n(self, n: int, t: int, f: int):
        # init
        self.pool = IDPool()
        for u in range(n):
            for v in range(u+1, n):
                _ = self.color(u, v)

        for u in range(n):
            _, _ = self.select(u, 0), self.select(u, 1)

        cnf = CNF()

        lb = [f-1, t-1]
        # --- Bruteforce Clique Exclusion ---
        # forbid any T-clique of size t
        for subset in combinations(range(n), t):
            tmp = []
            for u, v in combinations(subset, 2):
                tmp.append(-self.color(u, v))
            cnf.append(tmp)

        # forbid any F-clique of size f
        for subset in combinations(range(n), f):
            tmp = []
            for u, v in combinations(subset, 2):
                tmp.append(self.color(u, v))
            cnf.append(tmp)
        
        cnf.to_file("problem.cnf")
        return

        with self.solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()

            if not sat: return False, None

            model = set(s.get_model())
            G = nx.complete_graph(n)
            for u in range(n):
                for v in range(u+1, n):
                    G[u][v]['color'] = 'T' if self.color(u, v) in model else 'F'
            return True, G

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

if __name__ == "__main__":
    sat, G = NRamsey().solve_for_n(36, 6, 4)
    # print(sat)
    # if sat: show_graph(G)