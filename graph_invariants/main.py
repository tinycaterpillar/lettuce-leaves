import argparse
import networkx as nx
import sqlite3
from pathlib import Path

from utils import load_graphs, setup_logger
from db import upsert_result
from solver import ChromaticNumberSAT

def get_prediction(delta):
    if delta == 3: return 7
    elif delta < 8: return delta+5
    else: return 3*delta//2+1

parser = argparse.ArgumentParser(
    description="Process graph data folder"
)
parser.add_argument(
    "folder",
    type=str,
    help="Path to data folder (e.g. data/11to20)"
)
args = parser.parse_args()

folder = Path(args.folder)
path = str(list(folder.glob("*.g6"))[0])
logger = setup_logger(folder)
g_list = load_graphs(path)
logger.info(f"[PROCESSING] {folder} ({len(g_list)} graphs)")

rows = []
for ind, g in enumerate(g_list):
    if ind%10 == 0: logger.info(f"[PROCESSING] {ind}th graphs")
    delta = max(dict(g.degree()).values())
    if delta < 3: continue

    g2 = nx.power(g, 2)
    predict = get_prediction(delta)
    sat, _ = ChromaticNumberSAT(g2).solve_k(predict)
    # χ(G2) <= predict
    if sat:
        support, _ = ChromaticNumberSAT(g2).solve_k(predict-1)
        # χ(G2) = predict
        if not support:
            upsert_result(g=g, file_path=path, graph_index=ind, prediction=predict, conjecture_role="TIGHT")
            logger.info(f"[TIGHT] found, {ind}th graphs")
    # χ(G2) > predict
    else:
        upsert_result(g=g, file_path=path, graph_index=ind, prediction=predict, conjecture_role="COUNTEREXAMPLE")
        logger.info(f"[COUNTEREXAMPLE] found, {ind}th graphs")

logger.info(f"[DONE] Finished checking all {len(g_list)} graphs across all .g6 files.")