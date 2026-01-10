#!/usr/bin/env python3
"""
Project Euler 623 - Lambda Count

We count alpha-equivalence classes of closed lambda terms by size (symbols):
  Variable: size 1
  Application: (M N): size = 2 + size(M) + size(N)   (parentheses)
  Abstraction: (λx.M): size = 5 + size(M)            ( ( λ x . ) )

Using de Bruijn indices eliminates alpha-equivalence issues.

Let T_k(z) be the ordinary generating function counting lambda-terms
in an environment with k bound variables available (i.e. depth k).
Then:
    T_k = k*z + z^5*T_{k+1} + z^2*T_k^2

We set U_k = z^2*T_k to remove the shift in the quadratic term:
    U_k = U_k^2 + k*z^3 + z^5*U_{k+1}

So U_k solves:
    U_k^2 - U_k + X_k = 0   where X_k = k*z^3 + z^5*U_{k+1}

Choose the solution with U_k(0)=0:
    U_k = (1 - sqrt(1 - 4*X_k)) / 2

We compute sqrt(1-4X) using Newton iteration for inverse square root
(which avoids polynomial inversion):
    g ≈ (R)^(-1/2)
    g' = g * (3 - R*g^2) / 2
Then sqrt(R) = R*g.

Polynomial multiplication is done quickly via Kronecker substitution:
pack coefficients into a large integer in base 2^80 so no carries occur.

We also exploit depth truncation:
To compute U_k up to degree D_k = (N+2) - 5k, we don't need higher degrees.
"""

MOD = 1_000_000_007
INV2 = (MOD + 1) // 2

# Kronecker substitution packing base: must exceed maximal convolution coefficient.
# With limit <= 2003 and coefficients < MOD, max sum < 2^71, so 2^80 is safe.
BASE_BITS = 80
MASK = (1 << BASE_BITS) - 1


def poly_mul(a, b, limit):
    """Multiply polynomials a and b modulo MOD, truncated to 'limit' coeffs."""
    la = min(len(a), limit)
    lb = min(len(b), limit)
    if la == 0 or lb == 0:
        return [0] * limit

    # Trim trailing zeros for speed
    while la > 0 and a[la - 1] == 0:
        la -= 1
    while lb > 0 and b[lb - 1] == 0:
        lb -= 1
    if la == 0 or lb == 0:
        return [0] * limit

    # For tiny sizes, naive multiplication is faster than packing big ints.
    if la * lb <= 8000:
        res = [0] * limit
        for i in range(la):
            ai = a[i]
            if ai:
                # only compute needed prefix
                maxj = min(lb, limit - i)
                for j in range(maxj):
                    res[i + j] = (res[i + j] + ai * b[j]) % MOD
        return res

    # Pack into big integers A = sum a[i] << (BASE_BITS*i), similarly for B.
    A = 0
    for i in range(la):
        A |= (a[i] % MOD) << (BASE_BITS * i)

    B = 0
    for i in range(lb):
        B |= (b[i] % MOD) << (BASE_BITS * i)

    P = A * B  # big-int multiplication in C (fast)

    # Extract coefficients (no carries because BASE_BITS chosen large enough)
    m = min(limit, la + lb - 1)
    res = [0] * limit
    for i in range(m):
        res[i] = ((P >> (BASE_BITS * i)) & MASK) % MOD
    return res


def poly_invsqrt(R, n):
    """
    Compute g(z) = R(z)^(-1/2) mod z^n for R(0)=1 using Newton iteration:
        g_{new} = g * (3 - R*g^2) / 2
    """
    g = [1]
    m = 1
    while m < n:
        m2 = min(2 * m, n)
        g2 = poly_mul(g, g, m2)
        rg2 = poly_mul(R[:m2], g2, m2)

        v = [0] * m2
        v[0] = (3 - rg2[0]) % MOD
        for i in range(1, m2):
            v[i] = (-rg2[i]) % MOD

        g = poly_mul(g, v, m2)
        g = [(x * INV2) % MOD for x in g]
        m = m2

    if len(g) < n:
        g += [0] * (n - len(g))
    return g[:n]


def compute_U0(N_symbols):
    """
    Compute U_0 up to degree (N_symbols + 2), using depth truncation:
        D_k = (N_symbols + 2) - 5k
    """
    maxdeg = N_symbols + 2
    # deepest k that can still contribute within maxdeg:
    K = (maxdeg - 3) // 5

    U_next = [0] * (maxdeg - 5 * (K + 1) + 1 if K + 1 > 0 else maxdeg + 1)

    for k in range(K, -1, -1):
        Dk = maxdeg - 5 * k
        n = Dk + 1

        # Build X_k = k*z^3 + z^5*U_{k+1}
        X = [0] * n
        if 3 < n:
            X[3] = k % MOD
        # z^5 shift of U_next
        for i in range(5, n):
            j = i - 5
            if j < len(U_next):
                X[i] = U_next[j]

        # R = 1 - 4X
        R = [0] * n
        R[0] = 1
        for i in range(1, n):
            R[i] = (-4 * X[i]) % MOD

        inv_sqrt = poly_invsqrt(R, n)
        sqrtR = poly_mul(R, inv_sqrt, n)

        # U = (1 - sqrtR)/2, constant term is 0 since sqrtR[0]=1
        U = [0] * n
        for i in range(1, n):
            U[i] = (-sqrtR[i] * INV2) % MOD

        U_next = U

    # pad to full length maxdeg+1 if needed (should already be)
    if len(U_next) < maxdeg + 1:
        U_next += [0] * (maxdeg + 1 - len(U_next))
    return U_next[: maxdeg + 1]


def solve():
    N = 2000
    U0 = compute_U0(N)

    # T_0[n] = coefficient of z^n in T_0 = U0[n+2]
    T0 = [0] * (N + 1)
    for n in range(N + 1):
        idx = n + 2
        if idx < len(U0):
            T0[n] = U0[idx] % MOD

    # Lambda(n) = sum_{m<=n} T0[m]
    lam = [0] * (N + 1)
    s = 0
    for n in range(N + 1):
        s = (s + T0[n]) % MOD
        lam[n] = s

    # Required asserts from problem statement
    assert lam[6] == 1
    assert lam[9] == 2
    assert lam[15] == 20
    assert lam[35] == 3166438

    print(lam[N])


if __name__ == "__main__":
    solve()
