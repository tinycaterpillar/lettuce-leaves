from collections import defaultdict
from itertools import combinations
import networkx as nx
from util import show_graph


from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Glucose4  # 필요시 Kissat, CaDiCaL 등으로 교체 가능

# ----- 0) 예시 그래프 -----
k = 0
graph = nx.MultiGraph()
graph.add_edge(0, 1, color='red')
graph.add_edge(1, 2, color='red')
graph.add_edge(1, 3, color='red')
graph.add_edge(1, 3, color='red')   # 평행 간선
graph.add_edge(2, 3, color='blue')
graph.add_edge(3, 0, color='blue')

# show_graph(graph)

# ----- 1) 기본 수집 -----
V = list(graph.nodes())
assert V, "Graph is trivial."
missing = [(u, v, k) for u, v, k, d in graph.edges(keys=True, data=True) if ('color' not in d) or (d['color'] is None)]
assert not missing, f"Every edge must have a 'color' attribute. Missing: {missing}"
root = V[0]

# 색 목록
colors = sorted({d.get('color') for _, _, d in graph.edges(data=True)})

# 간선 목록(고유 식별: (u,v,key))
E = list(graph.edges(keys=True))  # [(u,v,key), ...]

# 색별 '실제' 간선 쌍(무향)을 수집: (min(u,v), max(u,v))
pairs_by_color = {c: set() for c in colors}
for u, v, data in graph.edges(data=True):
    c = data.get('color')
    a, b = (u, v) if u <= v else (v, u)
    pairs_by_color[c].add((a, b))

# ----- 2) 변수 생성 (IDPool) -----
pool = IDPool()

def wid(e):  # wild 변수
    u, v, k = e
    a, b = (u, v) if u <= v else (v, u)
    return pool.id(('wild', a, b, k))

def rid(c, u, v):  # reach(c,u,v)
    return pool.id(('reach', c, u, v))

# 미리 한 번 생성(선택 사항이지만 가독성 위해)
for e in E:
    _ = wid(e)
for c in colors:
    for u in V:
        for v in V:
            if u != v:
                _ = rid(c, u, v)

# ----- 3) 절 생성 -----
cnf = CNF()

# 그래프에서 wild가 될 수 없는 edge들은 미리 걸러내기

# 3a) at-most-k (카디널리티 인코딩)
wild_lits = [wid(e) for e in E]
if k < len(wild_lits):
    amk = CardEnc.atmost(lits=wild_lits, bound=k, top_id=pool.top)
    cnf.extend(amk.clauses)
    # CardEnc가 새 보조변수를 쓰므로 pool.top은 이후 새로 쓰지 않는 게 안전

# 3b) 색별: 직접 도달성(실제 간선), wild 간선, 전이성, 연결성
for c in colors:
    # (i) 실제 c-간선: u<->v 즉시 도달 (단위절)
    for (a, b) in pairs_by_color[c]:
        cnf.append([rid(c, a, b)])
        cnf.append([rid(c, b, a)])

    # (ii) wild 간선도 모든 색에서 즉시 도달
    for (u, v, k_) in E:
        cnf.append([-wid((u, v, k_)), rid(c, u, v)])
        cnf.append([-wid((u, v, k_)), rid(c, v, u)])

    # (iii) 전이성: (u→v ∧ v→w) ⇒ u→w
    for u in V:
        for v in V:
            if u == v: continue
            for w in V:
                if w == u or w == v: continue
                cnf.append([-rid(c, u, v), -rid(c, v, w), rid(c, u, w)])

    # (iv) 연결성: root에서 모든 정점으로 도달
    for v in V:
        if v != root:
            cnf.append([rid(c, root, v)])

# ----- 4) 풀기 -----
with Glucose4(bootstrap_with=cnf.clauses) as solver:
    sat = solver.solve()
    if not sat:
        print("UNSAT (주어진 k로는 불가능)")
    else:
        model = set(solver.get_model())  # 양수 literal 집합
        wild_edges = [e for e in E if wid(e) in model]
        print("SAT")
        print("wild edges:", wild_edges)
