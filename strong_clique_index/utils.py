import os
import networkx as nx
import matplotlib.pyplot as plt

def load_graphs(file_path: str):
    """Load graphs from a Graph6 (.g6) file and return them as a list of NetworkX Graph objects."""
    
    # Check if the file path is valid
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Ensure the file has the correct extension
    if not file_path.endswith(".g6"):
        raise ValueError("Only Graph6 files (.g6) are supported.")
    
    # Read graphs from the file
    graphs = list(nx.read_graph6(file_path))
    
    # Print how many graphs were loaded
    print(f"Loaded {len(graphs)} graphs from '{file_path}'.")
    
    # Return the list of graphs
    return graphs

def display(graph: nx.Graph):
    """Display a NetworkX graph using matplotlib."""
    plt.figure(figsize=(6, 6))
    pos = nx.spring_layout(graph)  # Layout for positioning nodes
    nx.draw(graph, pos, with_labels=True, node_size=500, node_color="lightblue", font_size=10)
    plt.show()