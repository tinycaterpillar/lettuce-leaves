import os
import sqlite3
import pandas as pd
import datetime
from pathlib import Path

from utils import encode

PROJECT_ROOT = Path(__file__).resolve().parents[0]
RESULT_DIR = PROJECT_ROOT / "results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = RESULT_DIR / "results.db"

def init_db(db_path: str = DB_PATH):
    """Initialize the SQLite database for storing results."""
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                -- 1. Graph identification
                g6 TEXT PRIMARY KEY,                       -- Canonical graph6 string (unique ID)
                file_name TEXT,                            -- Source file name
                graph_index INTEGER,                       -- Graph index in the file

                -- 2. Graph structure
                vertex_count INTEGER,                      -- Number of vertices
                edge_count INTEGER,                        -- Number of edges
                max_deg INTEGER,                           -- Maximum vertex degree Δ

                -- 3. Computation results
                chromatic_number_of_square INTEGER,        -- Computed chromatic_number_of_square
                prediction REAL,                           -- Prediction in Wegner's Conjecture

                conjecture_role TEXT NOT NULL               -- Role w.r.t. the conjecture
                DEFAULT 'UNKNOWN'
                CHECK (conjecture_role IN (
                    'TIGHT',
                    'COUNTEREXAMPLE',
                    'SUPPORTING',
                    'UNKNOWN'
                )),

                -- 4. Metadata
                timestamp TEXT,                            -- Computation timestamp (YYYY-MM-DD HH:MM:SS)
                note TEXT,                                 -- Optional note or comment
                URL TEXT                                   -- Optional url of house of graph
            )
        """)
        conn.commit()


def make_row(
    graph,
    file_path: str,
    graph_index: int,
    chromatic_number_of_square: int,
    prediction: float,
    conjecture_role: str,   # 'TIGHT'/'COUNTEREXAMPLE'/'SUPPORTING'/'UNKNOWN'
):
    """
    Return a DB row tuple matching the results table schema.
    """
    g6 = encode(graph)
    file_name = os.path.basename(file_path)

    vertex_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    max_deg = max(dict(graph.degree()).values()) if vertex_count > 0 else 0

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        g6,                 # g6
        file_name,          # file_name
        graph_index,        # graph_index
        vertex_count,       # vertex_count
        edge_count,         # edge_count
        max_deg,            # max_deg
        chromatic_number_of_square,
        prediction,
        conjecture_role,
        timestamp,
    )


UPSERT_SQL = """
INSERT INTO results (
    g6, file_name, graph_index,
    vertex_count, edge_count, max_deg,
    chromatic_number_of_square, prediction, conjecture_role,
    timestamp
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(g6) DO UPDATE SET
    file_name = excluded.file_name,
    graph_index = excluded.graph_index,
    vertex_count = excluded.vertex_count,
    edge_count = excluded.edge_count,
    max_deg = excluded.max_deg,
    chromatic_number_of_square = excluded.chromatic_number_of_square,
    prediction = excluded.prediction,
    conjecture_role = excluded.conjecture_role,
    timestamp = excluded.timestamp;
"""

def save_rows(
    rows: list[tuple],
    db_path: str | Path = DB_PATH,
):
    """
    rows: [(g6, file_name, graph_index, vertex_count, edge_count, max_deg,
            chromatic_number_of_square, prediction, conjecture_role, timestamp), ...]
    """
    if not rows:
        return

    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        conn.executemany(UPSERT_SQL, rows)
        conn.commit()


def export_to_excel_single_sheet(db_path: str = DB_PATH) -> None:
    """
    Export all rows from the results table into a single Excel sheet.
    """
    db_path = Path(db_path)
    excel_path = db_path.with_suffix(".xlsx")

    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query("SELECT * FROM results", conn)

    df.to_excel(excel_path, index=False)

    print(f"[INFO] Exported all results to {excel_path}")


if __name__ == "__main__":
    # init_db()
    export_to_excel_single_sheet()