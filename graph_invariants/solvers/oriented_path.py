from sage.all import *

def find_oriented_path(G, P, len):
    assert G.is_directed(), "Both G must be directed graphs."
    assert isinstance(P, int), "P must be an integer representing a oriented path"

    n = G.num_verts()
    used = [False] * n; used[0] = True
    ret = [0]

    for _ in range(len):
        dir = (P&1); P >>= 1
        flag = True
        for v in range(n):
            if used[v]: continue

            if G.has_edge(ret[-1], v) if dir else G.has_edge(v, ret[-1]):
                used[v] = True
                ret.append(v)
                flag = False
                break
            
        if flag: raise ValueError("No such path exists in this algorithm")
    return ret

def decode_oriented_path(P, len):
    ret = []
    for _ in range(len):
        dir = (P&1); P >>= 1
        ret.append(dir)
    return "".join("→" if d else "←" for d in ret)

def make_oriented_path(P, length):
    edges = []
    for i in range(length):
        bit = (P & 1); P >>= 1
        edges.append((i, i+1) if bit else (i+1, i))

    V = list(range(length + 1))
    return DiGraph([V, edges], loops=False, multiedges=False)


if __name__ == "__main__":
    op = 0b1010001 
    length = 7
    print(decode_oriented_path(op, length))