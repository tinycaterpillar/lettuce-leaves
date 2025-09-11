import os
import subprocess
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
import math

DEFAULT_PASTEL = [
    "#ffadad",  # pastel red
    "#ffd6a5",  # pastel orange
    "#fdffb6",  # pastel yellow
    "#caffbf",  # pastel green
    "#9bf6ff",  # pastel cyan
    "#a0c4ff",  # pastel blue
    "#bdb2ff",  # pastel purple
    "#ffc6ff",  # pastel pink
    "#fffffc",  # off-white
    "#d0f4de",  # pastel mint
    "#f1c0e8",  # pastel lavender-pink
]

def _compute_pos(G, layout="kk", seed=42, scale=1.0, spring_k=None):
    """Return node positions according to the chosen layout."""
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

def show_graph_with_edge_colors(
    G: nx.Graph,
    label_attr: str = "color",
    palette: list[str] = None,
    seed: int = 42,
    figsize=(6, 6),
    dpi: int = 120,
    edge_width: float = 10,
    layout: str = "kk",
    scale: float = 1.0,
    spring_k: float | None = None,
):
    """Draw Graph with pastel colored edges based on edge attribute."""
    if palette is None:
        palette = DEFAULT_PASTEL

    pos = _compute_pos(G, layout=layout, seed=seed, scale=scale, spring_k=spring_k)

    # 라벨별 그룹핑
    groups = defaultdict(list)
    for u, v, d in G.edges(data=True):
        lbl = d.get(label_attr, "None")
        groups[str(lbl)].append((u, v))
    labels_sorted = sorted(groups.keys(), key=str)

    # 색상 매핑
    color_map = {lbl: palette[i % len(palette)] for i, lbl in enumerate(labels_sorted)}

    plt.figure(figsize=figsize, dpi=dpi)

    # 엣지 그리기
    for lbl in labels_sorted:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=groups[lbl],
            edge_color=color_map[lbl],
            width=edge_width,
            alpha=0.92,
        )

    # 노드 & 라벨
    nx.draw_networkx_nodes(G, pos, node_color="#ffffff", edgecolors="#333333",
                           linewidths=1.2, node_size=520)
    nx.draw_networkx_labels(G, pos, font_size=11)

    # 범례
    handles = [Line2D([0], [0], color=color_map[lbl], lw=edge_width, alpha=0.92)
               for lbl in labels_sorted]
    plt.legend(handles, labels_sorted, title=label_attr, loc="upper right",
               frameon=True, framealpha=0.9)

    plt.axis("off")
    plt.tight_layout()
    plt.show()

def show_graph_with_node_colors(
    G: nx.Graph,
    color_attr: str = "color",
    palette: list[str] = None,
    seed: int = 42,
    figsize=(6, 6),
    dpi: int = 120,
    edge_width: float = 1.8,
    layout: str = "kk",
    scale: float = 1.0,
    spring_k: float | None = None,
):
    """노드 color_attr 값이 있으면 해당 색으로 노드 색칠."""
    if palette is None:
        palette = DEFAULT_PASTEL

    pos = _compute_pos(G, layout=layout, seed=seed, scale=scale, spring_k=spring_k)

    # 노드 라벨 수집
    labels = [str(G.nodes[n].get(color_attr, "None")) for n in G.nodes()]

    # 유니크 라벨 → 색상 매핑 (겹치지 않음)
    uniq_labels = list(dict.fromkeys(labels))
    color_map = {lbl: palette[i] for i, lbl in enumerate(uniq_labels)}

    # 각 노드 색상
    colors = [color_map[lbl] for lbl in labels]

    # 그래프 그리기
    plt.figure(figsize=figsize, dpi=dpi)
    nx.draw_networkx_edges(G, pos, width=edge_width, edge_color="#333333", alpha=0.4)
    nx.draw_networkx_nodes(
        G, pos,
        node_color=colors,
        edgecolors="#333333",
        linewidths=1.2,
        node_size=520,
    )
    nx.draw_networkx_labels(G, pos, font_size=11)

    # 범례
    handles = [
        Line2D([0], [0], marker="o", markersize=10,
               markerfacecolor=color_map[lbl], markeredgecolor="#333333", lw=0)
        for lbl in uniq_labels
    ]

    plt.legend(
        handles, uniq_labels,
        title=color_attr,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True, framealpha=0.9
    )

    plt.axis("off")
    plt.tight_layout()
    plt.show()


    fname = make_cubic(n, k, t, m=m)
    graphs = parse_genreg_asc(fname)
    return graphs

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


if __name__ == "__main__":
    pass