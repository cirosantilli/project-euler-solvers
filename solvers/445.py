#!/usr/bin/env python3
"""Project Euler 445: Retractions A

We define affine functions on Z/nZ:
    f_{n,a,b}(x) ≡ a x + b (mod n)
with 0 < a < n and 0 ≤ b < n.
A function is a *retraction* if f(f(x)) ≡ f(x) for all x.
Let R(n) be the number of retractions for n.

For N = 10_000_000, compute
    S(N) = ∑_{k=1..N-1} R(C(N,k))  (mod 1_000_000_007)

No external libraries are used.
"""

from __future__ import annotations

from array import array
from math import isqrt

MOD = 1_000_000_007


def _sieve_spf_and_primes(n: int) -> tuple[array, array, array]:
    """Return (spf, primes, prime_idx).

    spf[x] = smallest prime factor of x (spf[0]=spf[1]=1)
    primes = array of primes ≤ n (ascending)
    prime_idx[p] = (index in primes) + 1 for primes p, else 0

    Uses an odd-only sieve; this is fast enough for n=10^7 in CPython.
    """
    spf = array("I", [0]) * (n + 1)
    prime_idx = array("I", [0]) * (n + 1)
    primes = array("I")

    if n >= 1:
        spf[0] = 1
        spf[1] = 1

    if n >= 2:
        spf[2] = 2
        primes.append(2)
        prime_idx[2] = 1  # 1-based
        for x in range(4, n + 1, 2):
            spf[x] = 2

    limit = isqrt(n)
    for i in range(3, n + 1, 2):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
            prime_idx[i] = len(primes)  # 1-based
            if i <= limit:
                step = i << 1
                start = i * i
                for j in range(start, n + 1, step):
                    if spf[j] == 0:
                        spf[j] = i

    return spf, primes, prime_idx


