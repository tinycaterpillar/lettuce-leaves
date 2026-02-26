import os
from sage.all import *

def decode(g6_string: str) -> Graph:
    """
    Input: g6_string (str): A Graph6-encoded string (e.g., 'DLo')
    Output: Graph: The decoded Sage graph
    """
    return Graph(g6_string)


def encode(G: Graph) -> str:
    """
    Input: G (Graph): A Sage graph
    Output: str: The canonical Graph6 string (House of Graphs format)
    """
    return G.canonical_label().graph6_string().strip()


def load_graphs(file_path: str) -> list[Graph]:
    """
    Input: file_path (str): Path to a Graph6 (.g6) file
    Output: list[Graph]: A list of Sage graphs loaded from the file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.endswith(".g6"):
        raise ValueError("Only Graph6 files (.g6) are supported.")

    graphs = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                graphs.append(Graph(line))

    print(f"Loaded {len(graphs)} graphs from '{file_path}'.")
    return graphs


if __name__ == "__main__":
    G = graphs.CompleteGraph(8)
    g6 = encode(G)
    print(g6)