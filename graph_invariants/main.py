import networkx as nx

from utils import load_graphs, setup_logger
from db import save_graph
from solvers import ChromaticNumberSAT

def get_prediction(delta):
    if delta == 3: return 7
    elif delta < 8: return delta+5
    else: return 3*delta//2+1

if __name__ == "__main__":
    folder = "data/1to10"
    path = "data/1to10/list_1448_graphs_1to10.g6"
    logger = setup_logger(folder)
    g_list = load_graphs(path)
    logger.info(f"[PROCESSING] {folder} ({len(g_list)} graphs)")

    for ind, g in enumerate(g_list):
        if ind%100 == 0: logger.info(f"[PROCESSING] {ind}th graphs")
        delta = max(dict(g.degree()).values())
        if delta < 3: continue

        g2 = nx.power(g, 2)
        chi, _ = ChromaticNumberSAT(g2).chromatic_number()
        predict = get_prediction(delta)
        if predict <= chi:
            rule = "COUNTEREXAMPLE" if chi > predict else 'TIGHT'
            logger.info(f"[{rule}] found")
            save_graph(g, path, ind, chi, predict, rule)

    logger.info(f"[DONE] Finished checking all {len(g_list)} graphs across all .g6 files.")
    