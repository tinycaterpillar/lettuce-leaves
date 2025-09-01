import networkx as nx
from utils import show_graph, random_partition, partitions_fixed_length
import random
from solver import KWildSAT
from multiprocessing import Pool, cpu_count

# 전역 변수로 그래프 템플릿 캐싱
_graph_cache = {}

def get_base_graph(n):
    """n에 대한 기본 complete graph를 캐싱하여 재사용"""
    if n not in _graph_cache:
        G = nx.complete_graph(n=n, create_using=nx.MultiGraph)
        edges = list(G.edges(keys=True))
        _graph_cache[n] = (G, edges)
    return _graph_cache[n]

def worker_optimized(args):
    """
    단일 워커에서 여러 trial을 처리하는 최적화된 버전
    """
    P, n, trial_start, trial_count = args
    results = []
    
    # 캐싱된 그래프와 엣지 리스트 사용
    G_template, edges = get_base_graph(n)
    
    for i in range(trial_count):
        trial_id = trial_start + i
        random.seed(trial_id)
        
        G = G_template.copy()
        partition = random_partition(edges, P)

        # 엣지 색상 할당 최적화
        for ind, edge_list in enumerate(partition):
            color = chr(ord('A') + ind)
            for (u, v, key) in edge_list:
                G[u][v][key]['color'] = color

        ans_k, ans_w = KWildSAT(G).find_min_k(use_external=True)
        results.append(ans_k)
    
    return results

def worker_batch(P, n, trials=100):
    """
    배치 처리로 최적화된 worker 함수
    """
    num_processes = cpu_count()
    trials_per_process = max(1, trials // num_processes)
    
    # 작업을 배치로 분할
    tasks = []
    trial_id = 1
    for _ in range(num_processes):
        actual_trials = min(trials_per_process, trials - (trial_id - 1))
        if actual_trials > 0:
            tasks.append((P, n, trial_id, actual_trials))
            trial_id += actual_trials
    
    with Pool(processes=num_processes) as pool:
        batch_results = pool.map(worker_optimized, tasks)
    
    # 결과 평탄화
    all_results = []
    for batch in batch_results:
        all_results.extend(batch)
    
    return P, max(all_results), min(all_results)

if __name__ == "__main__":
    for n in range(3, 10):
        for l in range(2, n+1):
            maxval, minval = -1, n-1
            parts = list(partitions_fixed_length(n * (n - 1) // 2, l))

            for P in parts:
                _, max_tmp, min_tmp = worker_batch(P, n, 100)
                maxval = max(maxval, max_tmp)
                minval = min(minval, min_tmp)
            
            # 각 (n, l) 결과가 나올 때마다 바로 출력
            print(f"n={n}, l={l}:")
            print("maxval", maxval)
            print("minval", minval)
            print()
            
            # 출력 버퍼 즉시 플러시
            import sys
            sys.stdout.flush()