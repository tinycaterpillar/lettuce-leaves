# Graph Dataset Information

## 📘 Description
This dataset contains **connected, C₅-free graphs** — that is, graphs that do **not contain an induced 5-cycle (C₅)**.  
All graphs are obtained from the **House of Graphs** database.

Each file stores multiple graphs encoded in **Graph6 (.g6)** format, which is directly compatible with Python’s `networkx.read_graph6()` function.



## 📂 File Naming Convention
Files follow this pattern:

```
list_{#graphs}_graphs_{#min_vertex}_to_{#max_vertex}.g6
```

### Examples
- `list_2000_graphs_5_to_7.g6` → 2000 graphs with 5–7 vertices  
- `list_150_graphs_8_to_9.g6` → 150 graphs with 8–9 vertices


## 🧩 Graph Properties
- **Connected** – each graph has a single connected component.  
- **C₅-free** – no induced subgraph isomorphic to a 5-cycle.  

## 📎 Reference
- Source: [House of Graphs](https://houseofgraphs.org/)
- Graph format: [Graph6 specification (NetworkX docs)](https://networkx.org/documentation/stable/reference/readwrite/graph6.html)

11->1006700565

https://github.com/markusa4/satsuma


sqlite3 results.db "SELECT g6, Is_induced_C5_free FROM results WHERE status='COUNTER';"