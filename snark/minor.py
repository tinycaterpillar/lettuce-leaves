import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195
from pysat.card import CardEnc
from collections import defaultdict
import tempfile
import subprocess

from utils import show_graph_with_node_colors, parse_kissat_output

class MinorChecker:
    def __init__(self, G: nx.Graph, H: nx.Graph, solver_path="./kissat", solver=Cadical195):
        self.G = G
        self.H = H
        self.pool = IDPool()
        self.solver = solver
        self.base_cnf = CNF()
        self._build_base_cnf()
        self.solver_path = solver_path

    def part(self, g, h): # partiton(u, h) := assign the vertex u ∈ G as a part h
        return self.pool.id(("part", g, h))
    
    def dist(self, h, v, t): # dist(s, v) in part h <= t where s is some starting point
        return self.pool.id(('dist', h, v, t))

    def aux(self, g1, h1, g2, h2):
        return self.pool.id(("aux", g1, h1, g2, h2))

    def _build_base_cnf(self):
        # 1. Partition: each g in G -> exactly one of H∪{DEL}
        parts = list(self.H.nodes()) + ["DEL"]
        for g in self.G.nodes():
            lits = [self.part(g, h) for h in parts]
            amo = CardEnc.equals(lits=lits, bound=1,
                                 encoding=1, top_id=self.pool.top)
            self.pool.top = amo.nv
            self.base_cnf.extend(amo.clauses)

        # 2. Surjectivity: each h in H must be used at least once
        for h in self.H.nodes():
            self.base_cnf.append([self.part(g, h) for g in self.G.nodes()])

        # 3. Adjacency preservation:
        for (h1, h2) in self.H.edges():
            witness_vars = []
            for (g1, g2) in self.G.edges():
                # Case 1: g1 ∈ branch(h1), g2 ∈ branch(h2)
                w1 = self.aux(g1, h1, g2, h2)
                witness_vars.append(w1)
                self.base_cnf.append([-w1, self.part(g1, h1)])
                self.base_cnf.append([-w1, self.part(g2, h2)])
                self.base_cnf.append([-self.part(g1, h1), -self.part(g2, h2), w1])
                
                # Case 2: g1 ∈ branch(h2), g2 ∈ branch(h1) (대칭성)
                w2 = self.aux(g1, h2, g2, h1)
                witness_vars.append(w2)
                self.base_cnf.append([-w2, self.part(g1, h2)])
                self.base_cnf.append([-w2, self.part(g2, h1)])
                self.base_cnf.append([-self.part(g1, h2), -self.part(g2, h1), w2])
            
            if witness_vars:
                self.base_cnf.append(witness_vars)

        # 4. branch set connectivity
        n = len(self.G.nodes())
        for h in self.H.nodes():
            gnodes = list(self.G.nodes())

            # (a) Exactly-one root: for each h pick exactly one g as start
            root_vars = [self.dist(h, g, 0) for g in gnodes]
            am1 = CardEnc.equals(lits=root_vars, bound=1,
                                 encoding=1, top_id=self.pool.top)
            self.pool.top = am1.nv
            self.base_cnf.extend(am1.clauses)

            # (b) dist(h,g,t) ⇒ part(g,h)
            for g in gnodes:
                for t in range(n):
                    self.base_cnf.append([-self.dist(h, g, t), self.part(g, h)])

            # (c) Monotonicity: dist(h,g,t) → dist(h,g,t+1)
            for g in gnodes:
                for t in range(n-1):
                    self.base_cnf.append([-self.dist(h, g, t), self.dist(h, g, t+1)])

            # (d) Propagation: if dist(h,g,t+1) then dist(h,g,t) or neighbor reachable
            for g in gnodes:
                for t in range(n-1):
                    clause = [-self.dist(h, g, t+1), self.dist(h, g, t)]
                    for u in self.G.neighbors(g):
                        clause.append(self.dist(h, u, t))
                    self.base_cnf.append(clause)

            # (e) Coverage: if g ∈ part(h) then must be reachable at step n-1
            for g in gnodes:
                self.base_cnf.append([-self.part(g, h), self.dist(h, g, n-1)])
    
    def is_minor(self, Use_external=False):
        if Use_external:
            return self._external_solver(self.base_cnf)

        with self.solver(bootstrap_with=self.base_cnf.clauses) as s:
            sat = s.solve()
            if not sat:
                return False, self.G
            model = set(s.get_model())

            for u in self.G.nodes():
                for h in list(self.H.nodes()) + ["DEL"]:
                    if self.part(u, h) in model:
                        self.G.nodes[u]["color"] = str(h)
                        break
            return True, self.G
    
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
                return False, self.G
            
            for u in self.G.nodes():
                for h in list(self.H.nodes()) + ["DEL"]:
                    if self.part(u, h) in model:
                        self.G.nodes[u]["color"] = str(h)
                        break
            return True, self.G


def contract(G: nx.Graph) -> nx.Graph:
    if not all("color" in G.nodes[n] for n in G.nodes()):
        raise ValueError("All nodes must have 'color' attribute.")

    G = G.copy()
    del_nodes = [n for n, data in G.nodes(data=True) if data["color"] == "DEL"]
    G.remove_nodes_from(del_nodes)

    partition = defaultdict(set)
    for n, data in G.nodes(data=True):
        partition[data["color"]].add(n)

    H = nx.quotient_graph(G, list(partition.values()), relabel=True)

    mapping = {frozenset(nodes): color for color, nodes in partition.items()}
    H = nx.relabel_nodes(H, mapping)

    return H

if __name__ == "__main__":
    G = nx.Graph()
    G.add_edges_from([(0,1), (1,2), (2,0)])        # left triangle
    G.add_edges_from([(1,3), (3,4), (4,5)])        # path to the right
    G.add_edges_from([(3,6), (6,4)])               # bottom triangle
    
    H = nx.Graph()
    H.add_edges_from([(0,1), (0,2), (0,3), (0,4)]) # cross shape

    checker = MinorChecker(G, H)
    sat, G = checker.is_minor()
    print("Is H a minor of G?", sat)
    if sat:
        show_graph_with_node_colors(G)