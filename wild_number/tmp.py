import networkx as nx
from itertools import combinations
from tqdm import tqdm
from math import comb as nCr
from concurrent.futures import ProcessPoolExecutor

from utils import show_graph
from solver import KWildSAT 

n = 10
k = 4

# 그래프와 엣지 초기화
G = nx.complete_graph(n, create_using=nx.MultiGraph)
edges = list(G.edges())

def worker(comb):
    # 프로세스마다 그래프 복사 (안전하게)
    G_local = nx.complete_graph(n, create_using=nx.MultiGraph)
    nx.set_edge_attributes(G_local, {e: "A" for e in G_local.edges(keys=True)}, name="color")

    # 선택된 edge를 'B'로 색칠
    for e in comb:
        G_local[e[0]][e[1]][0]["color"] = "B"


    # 계산
    ans_k, ans_w = KWildSAT(G_local).find_min_k()
    return ans_k


def main():
    ans_tmp = set()

    with ProcessPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(worker, combinations(edges, k)),
            total=nCr(len(edges), k)
        ))

    ans_tmp.update(results)
    print(f"n={n}, k={k}, ans_k={sorted(ans_tmp)}")


if __name__ == "__main__":
    main()