def _inverses_upto(n: int, mod: int) -> array:
    """inv[i] = i^{-1} (mod mod) for 1 ≤ i ≤ n.

    Requires mod to be prime and n < mod.
    Runs in O(n) time.
    """
    inv = array("I", [0]) * (n + 1)
    inv[1] = 1
    # inv[i] = mod - (mod//i) * inv[mod%i] % mod
    for i in range(2, n + 1):
        inv[i] = (mod - (mod // i) * inv[mod % i] % mod) % mod
    return inv


def _batch_inverse(vals: array, mod: int) -> array:
    """Compute modular inverses for a batch (handles zeros).

    Returns invs where invs[i] = vals[i]^{-1} (mod mod) if vals[i]!=0 else 0.
    Uses a single pow() for the whole batch.
    """
    n = len(vals)
    invs = array("I", [0]) * n

    idxs = array("I")
    prefix = array("I")
    prod = 1

    for i in range(n):
        v = vals[i]
        if v:
            prod = (prod * v) % mod
            idxs.append(i)
            prefix.append(prod)

    if len(idxs) == 0:
        return invs

    inv_all = pow(prod, mod - 2, mod)

    # Standard backward sweep (on the non-zero subarray)
    for j in range(len(idxs) - 1, -1, -1):
        i = idxs[j]
        prev = prefix[j - 1] if j else 1
        invs[i] = (inv_all * prev) % mod
        inv_all = (inv_all * vals[i]) % mod

    return invs


def solve(N: int) -> int:
    """Return S(N) modulo MOD."""
    spf, primes, prime_idx = _sieve_spf_and_primes(N)
    inv_num = _inverses_upto(N, MOD)

    num_primes = len(primes)
    max_exp = array("I", [0]) * num_primes
    offset = array("I", [0]) * num_primes

    # For each prime p, we need inverses of (1 + p^e) for e=1..v_p(N!).
    total_terms = 0
    for idx in range(num_primes):
        p = primes[idx]
        t = N
        e = 0
        while t:
            t //= p
            e += t
        max_exp[idx] = e
        offset[idx] = total_terms
        total_terms += e

    inv_terms = array("I", [0]) * total_terms

    # Build inv_terms in prime order, sequentially.
    # We do modular inverses chunk-wise to avoid O(total_terms) pow() calls.
    CHUNK = 1_000_000
    write_pos = 0
    vals = array("I")

    for idx in range(num_primes):
        p = primes[idx]
        m = max_exp[idx]
        pow_val = p % MOD
        for _ in range(m):
            vals.append((pow_val + 1) % MOD)
            pow_val = (pow_val * p) % MOD
            if len(vals) >= CHUNK:
                invs = _batch_inverse(vals, MOD)
                inv_terms[write_pos : write_pos + len(vals)] = invs
                write_pos += len(vals)
                vals = array("I")

    if len(vals):
        invs = _batch_inverse(vals, MOD)
        inv_terms[write_pos : write_pos + len(vals)] = invs
        write_pos += len(vals)

    assert write_pos == total_terms

    # Walk through binomial coefficients using:
    #   C(N,k) = C(N,k-1) * (N-k+1) / k
    # Maintain sigma*(C(N,k)) = ∏_{p^e || C(N,k)} (1 + p^e) (mod MOD).
    exp = array("I", [0]) * num_primes
    p_pow = array("I", [1]) * num_primes  # p^exp (mod MOD), starts at 1

    prod = 1
    zero_count = 0  # how many factors (1+p^e) are 0 mod MOD

    mid = N // 2
    even = N % 2 == 0

    sum_sigma = 0

    spf_local = spf
    prime_idx_local = prime_idx
    inv_num_local = inv_num
    inv_terms_local = inv_terms
    offset_local = offset
    exp_local = exp
    p_pow_local = p_pow
    mod = MOD

    for k in range(1, mid + 1):
        numer = N - k + 1
        denom = k

        # Multiply by numer
        x = numer
        while x > 1:
            p = spf_local[x]
            pi = prime_idx_local[p] - 1
            cnt = 0
            while x > 1 and spf_local[x] == p:
                x //= p
                cnt += 1

            old_e = exp_local[pi]
            if old_e:
                term_old = p_pow_local[pi] + 1
                if term_old == mod:
                    term_old = 0
                if term_old:
                    prod = (prod * inv_terms_local[offset_local[pi] + old_e - 1]) % mod
                else:
                    zero_count -= 1

            new_e = old_e + cnt
            exp_local[pi] = new_e

            if cnt == 1:
                p_pow_local[pi] = (p_pow_local[pi] * p) % mod
            elif cnt == 2:
                pp = (p * p) % mod
                p_pow_local[pi] = (p_pow_local[pi] * pp) % mod
            else:
                p_pow_local[pi] = (p_pow_local[pi] * pow(p, cnt, mod)) % mod

            term_new = p_pow_local[pi] + 1
            if term_new == mod:
                term_new = 0
            if term_new:
                prod = (prod * term_new) % mod
            else:
                zero_count += 1

        # Divide by denom
        x = denom
        while x > 1:
            p = spf_local[x]
            pi = prime_idx_local[p] - 1
            cnt = 0
            while x > 1 and spf_local[x] == p:
                x //= p
                cnt += 1

            old_e = exp_local[pi]
            # old_e must be > 0
            term_old = p_pow_local[pi] + 1
            if term_old == mod:
                term_old = 0
            if term_old:
                prod = (prod * inv_terms_local[offset_local[pi] + old_e - 1]) % mod
            else:
                zero_count -= 1

            new_e = old_e - cnt
            exp_local[pi] = new_e

            invp = inv_num_local[p]
            if cnt == 1:
                p_pow_local[pi] = (p_pow_local[pi] * invp) % mod
            elif cnt == 2:
                invpp = (invp * invp) % mod
                p_pow_local[pi] = (p_pow_local[pi] * invpp) % mod
            else:
                p_pow_local[pi] = (p_pow_local[pi] * pow(invp, cnt, mod)) % mod

            if new_e:
                term_new = p_pow_local[pi] + 1
                if term_new == mod:
                    term_new = 0
                if term_new:
                    prod = (prod * term_new) % mod
                else:
                    zero_count += 1

        sigma_val = 0 if zero_count else prod

        if even and k == mid:
            sum_sigma += sigma_val
        else:
            sum_sigma += 2 * sigma_val

        # occasional reduction to keep integers small
        if sum_sigma >= (1 << 62):
            sum_sigma %= mod

    sum_sigma %= mod

    # R(n) = sigma*(n) - n and ∑_{k=1..N-1} C(N,k) = 2^N - 2.
    sum_binom = (pow(2, N, mod) - 2) % mod
    return (sum_sigma - sum_binom) % mod


def main() -> None:
    # Test value from the problem statement:
    assert solve(100_000) == 628701600

    N = 10_000_000
    print(solve(N))


if __name__ == "__main__":
    main()
