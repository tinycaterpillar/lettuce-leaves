import networkx as nx
from networkx.algorithms.coloring import greedy_color
from minor import MinorChecker
from utils import show_graph_with_node_colors

n = 9
G = nx.mycielski_graph(n)
H = nx.complete_graph(n)
sat, G = MinorChecker(G, H).is_minor()
print(sat)