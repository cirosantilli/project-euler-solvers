#!/usr/bin/env python3
"""
Project Euler 603: Substring Sums of Prime Concatenations

Compute:
    S(C(10^6, 10^12)) mod (10^9+7)

Where:
- S(x) is the sum of all contiguous decimal substrings of x (leading zeros allowed).
- P(n) is the concatenation of the first n primes.
- C(n,k) is k copies of P(n) concatenated.

No external libraries are used.
"""

from __future__ import annotations

import math

MOD = 1_000_000_007


# ---------------------------
# Substring-sum monoid (digit string aggregates)
# ---------------------------


class Node:
    __slots__ = (
        "length",
        "length_mod",
        "pow_len",
        "pow_sum",
        "val",
        "pre",
        "suf",
        "subs",
    )

    def __init__(
        self,
        length: int = 0,
        length_mod: int = 0,
        pow_len: int = 1,  # 10^length mod MOD
        pow_sum: int = 0,  # 10^1 + ... + 10^length mod MOD
        val: int = 0,  # numeric value of whole string mod MOD
        pre: int = 0,  # sum of all prefix values mod MOD
        suf: int = 0,  # sum of all suffix values mod MOD
        subs: int = 0,  # sum of all substring values mod MOD (this is S)
    ) -> None:
        self.length = length
        self.length_mod = length_mod
        self.pow_len = pow_len
        self.pow_sum = pow_sum
        self.val = val
        self.pre = pre
        self.suf = suf
        self.subs = subs

    @staticmethod
    def identity() -> "Node":
        return Node()

    def copy(self) -> "Node":
        return Node(
            self.length,
            self.length_mod,
            self.pow_len,
            self.pow_sum,
            self.val,
            self.pre,
            self.suf,
            self.subs,
        )


def merge(a: Node, b: Node) -> Node:
    """Return the aggregate node for concatenation of digit strings A+B."""
    # Unpack for speed
    La = a.length
    La_mod = a.length_mod
    Lb = b.length
    # Lb_mod = b.length_mod  # only needed for combined length_mod
    out = Node()
    out.length = La + Lb
    out.length_mod = (La_mod + b.length_mod) % MOD

    out.pow_len = (a.pow_len * b.pow_len) % MOD
    out.pow_sum = (a.pow_sum + a.pow_len * b.pow_sum) % MOD

    out.val = (a.val * b.pow_len + b.val) % MOD
    out.pre = (a.pre + a.val * b.pow_sum + b.pre) % MOD
    out.suf = (b.suf + a.suf * b.pow_len + La_mod * b.val) % MOD
    out.subs = (a.subs + b.subs + a.suf * b.pow_sum + La_mod * b.pre) % MOD
    return out


def append_digit_inplace(node: Node, d: int) -> None:
    """Append a single digit d (0..9) to the right of node's digit string."""
    # temp = d + 10*suf + length*d  (mod MOD)
    temp = d + 10 * node.suf + node.length_mod * d
    temp %= MOD

    node.subs += temp
    node.subs %= MOD

    node.suf = temp

    node.pre += node.val * 10 + d
    node.pre %= MOD

    node.val = (node.val * 10 + d) % MOD

    node.pow_sum += node.pow_len * 10
    node.pow_sum %= MOD

    node.pow_len = (node.pow_len * 10) % MOD

    node.length += 1
    node.length_mod += 1
    if node.length_mod >= MOD:
        node.length_mod -= MOD


def build_node_from_string(s: str) -> Node:
    node = Node.identity()
    for ch in s:
        append_digit_inplace(node, ord(ch) - 48)
    return node


def node_pow(base: Node, exp: int) -> Node:
    """Concatenate 'base' with itself exp times using binary exponentiation."""
    res = Node.identity()
    x = base
    e = exp
    while e:
        if e & 1:
            res = merge(res, x)
        e >>= 1
        if e:
            x = merge(x, x)
    return res


# ---------------------------
# Prime generation (odd-only sieve)
# ---------------------------


def nth_prime_upper_bound(n: int) -> int:
    """
    Safe upper bound for the nth prime.
    For n >= 6: p_n < n (log n + log log n) + margin.
    """
    if n < 6:
        return 15
    nn = float(n)
    return int(nn * (math.log(nn) + math.log(math.log(nn)))) + 100


def build_prime_concat_node(n_primes: int) -> Node:
    """
    Build the Node for P(n_primes) by generating the first n_primes primes and
    streaming their decimal digits into the substring-sum aggregate.
    """
    limit = nth_prime_upper_bound(n_primes)

    # Odd-only sieve: sieve[i] corresponds to odd number (2*i + 1)
    size = limit // 2 + 1
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    r = int(math.isqrt(limit))
    # i up to r//2 corresponds to odd p up to sqrt(limit)
    for i in range(1, r // 2 + 1):
        if sieve[i]:
            p = 2 * i + 1
            start = (p * p) // 2
            sieve[start::p] = b"\x00" * (((size - 1 - start) // p) + 1)

    node = Node.identity()

    # Stream primes into node
    count = 0

    # prime 2
    append_digit_inplace(node, 2)
    count = 1
    if count == n_primes:
        return node

    for i in range(1, size):
        if sieve[i]:
            p = 2 * i + 1
            for ch in str(p):
                append_digit_inplace(node, ord(ch) - 48)
            count += 1
            if count == n_primes:
                break

    if count != n_primes:
        # Extremely unlikely with the chosen bound; keep a clear error.
        raise RuntimeError(
            "Prime upper bound too small; increase nth_prime_upper_bound margin."
        )

    return node


# ---------------------------
# Brute helpers for tiny asserts
# ---------------------------


def brute_substring_sum_decimal_string(s: str) -> int:
    tot = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            tot += int(s[i:j])
    return tot


def first_primes_small(n: int) -> list[int]:
    """Simple small-prime generator for asserts."""
    primes: list[int] = []
    x = 2
    while len(primes) < n:
        is_p = True
        r = int(math.isqrt(x))
        for p in primes:
            if p > r:
                break
            if x % p == 0:
                is_p = False
                break
        if is_p:
            primes.append(x)
        x += 1
    return primes


def prime_concat_small(n: int) -> str:
    return "".join(str(p) for p in first_primes_small(n))


# ---------------------------
# Main
# ---------------------------


def main() -> None:
    # Problem statement examples
    assert brute_substring_sum_decimal_string("2024") == 2304
    assert build_node_from_string("2024").subs == 2304

    assert prime_concat_small(7) == "2357111317"
    assert (prime_concat_small(7) * 3) == "235711131723571113172357111317"

    # Required computation
    n = 10**6
    k = 10**12

    base = build_prime_concat_node(n)  # Node for P(10^6)
    ans = node_pow(base, k).subs % MOD  # Node for C(n,k), take S modulo MOD

    print(ans)


if __name__ == "__main__":
    main()
