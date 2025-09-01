import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import math
import random

# Pastel highlighter-style palette
DEFAULT_PASTEL = [
    "#ffadad", "#ffd6a5", "#fdffb6", "#caffbf",
    "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff", "#fffffc"
]

def _compute_pos(
    G: nx.Graph,
    layout: str = "kk",      # "kk" | "circular" | "spring" | "spectral" | "planar"
    seed: int = 42,
    scale: float = 1.0,
    spring_k: float | None = None,
):
    """Return node positions according to the chosen layout."""
    layout = layout.lower()
    n = max(len(G), 1)

    if layout in ("kk", "kamada_kawai", "kamada-kawai"):
        # Good uniform-looking layout (treat all edges equally)
        return nx.kamada_kawai_layout(G, weight=None, scale=scale)

    if layout in ("circular", "circle"):
        # Perfectly uniform angles on a circle
        return nx.circular_layout(G, scale=scale)

    if layout in ("spectral",):
        # Eigenvector-based layout; often spreads nodes fairly evenly
        return nx.spectral_layout(G, scale=scale)

    if layout in ("planar",):
        # Works only for planar graphs; fallback to KK if not planar
        try:
            return nx.planar_layout(G, scale=scale)
        except nx.NetworkXException:
            return nx.kamada_kawai_layout(G, weight=None, scale=scale)

    # Default: Fruchterman–Reingold (spring)
    # Choose k ~ c / sqrt(n) for decent spreading if not given
    if spring_k is None:
        spring_k = 1.2 / math.sqrt(n)
    return nx.spring_layout(G, seed=seed, k=spring_k, iterations=300, scale=scale)

def show_graph(
    G: nx.MultiGraph,
    wild_edges: list[tuple] | None = None,   # 첫 번째 매개변수로 이동
    label_attr: str = "color",
    palette: list[str] = None,
    seed: int = 42,
    figsize=(6, 6),
    dpi: int = 120,
    edge_width: float = 10,      # 색 실선 두께
    layout: str = "kk",
    scale: float = 1.0,
    spring_k: float | None = None,
    # --- wild overlay options ---
    wild_width: float | None = None,         # 점선 두께 (None이면 edge_width*0.2)
    wild_alpha: float = 0.95,
    wild_dash: str = "dotted",                   # 점선 스타일
    wild_color: str = "#222222",             # 검은 점선
):
    """Draw MultiGraph with pastel colored edges and black dotted overlay for wild edges."""
    if palette is None:
        palette = DEFAULT_PASTEL

    # 1) 위치
    pos = _compute_pos(G, layout=layout, seed=seed, scale=scale, spring_k=spring_k)

    # 2) 병렬 엣지 곡률
    base = 0.18
    rad_map = {}
    seen_pairs = set()
    for u, v in G.edges():
        a, b = (u, v) if u <= v else (v, u)
        if (a, b) in seen_pairs:
            continue
        seen_pairs.add((a, b))
        keys = list(G[a][b].keys()) if b in G[a] else []  # 버그 수정: KeyError 방지
        m = len(keys)
        rads = [0.0] if m == 1 else [(i - (m - 1) / 2) * (base * 1.2) for i in range(m)]
        for k, rad in zip(keys, rads):
            rad_map[(a, b, k)] = rad

    # 3) 라벨별 그룹
    groups = defaultdict(list)
    for u, v, k, d in G.edges(keys=True, data=True):
        lbl = d.get(label_attr, "None")  # 버그 수정: None 대신 문자열 "None" 사용
        groups[str(lbl)].append((u, v, k))
    labels_sorted = sorted(groups.keys(), key=str)

    # 4) 색 맵
    color_map = {lbl: palette[i % len(palette)] for i, lbl in enumerate(labels_sorted)}

    # 5) wild set 정규화
    wild_set = set()
    if wild_edges:
        for item in wild_edges:
            if len(item) < 3:
                continue
            u, v, k = item[:3]
            a, b = (u, v) if u <= v else (v, u)
            if a in G and b in G[a] and k in G[a][b]:
                wild_set.add((a, b, k))

    plt.figure(figsize=figsize, dpi=dpi)

    # 6) 일반 엣지: 파스텔 "굵은 실선"
    for lbl in labels_sorted:
        edge_list = []
        for (u, v, k) in groups[lbl]:
            a, b = (u, v) if u <= v else (v, u)
            edge_list.append((a, b, k))
        
        if edge_list:  # 버그 수정: 빈 리스트 체크
            for (a, b, k) in edge_list:
                try:
                    lc = nx.draw_networkx_edges(
                        G, pos,
                        edgelist=[(a, b, k)],
                        edge_color=color_map[lbl],
                        width=edge_width,
                        alpha=0.92,
                        connectionstyle=f"arc3,rad={rad_map.get((a, b, k), 0.0)}",
                        style="solid",
                    )
                    # 둥근 끝(점선과 어울리게) - lc가 리스트인 경우 처리
                    if lc is not None:
                        if isinstance(lc, list):
                            for line in lc:
                                if hasattr(line, 'set_capstyle'):
                                    line.set_capstyle("round")
                        else:
                            if hasattr(lc, 'set_capstyle'):
                                lc.set_capstyle("round")
                except Exception as e:
                    print(f"Warning: Could not draw edge ({a}, {b}, {k}): {e}")

    # 7) wild 엣지: 같은 경로에 "검은 점선 오버레이"
    if wild_set:
        wwidth = (edge_width * 0.2) if wild_width is None else wild_width
        for (a, b, k) in wild_set:
            try:
                lc2 = nx.draw_networkx_edges(
                    G, pos,
                    edgelist=[(a, b, k)],
                    edge_color=wild_color,
                    width=wwidth,
                    alpha=wild_alpha,
                    connectionstyle=f"arc3,rad={rad_map.get((a, b, k), 0.0)}",
                    style=wild_dash,  # dotted
                )
                if lc2 is not None:
                    if isinstance(lc2, list):
                        for line in lc2:
                            if hasattr(line, 'set_capstyle'):
                                line.set_capstyle("round")
                    else:
                        if hasattr(lc2, 'set_capstyle'):
                            lc2.set_capstyle("round")
            except Exception as e:
                print(f"Warning: Could not draw wild edge ({a}, {b}, {k}): {e}")

    # 8) 노드/라벨
    try:
        nx.draw_networkx_nodes(G, pos, node_color="#ffffff", edgecolors="#333333", linewidths=1.2, node_size=520)
        nx.draw_networkx_labels(G, pos, font_size=11)
    except Exception as e:
        print(f"Warning: Could not draw nodes or labels: {e}")

    # 9) 범례 (라벨 + wild 표시)
    try:
        from matplotlib.lines import Line2D
        handles = [Line2D([0], [0], color=color_map[lbl], lw=edge_width, alpha=0.92)
                   for lbl in labels_sorted]
        labels = labels_sorted[:]
        if wild_set:
            handles.append(Line2D([0], [0], color=wild_color, lw=wwidth, alpha=wild_alpha,
                                  linestyle="dotted"))
            labels.append("wild")
        plt.legend(handles, labels, title=label_attr, loc="upper right", frameon=True, framealpha=0.9)
    except Exception as e:
        print(f"Warning: Could not create legend: {e}")

    plt.axis("off")
    plt.tight_layout()
    plt.show()


