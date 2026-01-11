from __future__ import annotations

from collections import deque
from typing import Dict, List, Tuple


MOD = 1_000_000_007
TARGET_SUM = 10
MAX_SUM = 10


def build_states() -> Tuple[List[Tuple[int, int]], Dict[Tuple[int, int], int]]:
    init_states = set()
    for first in range(1, 10):
        mask = 1 << first
        init_states.add((mask, mask))

    seen = set(init_states)
    queue: deque[Tuple[int, int]] = deque(init_states)
    while queue:
        e_mask, a_mask = queue.popleft()
        d_zero = bool(a_mask & (1 << TARGET_SUM))
        for digit in range(10):
            e_next = 0
            for s in range(MAX_SUM + 1):
                if e_mask & (1 << s):
                    if s + digit <= MAX_SUM:
                        e_next |= 1 << (s + digit)
            e_next |= 1 << digit

            a_next = 0
            for s in range(MAX_SUM + 1):
                if a_mask & (1 << s):
                    if s + digit <= MAX_SUM:
                        a_next |= 1 << (s + digit)
            if d_zero:
                a_next |= 1 << digit
            if a_next == 0:
                continue
            if a_next & (1 << TARGET_SUM):
                a_next = e_next
            state = (e_next, a_next)
            if state not in seen:
                seen.add(state)
                queue.append(state)

    states = list(seen)
    idx = {st: i for i, st in enumerate(states)}
    return states, idx


def build_transitions(states: List[Tuple[int, int]], idx: Dict[Tuple[int, int], int]) -> List[List[int]]:
    trans: List[List[int]] = [[] for _ in states]
    for i, (e_mask, a_mask) in enumerate(states):
        d_zero = bool(a_mask & (1 << TARGET_SUM))
        for digit in range(10):
            e_next = 0
            for s in range(MAX_SUM + 1):
                if e_mask & (1 << s):
                    if s + digit <= MAX_SUM:
                        e_next |= 1 << (s + digit)
            e_next |= 1 << digit

            a_next = 0
            for s in range(MAX_SUM + 1):
                if a_mask & (1 << s):
                    if s + digit <= MAX_SUM:
                        a_next |= 1 << (s + digit)
            if d_zero:
                a_next |= 1 << digit
            if a_next == 0:
                continue
            if a_next & (1 << TARGET_SUM):
                a_next = e_next
            trans[i].append(idx[(e_next, a_next)])
    return trans


def build_sequences(max_len: int, states: List[Tuple[int, int]], idx: Dict[Tuple[int, int], int], trans: List[List[int]]) -> List[int]:
    n = len(states)
    vec = [0] * n
    for first in range(1, 10):
        mask = 1 << first
        vec[idx[(mask, mask)]] += 1

    accept = [i for i, (_, a_mask) in enumerate(states) if a_mask & (1 << TARGET_SUM)]

    counts = [0] * (max_len + 1)
    if max_len >= 1:
        counts[1] = sum(vec[i] for i in accept) % MOD

    for length in range(2, max_len + 1):
        new_vec = [0] * n
        for i, v in enumerate(vec):
            if v == 0:
                continue
            for j in trans[i]:
                new_vec[j] = (new_vec[j] + v) % MOD
        vec = new_vec
        counts[length] = sum(vec[i] for i in accept) % MOD
    return counts


def berlekamp_massey(seq: List[int]) -> List[int]:
    c = [1]
    b = [1]
    l = 0
    m = 1
    bb = 1
    for i, val in enumerate(seq):
        d = val
        for j in range(1, l + 1):
            d = (d + c[j] * seq[i - j]) % MOD
        if d == 0:
            m += 1
            continue
        t = c[:]
        coef = d * pow(bb, MOD - 2, MOD) % MOD
        while len(c) < len(b) + m:
            c.append(0)
        for j in range(len(b)):
            c[j + m] = (c[j + m] - coef * b[j]) % MOD
        if 2 * l <= i:
            l = i + 1 - l
            b = t
            bb = d
            m = 1
        else:
            m += 1
    return [(-x) % MOD for x in c[1:]]


NTT_MODS = (
    (167772161, 3),
    (469762049, 3),
    (1224736769, 3),
)


