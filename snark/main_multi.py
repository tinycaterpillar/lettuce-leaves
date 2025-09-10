from utils import get_cubic, show_graph_with_node_colors
from coloring import EdgeColoring
from minor import MinorChecker, contract
import networkx as nx
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def check_graph(args):
    """그래프 하나 검사"""
    ind, G, H = args
    sat, Gc = EdgeColoring(G).is_k_edge_colorable(Use_external=True)
    if not sat and len(list(nx.bridges(G))) == 0:
        sat_minor, Gc = MinorChecker(G, H).is_minor(Use_external=True)
        if not sat_minor:
            return ind, Gc  # counter example
    return None

if __name__ == "__main__":
    # graph_list = get_cubic(20, m=(i, j)) part i over j
    j = 10
    for i in range(4, j+1):
        graph_list = get_cubic(20, m=(i, j))
        H = nx.petersen_graph()

        results = []
        with ProcessPoolExecutor() as executor:
            tasks = [(ind, G, H) for ind, G in enumerate(graph_list)]
            for res in tqdm(executor.map(check_graph, tasks), total=len(tasks)):
                if res is not None:
                    ind, Gc = res
                    print("found counter example", ind)
                    results.append((ind, Gc))

        print("총 발견된 counter example 수:", len(results))
