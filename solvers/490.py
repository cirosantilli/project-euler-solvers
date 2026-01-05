#!/usr/bin/env python3
"""
Project Euler 490 - Jumping Frog

We count Hamiltonian paths from 1 to n in the graph on {1..n} with edges between
vertices at distance <= 3. Let f(n) be the number of such paths ending at n.

The key facts used here are:
  1) f(n) satisfies a fixed linear recurrence of order 8.
  2) We need S(L) = sum_{n=1..L} f(n)^3 (mod 1e9) for huge L (1e14).
     Using the 8x8 companion matrix A for f, we can compute the sum of cubes
     with a tensor-power "sum of powers" doubling method in O(8^4 log L).

No external libraries are used.
"""

MOD = 10**9

# Exact initial values (validated by brute force for small n)
# f(1)..f(8)
F_INIT = [1, 1, 1, 2, 6, 14, 28, 56]


# For n >= 9:
# f(n) = 2 f(n-1) - f(n-2) + 2 f(n-3) + f(n-4) + f(n-5) - f(n-7) - f(n-8)
def f_recurrence_next(f_nm1, f_nm2, f_nm3, f_nm4, f_nm5, f_nm6, f_nm7, f_nm8):
    return 2 * f_nm1 - f_nm2 + 2 * f_nm3 + f_nm4 + f_nm5 - f_nm7 - f_nm8


def f_exact_up_to(n):
    """Return list f[0..n] with f[0]=0, exact integers."""
    if n <= 0:
        return [0]
    f = [0] + F_INIT[:]  # indices: 1..8 available
    if n <= 8:
        return f[: n + 1]
    # Extend
    for k in range(9, n + 1):
        f.append(
            f_recurrence_next(
                f[k - 1],
                f[k - 2],
                f[k - 3],
                f[k - 4],
                f[k - 5],
                f[k - 6],
                f[k - 7],
                f[k - 8],
            )
        )
    return f


def build_companion_matrix(mod):
    """
    State vector is:
        X_n = [f(n), f(n-1), ..., f(n-7)]^T
    Then X_{n+1} = A * X_n (mod mod).
    """
    # f(n+1) in terms of f(n..n-7):
    # f(n+1) = 2 f(n) - f(n-1) + 2 f(n-2) + f(n-3) + f(n-4) - f(n-6) - f(n-7)
    coeff = [2, -1, 2, 1, 1, 0, -1, -1]
    A = [[0] * 8 for _ in range(8)]
    A[0] = [(c % mod) for c in coeff]
    for i in range(1, 8):
        A[i][i - 1] = 1
    return A


def mat_mul8(A, B, mod):
    """8x8 matrix multiplication modulo mod, exploiting sparsity."""
    res = [[0] * 8 for _ in range(8)]
    for i in range(8):
        Ai = A[i]
        for k in range(8):
            aik = Ai[k]
            if aik:
                Bk = B[k]
                for j in range(8):
                    res[i][j] = (res[i][j] + aik * Bk[j]) % mod
    return res


def tensor_from_vec(v, mod):
    """Return flattened 8x8x8 tensor for v⊗v⊗v (mod mod)."""
    T = [0] * 512
    vv = [x % mod for x in v]
    for i in range(8):
        vi = vv[i]
        for j in range(8):
            vij = (vi * vv[j]) % mod
            base = i * 64 + j * 8
            for k in range(8):
                T[base + k] = (vij * vv[k]) % mod
    return T


def tensor_transform(M, T, mod):
    """
    Apply (M ⊗ M ⊗ M) to a flattened 8x8x8 tensor T.

    Implemented as 3 successive mode-multiplications, each costing 8^4 operations.
    """
    # mode-1: i index
    U = [0] * 512
    for j in range(8):
        for k in range(8):
            base_jk = j * 8 + k
            for i in range(8):
                row = M[i]
                s = 0
                # sum over p
                for p in range(8):
                    s += row[p] * T[p * 64 + base_jk]
                U[i * 64 + base_jk] = s % mod

    # mode-2: j index
    V = [0] * 512
    for i in range(8):
        ioff = i * 64
        for k in range(8):
            for j in range(8):
                row = M[j]
                s = 0
                for q in range(8):
                    s += row[q] * U[ioff + q * 8 + k]
                V[ioff + j * 8 + k] = s % mod

    # mode-3: k index
    W = [0] * 512
    for i in range(8):
        ioff = i * 64
        for j in range(8):
            joff = ioff + j * 8
            for k in range(8):
                row = M[k]
                s = 0
                for r in range(8):
                    s += row[r] * V[joff + r]
                W[joff + k] = s % mod

    return W


def sum_cubes_from_state(u, length, A, mod):
    """
    Compute sum_{i=0..length-1} ( (A^i u)[0] )^3  (mod mod),
    where u is an 8-vector representing X_8 = [f(8),...,f(1)].

    Uses doubling on:
      P_m = A^m
      T_m = Σ_{i=0..m-1} (A^i u)⊗3
    and then binary decomposition to build the desired length.
    """
    if length <= 0:
        return 0

    # Precompute blocks for powers of two up to length
    blocksP = []
    blocksT = []
    P = [row[:] for row in A]
    T = tensor_from_vec(u, mod)
    m = 1
    while m <= length:
        blocksP.append(P)
        blocksT.append(T)
        # next doubling: (P,T) -> (P^2, T + (P⊗3)T)
        PT = tensor_transform(P, T, mod)
        T = [(T[i] + PT[i]) % mod for i in range(512)]
        P = mat_mul8(P, P, mod)
        m <<= 1

    # Accumulate selected blocks
    Q = [[0] * 8 for _ in range(8)]
    for i in range(8):
        Q[i][i] = 1  # identity = A^0

    acc = [0] * 512
    bit = 0
    rem = length
    while rem:
        if rem & 1:
            contrib = tensor_transform(Q, blocksT[bit], mod)
            acc = [(acc[i] + contrib[i]) % mod for i in range(512)]
            Q = mat_mul8(Q, blocksP[bit], mod)
        rem >>= 1
        bit += 1

    # entry (0,0,0) holds Σ (first_component)^3
    return acc[0]


def S_mod(L, mod=MOD):
    """Compute S(L) = Σ_{n=1..L} f(n)^3 (mod mod)."""
    if L <= 0:
        return 0
    if L <= 8:
        return sum((F_INIT[i] ** 3) % mod for i in range(L)) % mod

    # sum of cubes for n=1..7 directly
    prefix = sum((F_INIT[i] ** 3) % mod for i in range(7)) % mod

    # state at n=8: [f(8), f(7), ..., f(1)]
    u = [
        F_INIT[7],
        F_INIT[6],
        F_INIT[5],
        F_INIT[4],
        F_INIT[3],
        F_INIT[2],
        F_INIT[1],
        F_INIT[0],
    ]
    A = build_companion_matrix(mod)

    # need terms n=8..L inclusive => length = L-7
    tail = sum_cubes_from_state(u, L - 7, A, mod)
    return (prefix + tail) % mod


def run_asserts():
    # f(n) examples
    f = f_exact_up_to(40)
    assert f[6] == 14
    assert f[10] == 254
    assert f[40] == 1439682432976

    # S(L) examples (exact for small)
    S10 = sum(f[i] ** 3 for i in range(1, 11))
    S20 = sum(f[i] ** 3 for i in range(1, 21))
    assert S10 == 18230635
    assert S20 == 104207881192114219

    # modulo examples
    assert S_mod(1000) == 225031475
    assert S_mod(1_000_000) == 363486179


def main():
    run_asserts()
    print(S_mod(10**14))


if __name__ == "__main__":
    main()
