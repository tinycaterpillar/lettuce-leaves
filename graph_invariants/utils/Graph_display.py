from sage.all import *
import os
from glob import glob
import matplotlib.pyplot as plt
import datetime

def draw(G, H=None, name=None, folder=None):
    assert G.is_directed()

    fig, ax = plt.subplots(figsize=(8, 8))
    pos = G.layout("circular")

    P = Graphics()
    if H:
        highlight = Graph(H.edges(labels=False))  # simple graph
        P += highlight.plot(pos=pos,
                            edge_color=(1.0, 0.7, 0.4),
                            vertex_size=0,
                            edge_thickness=12)

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
    D = G.eulerian_orientation()
    draw(D)