def ntt(a: List[int], invert: bool, mod: int, root: int) -> None:
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    length = 2
    while length <= n:
        wlen = pow(root, (mod - 1) // length, mod)
        if invert:
            wlen = pow(wlen, mod - 2, mod)
        for i in range(0, n, length):
            w = 1
            half = i + length // 2
            for j in range(i, half):
                u = a[j]
                v = a[j + length // 2] * w % mod
                a[j] = (u + v) % mod
                a[j + length // 2] = (u - v) % mod
                w = w * wlen % mod
        length <<= 1

    if invert:
        inv_n = pow(n, mod - 2, mod)
        for i in range(n):
            a[i] = a[i] * inv_n % mod


def convolution(a: List[int], b: List[int]) -> List[int]:
    if not a or not b:
        return []
    need = len(a) + len(b) - 1
    n = 1
    while n < need:
        n <<= 1

    results: List[List[int]] = []
    for mod, root in NTT_MODS:
        fa = [x % mod for x in a] + [0] * (n - len(a))
        fb = [x % mod for x in b] + [0] * (n - len(b))
        ntt(fa, False, mod, root)
        ntt(fb, False, mod, root)
        for i in range(n):
            fa[i] = fa[i] * fb[i] % mod
        ntt(fa, True, mod, root)
        results.append(fa[:need])

    m1, _ = NTT_MODS[0]
    m2, _ = NTT_MODS[1]
    m3, _ = NTT_MODS[2]
    m12 = m1 * m2
    inv_m1_mod_m2 = pow(m1, m2 - 2, m2)
    inv_m12_mod_m3 = pow(m12 % m3, m3 - 2, m3)

    combined = [0] * need
    for i in range(need):
        x1 = results[0][i]
        x2 = (results[1][i] - x1) * inv_m1_mod_m2 % m2
        x3 = (results[2][i] - x1 - m1 * x2) * inv_m12_mod_m3 % m3
        combined[i] = (x1 + m1 * x2 + m12 * x3) % MOD
    return combined


def poly_inv(f: List[int], n: int) -> List[int]:
    g = [1]
    while len(g) < n:
        m = min(2 * len(g), n)
        fg = convolution(f[:m], g)[:m]
        for i in range(m):
            fg[i] = (-fg[i]) % MOD
        fg[0] = (fg[0] + 2) % MOD
        g = convolution(g, fg)[:m]
    return g


def poly_mul_mod(a: List[int], b: List[int], mod_poly: List[int], inv_rev: List[int]) -> List[int]:
    k = len(mod_poly) - 1
    conv = convolution(a, b)
    if len(conv) <= k:
        conv.extend([0] * (k - len(conv)))
        return conv
    m = len(conv) - k
    a_rev = conv[::-1][:m]
    q_rev = convolution(a_rev, inv_rev[:m])[:m]
    q = q_rev[::-1]
    qp = convolution(q, mod_poly)
    res = conv[:k]
    for i in range(k):
        if i < len(qp):
            res[i] = (res[i] - qp[i]) % MOD
    return res


def linear_recurrence_fast(coefs: List[int], init: List[int], n: int) -> int:
    k = len(coefs)
    if n < len(init):
        return init[n]

    mod_poly = [(-coefs[k - 1]) % MOD]
    for i in range(k - 2, -1, -1):
        mod_poly.append((-coefs[i]) % MOD)
    mod_poly.append(1)
    rev_mod_poly = mod_poly[::-1]
    inv_rev = poly_inv(rev_mod_poly, k)

    pol = [1] + [0] * (k - 1)
    if k == 1:
        base = [coefs[0] % MOD]
    else:
        base = [0] * k
        base[1] = 1

    exp = n
    while exp:
        if exp & 1:
            pol = poly_mul_mod(pol, base, mod_poly, inv_rev)
        base = poly_mul_mod(base, base, mod_poly, inv_rev)
        exp >>= 1

    ans = 0
    for i in range(k):
        ans = (ans + pol[i] * init[i]) % MOD
    return ans


def prepare_recurrence() -> Tuple[List[int], List[int]]:
    states, idx = build_states()
    trans = build_transitions(states, idx)

    max_len = 2 * len(states)
    counts = build_sequences(max_len, states, idx, trans)
    prefix = [0] * (max_len + 1)
    for i in range(1, max_len + 1):
        prefix[i] = (prefix[i - 1] + counts[i]) % MOD
    coefs = berlekamp_massey(prefix)
    return prefix, coefs


def main() -> None:
    prefix, coefs = prepare_recurrence()
    assert prefix[2] == 9
    assert prefix[5] == 3492

    n = 10**18
    if n < len(prefix):
        result = prefix[n]
    else:
        result = linear_recurrence_fast(coefs, prefix[: len(coefs)], n)
    print(result % MOD)


if __name__ == "__main__":
    main()
