from sage.all import *
import matplotlib.pyplot as plt

def draw(G):
    fig, ax = plt.subplots(figsize=(8, 8))
    G.plot(layout="circular").matplotlib(figure=fig)
    ax.set_axis_off()
    plt.show(block=True)

if __name__ == "__main__":
    G = graphs.CycleGraph(6)
    D = G.eulerian_orientation()
    draw(D)