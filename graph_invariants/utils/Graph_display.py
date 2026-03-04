from sage.all import *
import os
from glob import glob
import matplotlib.pyplot as plt
import datetime

pastels = [
    (0.95, 0.78, 0.55),  # pastel orange
    (0.75, 0.85, 0.95),  # pastel blue
]

def draw(G, H=None, name=None, folder=None, layout="circular"):
    """A layout algorithm – one of : “acyclic”, “circular” (plots the graph with vertices evenly distributed on a circle), “ranked”, “graphviz”, “planar”, “spring” (traditional spring layout, using the graph’s current positions as initial positions), or “tree” (the tree will be plotted in levels, depending on minimum distance for the root)."""

    assert G.is_directed()

    fig, ax = plt.subplots(figsize=(8, 8))
    pos = G.layout(layout)

    P = Graphics()
    if H:
        if not isinstance(H, (list, tuple)): H = [H]

        for i, Hi in enumerate(H):
            highlight = Graph(Hi.edges(labels=False))  # simple graph
            P += highlight.plot(pos=pos,
                                edge_color=pastels[i % len(pastels)],
                                vertex_size=0,
                                edge_thickness=14 - 7*(i % len(pastels)))

    P += G.plot(pos=pos, edge_color="black")

    if name: plt.title(name, fontsize=20)

    P.matplotlib(figure=fig)

    ax.set_frame_on(False)
    ax.set_xticks([]); ax.set_yticks([])
    plt.axis("off")

    if folder:
        assert name, "Name must be provided when saving the figure."
        os.makedirs(folder, exist_ok=True)
        filename = f"{folder}/{name}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    else: plt.show(block=True)

if __name__ == "__main__":
    G = graphs.CycleGraph(6)
    # D = G.eulerian_orientation()
    # draw(D)