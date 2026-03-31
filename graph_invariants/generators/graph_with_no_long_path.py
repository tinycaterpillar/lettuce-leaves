from sage.all import *

import sys, os
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Cadical195
import tempfile
import subprocess
from sortedcontainers import SortedSet
from collections import deque

from utils import draw, encode
# from utils import parse_kissat_output

class GraphSATBuilder:
    """
    Input: size of exits and minimum degree
    Output: A simple graph without δ-path
    """
    def __init__(self, number_of_exits, min_degree, solver=Cadical195):
        self.number_of_exits = number_of_exits
        self.min_degree = min_degree
        self.pool = IDPool()
        self.solver = solver
        self.solver_path = "./external_program/kissat"
        self.V = None

    def edge(self, e):
        return self.pool.id(("chosen", e))

    def reachable(self, rm, v, t):
        return self.pool.id(("reachable", rm, v, t))
    
    def canon_edge(self, e):
        u, v = e
        return (u, v) if u <= v else (v, u)

    def aux(self, a, b):
        return self.pool.id(("aux_and", a, b))

    def build_cnf(self, number_of_non_exits) -> CNF:
        self.pool = IDPool()
        cnf = CNF()

        exits = list(range(self.number_of_exits))
        non_exits = list(range(self.number_of_exits, self.number_of_exits+number_of_non_exits))
        self.V = exits+non_exits

        for u in self.V:
            for v in self.V:
                if u == v: continue
                self.edge(self.canon_edge((u, v)))

        # (1) degree_condition
        # d(exit) >= 2 and d(non_exit) >= min_degree
        for v in self.V:
            inc_v = [self.edge(self.canon_edge((u, v))) for u in self.V if u != v]
            lb = 2 if v < self.number_of_exits else self.min_degree
            enc = CardEnc.atleast(lits=inc_v, bound=lb, encoding=1, top_id=self.pool.top)
            self.pool.top = enc.nv
            cnf.extend(enc.clauses)

        # (2) 2-vertex-connectivity
        for rm in self.V:
            W = [v for v in self.V if v != rm]
            root = W[0]

            cnf.append([self.reachable(rm, root, 0)])   # root is reachable from itself
            for v in W:
                if v == root: continue
                cnf.append([-self.reachable(rm, v, 0)])    # others are not reachable at step 0

            # monotonicity: reachable(rm, v, t) -> reachable(rm, v, t+1)
            for v in W:
                for t in range(len(W)-1):
                    cnf.append([-self.reachable(rm, v, t), self.reachable(rm, v, t + 1)])


            # propagation:
            # reachable(rm, v, t+1) -> reachable(rm, v, t) or exists neighbor u with reachable(rm, u, t) and edge(u, v)
            for v in W:
                for t in range(len(W)-1):
                    clause = [-self.reachable(rm, v, t + 1), self.reachable(rm, v, t)]
                    
                    for u in W:
                        e = self.canon_edge((u, v))
                        x = self.edge(e)

                        # y <-> (reachable(rm, u, t) and x)
                        y = self.aux(self.reachable(rm, u, t), x)

                        cnf.append([-y, self.reachable(rm, u, t)])
                        cnf.append([-y, x])
                        cnf.append([y, -self.reachable(rm, u, t), -x])

                        clause.append(y)

                    cnf.append(clause)

            # every vertex must be reachable within n-1 steps
            for v in W:
                cnf.append([self.reachable(rm, v, len(W) - 1)])

        return cnf
    
    def find_bad_path(self, start, adj):
        n = len(adj)
        visited = [False] * n
        parent = [-1] * n

        def dfs(cur, prev, dep):
            visited[cur] = True
            parent[cur] = prev

            if dep >= self.min_degree: return cur

            for nxt in adj[cur]:
                if visited[nxt]: continue
                tmp = dfs(nxt, cur, dep+1)
                if tmp >= 0: return tmp

            visited[cur] = False
            return -1
    
        tmp = dfs(start, -1, 0)
        
        ret = []
        if tmp >= 0:
            while parent[tmp] != -1:
                ret.append((tmp, parent[tmp]))
                tmp = parent[tmp]

        return ret

    def external_solver(self, cnf):
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
            
            E = [
                (u, v)
                for u in self.V
                for v in self.V
                if u < v and self.edge(self.canon_edge((u, v))) in model
            ]
            G = Graph()
            G.add_vertices(self.V)
            G.add_edges(E)
            return True, G

    def solve(self, number_of_non_exits, external=True):
        cnf = self.build_cnf(number_of_non_exits)

        if external: return self.external_solver(cnf)
        
        iter = 1
        with self.solver(bootstrap_with=cnf.clauses) as s:
            while True:
                print(f"{iter} trial")
                iter += 1
    
                sat = s.solve()
                if not sat:
                    return False, None

                model = SortedSet(s.get_model())
                Edges = [[] for _ in range(len(self.V))]
                for u in range(len(self.V)):
                    for v in range(u+1, len(self.V)):
                        if self.edge(self.canon_edge((u, v))) not in model: continue
                        Edges[u].append(v)
                        Edges[v].append(u)

                flag = True
                for exit in range(self.number_of_exits):
                    path = self.find_bad_path(exit, Edges)
                    if path:
                        flag = False
                        s.add_clause([-self.edge(self.canon_edge((u, v))) for (u, v) in path])
                        break

                if flag:
                    G = Graph()
                    G.add_vertices(self.V)
                    for u in range(len(self.V)):
                        for v in Edges[u]:
                            if u < v:
                                G.add_edge(u, v)
                    return True, G


if __name__ == "__main__":
    min_degree = 25
    number_of_non_exits = 12
    number_of_exits = 14
    builder = GraphSATBuilder(number_of_exits=number_of_exits, min_degree=min_degree)
    sat, G = builder.solve(number_of_non_exits=number_of_non_exits, external=False)

    print("SAT:", sat)
    if sat:
        draw(G, V=list(range(number_of_exits)), name=encode(G), folder="pictures")