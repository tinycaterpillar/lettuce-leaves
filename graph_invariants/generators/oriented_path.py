from sage.all import *

def bitmask_to_direction_string(P, len):
    ret = []
    for _ in range(len):
        dir = (P&1); P >>= 1
        ret.append(dir)
    return "".join("→" if d else "←" for d in ret)

def bitmask_to_sage_graph(P, length):
    edges = []
    for i in range(length):
        bit = (P & 1); P >>= 1
        edges.append((i, i+1) if bit else (i+1, i))

    V = list(range(length + 1))
    return DiGraph([V, edges], loops=False, multiedges=False)

def get_alternating_path(length):
    P = 1
    for i in range(length-1):
        P <<= 1
        P |= (i&1)
    return P

if __name__ == "__main__":
    length = 3
    print(bitmask_to_direction_string(get_alternating_path(length), length))