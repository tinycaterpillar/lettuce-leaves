import networkx as nx
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed

max_trials = 10000
num_2 = 4           # 2의 개수 고정
num_threads = 8     # 병렬 처리할 쓰레드 수

def generate_and_check(index, degree_sequence):
    G = nx.havel_hakimi_graph(degree_sequence)
    try:
        G_swapped = nx.double_edge_swap(G.copy(), nswap=100, max_tries=1000)
    except nx.NetworkXAlgorithmError:
        G_swapped = G

    if list(nx.bridges(G_swapped)):
        return None

    if not nx.is_connected(G_swapped):
        return None

    matching = nx.algorithms.matching.max_weight_matching(G_swapped, maxcardinality=True)
    if len(matching) * 2 != G_swapped.number_of_nodes():
        return {
            'index': index,
            'graph': G_swapped,
            'matching': list(matching)
        }
    return None

def run_experiment(degree_sequence):
    print(f"Running experiment for degree_sequence: {degree_sequence}")
    if not nx.is_graphical(degree_sequence):
        print("Error: Invalid degree sequence!")
        return

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(generate_and_check, i, degree_sequence) for i in range(max_trials)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                G_result = result['graph']
                matching_edges = result['matching']
                pos = nx.spring_layout(G_result, seed=42)
                node_colors = ['skyblue' if G_result.degree(n) == 3 else 'lightgreen' for n in G_result.nodes()]

                plt.figure(figsize=(6, 6))
                nx.draw(G_result, pos, node_color=node_colors, node_size=500, with_labels=True)
                nx.draw_networkx_edges(G_result, pos, edgelist=matching_edges, edge_color='red', width=2)
                plt.title(f"Perfect Matching NOT Found (Trial {result['index'] + 1})\nDegree sequence: {degree_sequence}")
                plt.axis('off')
                plt.show()
                return  # 조기 종료
    print("All Clear: Perfect matching found in all graphs.\n")

for num_3 in range(2, 21, 2):
    degree_sequence = [3] * num_3 + [2] * num_2
    degree_sequence.sort(reverse=True)
    run_experiment(degree_sequence)