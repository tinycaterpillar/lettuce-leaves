import os
import subprocess
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
import math

# Pastel highlighter-style palette
DEFAULT_PASTEL = [
    "#ffadad", "#ffd6a5", "#fdffb6", "#caffbf",
    "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff", "#fffffc"
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

def show_graph(
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

def make_cubic(n: int, k=3, t=3):  # k := degree, t := girth
    fname = f"{n}_{k}_{t}.asc"

    # If file already exists, do nothing
    if os.path.exists(fname):
        print(f"{fname} already exists. Doing nothing.")
        return fname

    # Otherwise run GenReg
    print(f"{fname} not found. Running GenReg...")
    subprocess.run(
        ["./GenReg.exe", str(n), str(k), str(t), "-a"],
        check=True
    )

    print(f"Saved output to {fname}")
    return fname


def parse_genreg_asc(path="./10_3_3.asc"):
    """Convert a GenReg .asc file into a list of NetworkX Graph objects"""
    graphs = []
    G = None

    # --- degree 추출 ---
    fname = os.path.basename(path)
    parts = os.path.splitext(fname)[0].split("_")
    degree = int(parts[1])

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Start of a new graph
            if line.startswith("Graph"):
                if G is not None:
                    graphs.append(G)
                G = nx.Graph()
                continue

            # Adjacency line: "1 : 2 3 4"
            m = re.match(r"(\d+)\s*:\s*(.*)", line)
            if m:
                u = int(m.group(1))
                neighbors = [int(x) for x in m.group(2).split()]
                if len(neighbors) == degree:
                    for v in neighbors:
                        if u < v:  # prevent duplicate edges
                            G.add_edge(u, v)
                continue

            # End of graph marker: "Ordnung: ..."
            if line.startswith("Ordnung:"):
                if G is not None:
                    graphs.append(G)
                    G = None

    # Add the last graph if not closed
    if G is not None:
        graphs.append(G)

    return graphs

def get_cubic(n, k=3, t=3):
    fname = make_cubic(n, k, t)
    graphs = parse_genreg_asc(fname)
    return graphs


if __name__ == "__main__":
    graphs = make_cubic(12)
    print(graphs[0])