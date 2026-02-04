import os
import networkx as nx
from sage.all import Graph

def decode(g6_string: str) -> nx.Graph:
    """
    Input: g6_string (str): A Graph6-encoded string (e.g., 'DLo')
    Output: nx.Graph: The decoded NetworkX graph
    """
    return nx.from_graph6_bytes(g6_string.encode("ascii"))


def encode(G: nx.Graph) -> str:
    """
    Input: G (nx.Graph): A NetworkX graph
    Output: str: The canonical Graph6 string (House of Graphs format)
    """
    return Graph(G).canonical_label().graph6_string().strip()

def load_graphs(file_path: str) -> list[nx.Graph]:
    """
    Input: file_path (str): Path to a Graph6 (.g6) file
    Output: list[nx.Graph]: A list of NetworkX graphs loaded from the file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.endswith(".g6"):
        raise ValueError("Only Graph6 files (.g6) are supported.")

    graphs = list(nx.read_graph6(file_path))
    print(f"Loaded {len(graphs)} graphs from '{file_path}'.")

    return graphs


if __name__ == "__main__":
    G = nx.complete_graph(8)
    g6 = encode(G)
    print(g6)