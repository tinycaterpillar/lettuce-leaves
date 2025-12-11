import os
import networkx as nx
import time
import tempfile
import signal
import subprocess
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195
from sage.all import Graph
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from utils import *
from db_utils import hog_g6, determine_status

class StrongCliqueIndex:
    """Compute ω_S(G) = ω(L(G)²) using SAT distance constraints."""

    def __init__(self, G: nx.Graph, solver=Cadical195):
        L = nx.line_graph(G)
        dist = dict(nx.all_pairs_shortest_path_length(L, cutoff=2))
        self.V = list(L.nodes())
        self.max_deg = max(dict(G.degree()).values())
        self.pool = IDPool()
        self.solver = solver
        self.time_limit = 30
        self.solver_path="./external_program/kissat"
        base = CNF()

        for v in self.V:
            _ = self.select(v)

        # forbid selecting pairs farther than distance 2 in L(G)
        for i, u in enumerate(self.V):
            for v in self.V[i + 1:]:
                if dist[u].get(v, float("inf")) > 2:
                    base.append([-self.select(u), -self.select(v)])

        self.cnf_base = base
    
    def __del__(self):
        """
        Delete all temporary files created by _external_solver.
        """
        if not hasattr(self, "_temp_files"):
            return

        for path in self._temp_files:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
        self._temp_files.clear()

    def select(self, v):
        return self.pool.id(("select", v))

    def solve_for_k(self, k: int, Use_external=False, quick=False):
        if len(self.V) < k: return SatStatus.UNSAT, []

        cnf = CNF()
        cnf.extend(self.cnf_base.clauses)

        lits = [self.select(v) for v in self.V]
        eqk = CardEnc.equals(lits=lits, bound=k, top_id=self.pool.top)
        self.pool.top = eqk.nv
        cnf.extend(eqk.clauses)

        if Use_external:
            return self._external_solver(cnf, quick=quick)

        with self.solver(bootstrap_with=cnf.clauses) as s:
            if not s.solve():
                return SatStatus.UNSAT, []
            model = set(s.get_model())
            selected = [v for v in self.V if self.select(v) in model]
            return SatStatus.SAT, selected

    def find_max_k(self, Use_external=False):
        lo, hi = 1, len(self.V)
        best_k, payload = 0, []
        while lo <= hi:
            mid = (lo + hi) // 2
            satus, tmp_payload  = self.solve_for_k(mid, Use_external, quick=True)
            if satus == SatStatus.SAT:
                best_k, payload  = mid, tmp_payload 
                lo = mid + 1
            elif satus == SatStatus.UNSAT:
                hi = mid - 1
            else:
                raise ValueError(f"Unexpected SAT status: {satus.name}")

        if Use_external:
            _, model = parse_kissat_file(payload, quick=False)
            model = set(model)
            payload = [v for v in self.V if self.select(v) in model]
        return best_k, payload

    def _external_solver(self, cnf, quick=False):
        assert self.solver_path, "Please set self.solver_path to the path of an external solver"

        # Create temporary CNF and output files (kept for later cleanup)
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".cnf", delete=False) as cnf_file, \
             tempfile.NamedTemporaryFile(mode="w+", suffix=".out", delete=False) as out_file:

            cnf_path = cnf_file.name
            out_path = out_file.name

            # Track temporary files for cleanup when the object is destroyed
            if not hasattr(self, "_temp_files"):
                self._temp_files = []
            self._temp_files.extend([cnf_path, out_path])

            # Write CNF clauses to the temporary file
            cnf.to_file(cnf_path)
            cnf_file.flush()

        # Launch Kissat as a separate process in a new session
        # (this allows us to kill the entire process group if it hangs)
        with open(out_path, "w") as f:
            proc = subprocess.Popen(
                [self.solver_path, cnf_path],
                stdout=f,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # ensures a new process group
            )

            try:
                proc.wait(timeout=self.time_limit)
            except subprocess.TimeoutExpired:
                # 🔥 Kill the entire process group if timeout occurs
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()  # reap the zombie process
                return SatStatus.TIMEOUT, []

        # Kissat standard exit codes: 10 = SAT, 20 = UNSAT
        if proc.returncode == 10:
            status, model = parse_kissat_file(out_path, quick=quick)
            if quick:
                return status, out_path
            selected = [v for v in self.V if self.select(v) in model]
            return status, selected
        elif proc.returncode == 20:
            return SatStatus.UNSAT, []
        else:
            # Any other exit code is treated as an error
            return SatStatus.ERROR, []


if __name__ == "__main__":
    # Hard to Calculate
    # graphs = load_graphs("data/db_data/list_215_graphs_151_to_160.g6")
    # graph, best_sel = graphs[48], []

    graphs = load_graphs("data/db_data_201_to_250/list_306_graphs_239_to_240.g6")
    graph, best_sel = graphs[-1], []

    # graph, best_set = decode("DLo"), []

    obj = StrongCliqueIndex(graph)
    delta = obj.max_deg

    # display_all_layouts(graph, best_sel)
    start_time = time.time()

    best_k, best_sel = obj.find_max_k(Use_external=True)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"⏱️ find_max_k 실행 시간: {elapsed:.3f}초")
    print("strong_clique_index: ", best_k)
    print("delta: ", obj.max_deg)
    display(graph, best_sel)