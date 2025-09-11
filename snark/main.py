from utils import get_cubic
from coloring import EdgeColoring
import networkx as nx
from tqdm import tqdm

from minor import MinorChecker, contract
from utils import show_graph_with_node_colors, parse_genreg_asc

with open("snarks_50.04.oddness4.cyc4.some.g6", "rb") as f:
    graph_list = nx.read_graph6(f)

if isinstance(graph_list, nx.Graph):
    graph_list = [graph_list]

print(f"불러온 그래프 개수: {len(graph_list)}")

H = nx.petersen_graph()

for ind, G in enumerate(tqdm(graph_list, desc="Checking graphs")):
    sat, G = EdgeColoring(G).is_k_edge_colorable(Use_external=True)
    if not sat and len(list(nx.bridges(G))) == 0:
        print(f"checking graph {ind}", G, sep=', ')
        sat, G = MinorChecker(G, H).is_minor(Use_external=True)
        if not sat:
            print("found counter example", ind)