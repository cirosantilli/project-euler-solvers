#!/usr/bin/env python3
"""
Project Euler 434: Rigid Graphs

We have an m×n grid of square cells. Each cell may (or may not) contain a diagonal brace.
The orientation (\\ or /) is irrelevant for this problem, and adding both diagonals is treated
the same as adding just one: each cell is simply "braced" or "unbraced".

A classical result (Bolker–Crapo) shows that such a braced grid is rigid in the plane iff the
associated "brace graph" is connected:
- Create a bipartite graph with m "row" vertices and n "column" vertices.
- For every braced cell (row i, column j), add an edge between row i and column j.
Then the grid is rigid  <=>  this bipartite graph is connected.

Therefore R(m,n) equals the number of connected bipartite graphs on a fixed labeled bipartition
of sizes (m,n), i.e. connected subgraphs of K_{m,n}.
We compute these counts for 1<=m,n<=100 and sum them modulo 1000000033.
"""

MOD = 1000000033


def build_binom(nmax: int, mod: int):
    """Pascal-triangle binomial coefficients C(n,k) mod mod for 0<=n<=nmax."""
    binom = [[0] * (nmax + 1) for _ in range(nmax + 1)]
    for n in range(nmax + 1):
        binom[n][0] = 1
        binom[n][n] = 1
        for k in range(1, n):
            binom[n][k] = (binom[n - 1][k - 1] + binom[n - 1][k]) % mod
    return binom


def solve(N: int = 100, mod: int = MOD) -> int:
    # Precompute powers of two up to N*N (since total graphs = 2^(m*n)).
    pow2 = [1] * (N * N + 1)
    for k in range(1, N * N + 1):
        pow2[k] = (pow2[k - 1] * 2) % mod

    def total_graphs(m: int, n: int) -> int:
        return pow2[m * n]

    # Binomial coefficients up to N.
    binom = build_binom(N, mod)

    # R[m][n] will store the number of connected bipartite graphs on parts (m,n).
    # For the recurrence we also need the special base case R[1][0]=1 (a single isolated vertex).
    R = [[0] * (N + 1) for _ in range(N + 1)]
    R[1][0] = 1

    # Recurrence:
    # Let F(m,n)=2^(m*n) be the number of all bipartite graphs on (m,n).
    # Fix a specific vertex in the m-side. If its connected component has i vertices on the m-side
    # (including the fixed one) and j vertices on the n-side, then:
    #   choose vertices: C(m-1,i-1)*C(n,j)
    #   choose a connected graph on that component: R(i,j) (with R(1,0)=1)
    #   choose any graph on the remaining vertices: F(m-i, n-j)
    #   and forbid edges between the two parts, which is enforced by multiplying only by F(m-i,n-j).
    # Summing over (i,j) gives F(m,n). Solve for R(m,n) by subtracting all terms except (i,j)=(m,n).
    for m in range(1, N + 1):
        # Column=0: only connected when m=1 (single vertex)
        R[m][0] = 1 if m == 1 else 0

        for n in range(1, N + 1):
            total = total_graphs(m, n)
            sub = 0
            for i in range(1, m + 1):
                combA = binom[m - 1][i - 1]
                if combA == 0:
                    continue
                Ri = R[i]
                for j in range(0, n + 1):
                    if i == m and j == n:
                        continue
                    rij = Ri[j]
                    if rij == 0:
                        continue
                    term = combA * binom[n][j] % mod
                    term = term * rij % mod
                    term = term * total_graphs(m - i, n - j) % mod
                    sub = (sub + term) % mod
            R[m][n] = (total - sub) % mod

    # Tests from the problem statement
    assert R[2][3] == 19
    assert R[5][5] == 23679901
    s5 = sum(R[i][j] for i in range(1, 6) for j in range(1, 6)) % mod
    assert s5 == 25021721

    # Compute S(N)
    ans = sum(R[i][j] for i in range(1, N + 1) for j in range(1, N + 1)) % mod
    return ans


if __name__ == "__main__":
    print(solve())