def parse_kissat_output(output: str):
    is_sat = None
    model = set()

    for line in output.splitlines():
        if line.startswith("s "):
            if "UNSAT" in line:
                is_sat = False
            elif "SAT" in line:
                is_sat = True
        elif line.startswith("v "):
            lits = map(int, line.split()[1:])
            for lit in lits:
                if lit == 0:
                    break
                if lit > 0:
                    model.add(lit)

    return is_sat, model


class Dsu:
    def __init__(self, n):
        # If p[u] < 0: u is a root, and |p[u]| = size of the tree
        # If p[u] >= 0: p[u] is the parent of u
        self.p = [-1] * (n+1)
        self.c = n # number of components

    def find(self, u):
        if self.p[u] < 0: return u

        self.p[u] = self.find(self.p[u])
        return self.p[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)
        if root_u == root_v: return False

        if self.p[root_u] > self.p[root_v]:  # root_v has larger tree
            self.p[root_v] += self.p[root_u]
            self.p[root_u] = root_v
        else:
            self.p[root_u] += self.p[root_v]
            self.p[root_v] = root_u
        self.c -= 1
        return True


def random_partition(S, P):
    assert len(S) >= sum(P)
    items = list(S)
    random.shuffle(items)

    partitions = []
    for p in P:
        part = [items.pop() for _ in range(p)]  # 뒤에서 p개 pop
        partitions.append(part)

    return partitions

def partitions_fixed_length(n, l, max_val=None):
    if max_val is None:
        max_val = n

    # 종료 조건
    if l == 1:
        if 1 <= n <= max_val:
            yield [n]
        return

    # i는 현재 항, 다음 항들은 i 이하
    for i in range(1, min(max_val, n - l + 1) + 1):
        for rest in partitions_fixed_length(n - i, l - 1, i):
            yield [i] + rest
