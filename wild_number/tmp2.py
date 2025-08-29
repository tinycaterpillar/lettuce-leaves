import networkx as nx
from itertools import combinations
from tqdm import tqdm
from math import comb as nCr
from concurrent.futures import ProcessPoolExecutor

from utils import show_graph
from solver import KWildSAT 

n = 9

G = nx.complete_graph(n, create_using=nx.MultiGraph)
nx.set_edge_attributes(G, {e: "A" for e in G.edges(keys=True)}, name="color")
e = list(G.edges())[0]

# 선택된 edge를 'B'로 색칠
G[e[0]][e[1]][0]["color"] = "B"

# 계산
ans_k, ans_w = KWildSAT(G).solve_for_k(6, info=True)

show_graph(G, ans_w)
print(ans_k)