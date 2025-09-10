from utils import get_cubic, show_graph
from coloring import EdgeColoring
import networkx as nx

graphs = get_cubic(16)
for ind, G in enumerate(graphs):
    sat, G = EdgeColoring(G).is_k_edge_colorable()
    if not sat and len(list(nx.bridges(G))) == 0:
        print(ind)
        show_graph(G)