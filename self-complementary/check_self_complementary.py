import networkx as nx
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import random

# --------- 설정 ---------
max_trials = 1000
num_workers = 8
data_path = "data/seq.txt"

# True - display self-complmentary graph
# False - display none self-complmentary graph
flag = False
seed = random.randint(0, 10**6)
# -------------------------

def is_self_complementary_once(degree_sequence):
    G = nx.havel_hakimi_graph(degree_sequence)
    try:
        G = nx.double_edge_swap(G.copy(), nswap=100, max_tries=1000)
    except nx.NetworkXAlgorithmError:
        pass

    Gc = nx.complement(G)
    return nx.is_isomorphic(G, Gc), G, Gc

def test_one_sequence(seq_info):
    index, degree_sequence = seq_info
    for trial in range(max_trials):
        ans, G, Gc = is_self_complementary_once(degree_sequence)
        if flag == ans:
            return  {
                'index': index,
                'sequence': degree_sequence,
                'trial': trial,
                'graph': G,
                'complement': Gc,
                'radius': nx.radius(G),
                'diameter' : nx.diameter(G),
                'λ': nx.edge_connectivity(G),
                'δ': min(dict(G.degree()).values())
            }
    return None

def visualize(result):
    G = result['graph']
    Gc = result['complement']
    
    # 동일한 노드 위치를 양쪽 그래프에 사용
    # pos = nx.spring_layout(G, seed=42) # use this if kamada_kawai_layout is too slow
    G_pos = nx.kamada_kawai_layout(G)
    Gc_pos = nx.kamada_kawai_layout(Gc)

    plt.figure(figsize=(14, 6))

    # 원래 그래프
    plt.subplot(1, 2, 1)
    nx.draw_networkx_nodes(G, G_pos, node_color='skyblue', node_size=800)
    nx.draw_networkx_edges(G, G_pos, edge_color='gray', width=1.5)
    nx.draw_networkx_labels(G, G_pos, font_size=10)
    plt.title(f"G (Trial {result['trial'] + 1})")
    plt.axis('off')

    # 컴플리먼트 그래프
    plt.subplot(1, 2, 2)
    nx.draw_networkx_nodes(Gc, Gc_pos, node_color='salmon', node_size=800)
    nx.draw_networkx_edges(Gc, Gc_pos, edge_color='gray', width=1.5)
    nx.draw_networkx_labels(Gc, Gc_pos, font_size=10)
    plt.title("Complement of G")
    plt.axis('off')

    plt.suptitle(f"{'' if flag else 'not '}self-complementarity!", fontsize=14)
    info_text = (
        f"seed -> {seed}\n"
        f"rad(G) = {result['radius']}∈{{2}}   diam(G) = {result['diameter']}∈{{2, 3}}\n"
        f"λ(G) = {result['λ']}   δ(G) = {result['δ']}\n"
        f"Degree sequence: {' '.join(map(str, result['sequence']))}\n"
    )
    plt.figtext(0.5, 0.02, info_text, ha='center', fontsize=10)
    plt.show()

    
def load_sequences(path, seed=None):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    sequences = []
    for line in lines:
        tokens = line.strip().split()
        if not tokens or len(tokens) == 1:
            continue
        sequences.append(list(map(int, tokens)))
    
    if seed: 
        random.seed(seed)
        random.shuffle(sequences)
    return sequences

def main():
    sequences = load_sequences(data_path, seed=seed)
    print(f"Loaded {len(sequences)} sequences.")

    indexed_seqs = list(enumerate(sequences, start=1))

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(test_one_sequence, seq_info) for seq_info in indexed_seqs]
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"{'' if flag else 'not '}self-complementarity!")
                print(f"→ Degree sequence: {result['sequence']}")
                visualize(result)
                return

    print("\nAll sequences passed. All generated graphs were self-complementary.")

if __name__ == "__main__":
    main()
