import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import math

DEFAULT_PASTEL = [
    "#ffadad", "#ffd6a5", "#fdffb6", "#caffbf",
    "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff", "#fffffc"
]

def _compute_pos(
    G: nx.Graph,
    layout: str = "kk",
    seed: int = 42,
    scale: float = 1.0,
    spring_k: float | None = None,
):
    layout = layout.lower()
    n = max(len(G), 1)

    if layout in ("kk", "kamada_kawai", "kamada-kawai"):
        return nx.kamada_kawai_layout(G, weight=None, scale=scale)
    if layout in ("circular", "circle"):
        return nx.circular_layout(G, scale=scale)
    if layout in ("spectral",):
        return nx.spectral_layout(G, scale=scale)
    if layout in ("planar",):
        try:
            return nx.planar_layout(G, scale=scale)
        except nx.NetworkXException:
            return nx.kamada_kawai_layout(G, weight=None, scale=scale)

    if spring_k is None:
        spring_k = 1.2 / math.sqrt(n)
    return nx.spring_layout(G, seed=seed, k=spring_k, iterations=300, scale=scale)


def show_graph(
    G: nx.Graph,
    T_edges: list[tuple] | None = None,
    F_edges: list[tuple] | None = None,
    label_attr: str = "color",
    palette: list[str] = None,
    seed: int = 42,
    figsize=(6, 6),
    dpi: int = 120,
    edge_width: float = 10,
    layout: str = "kk",
    scale: float = 1.0,
    spring_k: float | None = None,
    T_style: dict = None,
    F_style: dict = None,
):
    if palette is None:
        palette = DEFAULT_PASTEL
    if T_style is None:
        T_style = dict(edge_color="black", style="dotted", width=edge_width*0.3, alpha=0.9)
    if F_style is None:
        F_style = dict(edge_color="red", style="dashdot", width=edge_width*0.4, alpha=0.9)

    pos = _compute_pos(G, layout=layout, seed=seed, scale=scale, spring_k=spring_k)

    # 1) 그룹핑 (라벨 속성별)
    groups = defaultdict(list)
    for u, v, d in G.edges(data=True):
        lbl = d.get(label_attr, "None")
        groups[str(lbl)].append((u, v))
    labels_sorted = sorted(groups.keys(), key=str)
    color_map = {lbl: palette[i % len(palette)] for i, lbl in enumerate(labels_sorted)}

    plt.figure(figsize=figsize, dpi=dpi)

    # 2) 일반 간선 (파스텔 실선)
    for lbl in labels_sorted:
        edge_list = groups[lbl]
        if edge_list:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=edge_list,
                edge_color=color_map[lbl],
                width=edge_width,
                alpha=0.9,
                style="solid",
            )

    # 3) F_edges 오버레이 (빨강 점선)
    if F_edges:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=F_edges,
            **F_style
        )

    # 4) T_edges 오버레이 (검정 점선)
    if T_edges:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=T_edges,
            **T_style
        )

    # 5) 노드와 라벨
    nx.draw_networkx_nodes(G, pos, node_color="#ffffff", edgecolors="#333333",
                           linewidths=1.2, node_size=520)
    nx.draw_networkx_labels(G, pos, font_size=11)

    # 6) 범례
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color=color_map[lbl], lw=edge_width, alpha=0.9)
               for lbl in labels_sorted]
    labels = labels_sorted[:]
    if T_edges:
        handles.append(Line2D([0], [0], color=T_style["edge_color"], lw=T_style["width"],
                              alpha=T_style["alpha"], linestyle=T_style["style"]))
        labels.append("T_edges")
    if F_edges:
        handles.append(Line2D([0], [0], color=F_style["edge_color"], lw=F_style["width"],
                              alpha=F_style["alpha"], linestyle=F_style["style"]))
        labels.append("F_edges")
    plt.legend(handles, labels, title=label_attr, loc="upper right",
               frameon=True, framealpha=0.9)

    plt.axis("off")
    plt.tight_layout()
    plt.show()


def edges_in_clique(vertices):
    """Given a list of vertex IDs, return all edges between them"""
    return [(vertices[i], vertices[j]) 
            for i in range(len(vertices)) 
            for j in range(i+1, len(vertices))]


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
