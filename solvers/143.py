from math import gcd, isqrt


def torricelli_sums(limit: int) -> set[int]:
    """
    Return the set of all distinct values s = p+q+r <= limit
    for Torricelli triangles (Project Euler 143).
    """
    # adjacency: connect x <-> y if x^2 + y^2 + xy is a perfect square
    adj: dict[int, set[int]] = {}

    def add_edge(a: int, b: int) -> None:
        if a == b:
            return
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    # Generate all valid (x, y) pairs using Eisenstein triple parameterization:
    # x = k(m^2 - n^2), y = k(2mn + n^2), gcd(m,n)=1, (m-n)%3!=0
    M = isqrt(limit) + 2
    for m in range(2, M + 1):
        mm = m * m
        for n in range(1, m):
            if gcd(m, n) != 1:
                continue
            if (m - n) % 3 == 0:
                continue

            nn = n * n
            x0 = mm - nn
            y0 = 2 * m * n + nn

            max0 = x0 if x0 > y0 else y0
            kmax = limit // max0
            for k in range(1, kmax + 1):
                add_edge(x0 * k, y0 * k)

    # Any (p,q,r) corresponds to a 3-clique: q in N(p), r in N(p), and r in N(q)
    sums: set[int] = set()
    for p, neighset in adj.items():
        neigh = sorted(neighset)
        ln = len(neigh)
        for i in range(ln):
            q = neigh[i]
            pq = p + q
            if pq >= limit:
                break
            qset = adj[q]
            for j in range(i + 1, ln):
                r = neigh[j]
                s = pq + r
                if s > limit:
                    break
                if r in qset:
                    sums.add(s)

    return sums


def euler143(limit: int = 120000) -> int:
    return sum(torricelli_sums(limit))


if __name__ == "__main__":
    # Known value from the problem statement's example (a=399,b=455,c=511 => p+q+r=784):
    assert 784 in torricelli_sums(784)

    # Solve the actual problem:
    print(euler143(120000))
