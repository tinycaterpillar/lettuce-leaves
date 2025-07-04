# Self-Complementary Graph Checker

This project consists of two parts:

1. A **C++ program** that generates suitable and graphical degree sequences for self-complementary graphs.
2. A **Python program** that tests whether randomly generated graphs from these sequences are truly self-complementary using NetworkX.


## 🔧 Part 1: Degree Sequence Generator (C++)

Input: A single integer `n` representing the number of vertices.  
- Only accepts `n ≡ 0 (mod 4)` or `n ≡ 1 (mod 4)`.

Output:  
- Writes all valid **suitable + graphical** degree sequences to `data/seq.txt`.

## 🧪 Part 2: Self-Complementarity Tester (Python)

It will:
- Load all degree sequences from `data/seq.txt`
- For each sequence:
  - Run `max_trials` randomized graph realizations using `havel_hakimi_graph + double_edge_swap`
  - Check if the generated graph is **isomorphic to its complement**
- If a counterexample is found:
  - The graph and its complement are visualized
  - The program stops early


## 📂 Folder Structure
.  
├── data/  
│   └── seq.txt  
├── degree_sequences.cpp  
└── check_self_complementary.py  

## 📌 Notes

- All input sequences are assumed to be:
  - **suitable** for self-complementary graphs
  - **graphical** (checked by the C++ generator)
- Visualization is skipped if all graphs are self-complementary.
- For large graphs, Kamada-Kawai layout can be slow — switch to `spring_layout` if needed.
