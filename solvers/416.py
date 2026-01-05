from __future__ import annotations

from typing import List, Tuple


MOD = 10**9


def build_transitions(
    k: int, mod: int
) -> Tuple[List[List[Tuple[int, int, bool]]], int]:
    # States are (a, c) where a is count of paths with offset 0, c with offset 2.
    # b is implied by k - a - c.
    idx = {}
    states: List[Tuple[int, int]] = []
    for a in range(k + 1):
        for c in range(k - a + 1):
            idx[(a, c)] = len(states)
            states.append((a, c))

    # Precompute binomial coefficients up to k.
    comb = [[0] * (k + 1) for _ in range(k + 1)]
    for n in range(k + 1):
        comb[n][0] = comb[n][n] = 1
        for r in range(1, n):
            comb[n][r] = comb[n - 1][r - 1] + comb[n - 1][r]

    transitions: List[List[Tuple[int, int, bool]]] = [[] for _ in range(len(states))]
    for i, (a, c) in enumerate(states):
        b = k - a - c
        for a0 in range(a + 1):
            for a1 in range(a - a0 + 1):
                a2 = a - a0 - a1
                # Multinomial coefficient for splitting a into a0,a1,a2.
                coeff = comb[a][a0] * comb[a - a0][a1]
                a_new = a0 + b
                c_new = a2
                j = idx[(a_new, c_new)]
                transitions[i].append((j, coeff % mod, a_new == 0))
    target = idx[(k, 0)]
    return transitions, target


def compute_sequence(k: int, n_terms: int, mod: int) -> List[int]:
    transitions, target = build_transitions(k, mod)
    size = len(transitions)
    dp0 = [0] * size
    dp1 = [0] * size
    dp0[target] = 1

    res = [0] * n_terms
    res[0] = 1  # F(m, 1) = 1

    for _ in range(1, n_terms):
        # Advance one position, counting a miss if no path lands (a_new == 0).
        new0 = [0] * size
        new1 = [0] * size
        for s in range(size):
            v0 = dp0[s]
            v1 = dp1[s]
            if v0 == 0 and v1 == 0:
                continue
            for j, c, is_zero in transitions[s]:
                if is_zero:
                    if v0:
                        new1[j] = (new1[j] + v0 * c) % mod
                else:
                    if v0:
                        new0[j] = (new0[j] + v0 * c) % mod
                    if v1:
                        new1[j] = (new1[j] + v1 * c) % mod
        dp0, dp1 = new0, new1
        res[_] = (dp0[target] + dp1[target]) % mod

    return res


def matmul(a: List[List[int]], b: List[List[int]], mod: int) -> List[List[int]]:
    n = len(a)
    res = [[0] * n for _ in range(n)]
    for i in range(n):
        ai = a[i]
        ri = res[i]
        for k in range(n):
            aik = ai[k]
            if aik == 0:
                continue
            bk = b[k]
            for j in range(n):
                ri[j] = (ri[j] + aik * bk[j]) % mod
    return res


def matadd(a: List[List[int]], b: List[List[int]], mod: int) -> List[List[int]]:
    n = len(a)
    res = [[0] * n for _ in range(n)]
    for i in range(n):
        ai = a[i]
        bi = b[i]
        ri = res[i]
        for j in range(n):
            ri[j] = (ai[j] + bi[j]) % mod
    return res


def matvec(v: List[int], a: List[List[int]], mod: int) -> List[int]:
    n = len(v)
    res = [0] * n
    for i in range(n):
        vi = v[i]
        if vi == 0:
            continue
        ai = a[i]
        for j in range(n):
            res[j] = (res[j] + vi * ai[j]) % mod
    return res


def compute_f(m: int, n: int, mod: int) -> int:
    if n <= 1:
        return 1 % mod

    k = 2 * m
    transitions, target = build_transitions(k, mod)
    size = len(transitions)

    # Build matrices A (no-miss transitions) and B (transitions that miss a square).
    a_mat = [[0] * size for _ in range(size)]
    b_mat = [[0] * size for _ in range(size)]
    for s in range(size):
        for j, c, is_zero in transitions[s]:
            if is_zero:
                b_mat[s][j] = (b_mat[s][j] + c) % mod
            else:
                a_mat[s][j] = (a_mat[s][j] + c) % mod

    exp = n - 1
    res_a = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    res_b = [[0] * size for _ in range(size)]
    base_a = a_mat
    base_b = b_mat

    while exp:
        if exp & 1:
            ra = matmul(res_a, base_a, mod)
            rb = matadd(matmul(res_b, base_a, mod), matmul(res_a, base_b, mod), mod)
            res_a, res_b = ra, rb
        ba = matmul(base_a, base_a, mod)
        bb = matadd(matmul(base_b, base_a, mod), matmul(base_a, base_b, mod), mod)
        base_a, base_b = ba, bb
        exp >>= 1

    start = [0] * size
    start[target] = 1
    v_a = matvec(start, res_a, mod)
    v_b = matvec(start, res_b, mod)
    return (v_a[target] + v_b[target]) % mod


def compute_f_small(m: int, n: int, mod: int) -> int:
    k = 2 * m
    seq = compute_sequence(k, n, mod)
    return seq[n - 1] % mod


def main() -> None:
    # Given examples.
    assert compute_f_small(1, 3, MOD) == 4
    assert compute_f_small(1, 4, MOD) == 15
    assert compute_f_small(1, 5, MOD) == 46
    assert compute_f_small(2, 3, MOD) == 16
    assert compute_f_small(2, 100, MOD) == 429_619_151

    ans = compute_f(10, 10**12, MOD)
    print(f"{ans:09d}")


if __name__ == "__main__":
    main()
