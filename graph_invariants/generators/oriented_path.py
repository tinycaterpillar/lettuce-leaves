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

def get_antidirected_path(length):
    P = 1
    for i in range(length-1):
        P <<= 1
        P |= (i&1)
    return P

def canonical_form(P, length):
    return min(P, (((1<<length)-1)^P))

def count_blocks(P, length):
    cnt = 0
    for _ in range(length-1):
        bit = (P & 1); P >>= 1
        if bit != (P&1):
            cnt += 1
    return cnt

def get_oriented_path(length):
    ret = list(set(canonical_form(i, length) for i in range(1<<length)))
    ret.sort(key=lambda x: count_blocks(x, length))
    return ret

if __name__ == "__main__":
    length = 3
    for i in get_oriented_path(length):
        print(bitmask_to_direction_string(i, length))