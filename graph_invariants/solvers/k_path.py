from sage.all import *

def reachable_at_least_k(G_sage, initial, k):
    assert isinstance(G_sage, Graph), "G_sage must be a simple graph."
    assert 0 <= initial < G_sage.order(), "initial must be a vertex of G_sage."
    assert k > 0, "k must be positive."

    n = G_sage.order()
    if n < k+1: return [] 
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

def get_non_initial_vertices(G_sage, k, X=None):
    assert isinstance(G_sage, Graph), "G_sage must be a simple graph."
    assert k > 0, "k must be positive."

    n = G_sage.order()
    if n < k+1: return []
    init = [False] * n
    visited = [False] * n
    def dfs(v, dep):
        if k <= dep: 
            init[v] = True
            return True

        visited[v] = True
        for u in G_sage.neighbors(v):
            if visited[u]: continue
            if dfs(u, dep + 1):
                visited[v] = False
                return True
        visited[v] = False
        
        return False

    for v in range(n):
        if init[v]: continue 
        init[v] = dfs(v, 0)

    return [i for i in range(n) if not init[i]]

def is_bad_internal_block(G_sage, X, k, is_vertex_transitive=False):
    assert isinstance(G_sage, Graph), "G_sage must be a simple graph."
    assert k > 0, "k must be positive."

    n = G_sage.order()
    if n < k+1: return False

    X_lis = [False]*n
    for i in X: X_lis[i] = True
    init = [False] * n
    visited = [False] * n
    def dfs(v, dep):
        if k <= dep and X_lis[v]:
            init[v] = True
            return True

        visited[v] = True
        for u in G_sage.neighbors(v):
            if visited[u]: continue
            if dfs(u, dep + 1):
                visited[v] = False
                return True
        visited[v] = False
        
        return False

    if is_vertex_transitive: return dfs(X[0], 0)
    for v in X:
        if init[v]: continue
        init[v] = dfs(v, 0)
    
    return all(init[i] for i in X)

if __name__ == "__main__":
    G = Graph("C^")

    init = 0
    k = max(G.degree())
    ans = reachable_at_least_k(G, init, k)
    print(ans, k)