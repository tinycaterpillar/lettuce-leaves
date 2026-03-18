from sage.all import *

def reachable_at_least_k(G_sage, initial, k):
    assert isinstance(G_sage, Graph), "G_sage must be a simple graph."
    assert 0 <= initial < G_sage.order(), "initial must be a vertex of G_sage."
    assert k > 0, "k must be positive."


    n = G_sage.order()
    if n <= k+1: return [] 
    reachable = [False] * n
    visited = [False] * n
    remain = n - 1
    def dfs(v, dep):
        nonlocal remain

        if k <= dep and not reachable[v]:
            reachable[v] = True
            remain -= 1
            if remain == 0:
                return True

        visited[v] = True
        for u in G_sage.neighbors(v):
            if visited[u]: continue
            if dfs(u, dep + 1): return True
        visited[v] = False

        return False

    dfs(initial, 0)

    return [i for i in range(n) if reachable[i]]

if __name__ == "__main__":
    G = Graph("C^")

    init = 0
    k = max(G.degree())
    ans = reachable_at_least_k(G, init, k)
    print(ans, k)