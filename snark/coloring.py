import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195

from utils import show_graph

class EdgeColoring:
    def __init__(self, graph: nx.Graph, k=3, solver=Cadical195):
        if graph.is_multigraph():
            raise ValueError("This checker supports only simple graphs (no multi-edges).")
        self.G = graph
        self.k = k
        self.pool = IDPool()
        self.solver = solver
        self.base_cnf = CNF()
        self._build_cnf()

    def color(self, edge, color): # color(e, 1) := color e as 1
        u, v = sorted(edge)
        return self.pool.id(("edge", (u, v), color))

    def _build_cnf(self):
        # Each edge gets exactly one color
        for e in self.G.edges():
            lits = [self.color(e, c) for c in range(self.k)]
            amo = CardEnc.equals(lits=lits, bound=1, encoding=1, top_id=self.pool.top)
            self.pool.top = amo.nv
            self.base_cnf.extend(amo.clauses)

        # Adjacent edges must not share the same color
        for v in self.G.nodes():
            incident_edges = list(self.G.edges(v))
            for i in range(len(incident_edges)):
                for j in range(i+1, len(incident_edges)):
                    e1, e2 = incident_edges[i], incident_edges[j]
                    for c in range(self.k):
                        self.base_cnf.append([-self.color(e1, c), -self.color(e2, c)])

    def is_k_edge_colorable(self):
        with self.solver(bootstrap_with=self.base_cnf.clauses) as s:
            sat = s.solve()
            if not sat:
                return False, self.G
            model = set(s.get_model())
            for e in self.G.edges():
                for c in range(self.k):
                    if self.color(e, c) in model:
                        self.G[e[0]][e[1]]["color"] = str(c)
            return True, self.G


if __name__ == "__main__":
    G = nx.cubical_graph()
    checker = EdgeColoring(G)
    sat, coloring = checker.is_k_edge_colorable()
    show_graph(G)