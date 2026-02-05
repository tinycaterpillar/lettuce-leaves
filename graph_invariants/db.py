import os
import sqlite3
import pandas as pd
import datetime
from pathlib import Path
from typing import Optional, Union
import networkx as nx

from utils import encode

PROJECT_ROOT = Path(__file__).resolve().parents[0]
RESULT_DIR = PROJECT_ROOT / "results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = RESULT_DIR / "results.db"


def init_db(db_path: Union[str, Path] = DB_PATH):
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                -- 1. Graph identification
                g6 TEXT PRIMARY KEY,
                file_name TEXT,
                graph_index INTEGER,

                -- 2. Graph structure
                vertex_count INTEGER,
                edge_count INTEGER,
                max_deg INTEGER,

                -- 3. Results
                prediction REAL,
                conjecture_role TEXT NOT NULL
                DEFAULT 'UNKNOWN'
                CHECK (conjecture_role IN (
                    'TIGHT',
                    'COUNTEREXAMPLE',
                    'SUPPORTING',
                    'UNKNOWN'
                )),

                -- 4. Metadata
                timestamp TEXT,
                note TEXT,
                URL TEXT
            )
        """)
        conn.commit()


UPSERT_SQL = """
INSERT INTO results (
    g6, file_name, graph_index,
    vertex_count, edge_count, max_deg,
    prediction, conjecture_role,
    timestamp, note, URL
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(g6) DO UPDATE SET
    file_name = excluded.file_name,
    graph_index = excluded.graph_index,
    vertex_count = excluded.vertex_count,
    edge_count = excluded.edge_count,
    max_deg = excluded.max_deg,
    prediction = excluded.prediction,
    conjecture_role = excluded.conjecture_role,
    timestamp = excluded.timestamp,
    note = excluded.note,
    URL = excluded.URL;
"""


def upsert_result(
    *,
    g: nx.graph,
    file_path: str,
    graph_index: int,
    prediction: Optional[float] = None,
    conjecture_role: str = "UNKNOWN",
    note: Optional[str] = None,
    url: Optional[str] = None,
    db_path: Union[str, Path] = DB_PATH,
):
    g6 = encode(g)
    file_name = os.path.basename(file_path)
    vertex_count = g.number_of_nodes()
    edge_count = g.number_of_edges()
    max_deg = max(dict(g.degree()).values())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = (
        g6,
        file_name,
        graph_index,
        vertex_count,
        edge_count,
        max_deg,
        prediction,
        conjecture_role,
        timestamp,
        note,
        url,
    )

    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute(UPSERT_SQL, row)
        conn.commit()


def export_to_excel_single_sheet(db_path: Union[str, Path] = DB_PATH):
    """Export DB to a single Excel sheet."""
    db_path = Path(db_path)
    excel_path = db_path.with_suffix(".xlsx")

    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query("SELECT * FROM results", conn)

    df.to_excel(excel_path, index=False)
    print(f"[INFO] Exported results to {excel_path}")


if __name__ == "__main__":
    # init_db()

    export_to_excel_single_sheet()
