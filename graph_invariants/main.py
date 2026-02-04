import argparse
import networkx as nx
import sqlite3
from pathlib import Path

from utils import load_graphs, setup_logger
from db import DB_PATH, make_row, save_rows
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
    if ind%100 == 0: logger.info(f"[PROCESSING] {ind}th graphs")
    delta = max(dict(g.degree()).values())
    if delta < 3: continue

    g2 = nx.power(g, 2)
    chi, _ = ChromaticNumberSAT(g2).chromatic_number()
    predict = get_prediction(delta)
    if predict <= chi:
        rule = "COUNTEREXAMPLE" if chi > predict else 'TIGHT'
        rows.append(make_row(g, path, ind, chi, predict, rule))
        logger.info(f"[{rule}] found")

save_rows(rows)
logger.info(f"[DONE] Finished checking all {len(g_list)} graphs across all .g6 files.")