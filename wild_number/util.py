import networkx as nx
import matplotlib.pyplot as plt

def show_graph(G_nx: nx.MultiGraph, seed=42, figsize=(6, 6), dpi=120):
    pos = nx.spring_layout(G_nx, seed=seed)
    plt.figure(figsize=figsize, dpi=dpi)

    base = 0.18  # 평행 간선 곡률 간격
    for u, v in G_nx.edges():
        key_dict = G_nx[u][v]
        keys = list(key_dict.keys())
        m = len(keys)
        rads = [0.0] if m == 1 else [(i - (m - 1) / 2) * (base * 1.2) for i in range(m)]

        # 각 간선 그리기
        for k, rad in zip(keys, rads):
            nx.draw_networkx_edges(
                G_nx, pos,
                edgelist=[(u, v, k)],
                edge_color=key_dict[k].get("color"),
                width=2.0,
                alpha=0.95,
                connectionstyle=f"arc3,rad={rad}",
            )

    # 노드/라벨
    nx.draw_networkx_nodes(G_nx, pos, node_color="#f2f2f2", edgecolors="#333", node_size=520)
    nx.draw_networkx_labels(G_nx, pos, font_size=10)

    plt.axis("off")
    plt.tight_layout()
    plt.show()
