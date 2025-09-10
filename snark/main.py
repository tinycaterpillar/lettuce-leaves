from utils import get_cubic
from coloring import EdgeColoring
import networkx as nx

from minor import MinorChecker, contract
from utils import show_graph_with_node_colors

graph_list = get_cubic(18)
H = nx.petersen_graph()

for ind, G in enumerate(graph_list):
    sat, G = EdgeColoring(G).is_k_edge_colorable(Use_external=True)
    if not sat and len(list(nx.bridges(G))) == 0:
        print(f"checking graph {ind}", G, sep=', ')
        sat, G = MinorChecker(G, H).is_minor(Use_external=True)
        if not sat:
            print("found counter example", ind)