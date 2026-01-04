from __future__ import annotations

from typing import Dict, List, Tuple
import math


MOD = 10**16 + 61


def sieve_primes(n: int) -> List[int]:
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    limit = int(n**0.5)
    for i in range(2, limit + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


def exponent_in_factorial(n: int, p: int) -> int:
    e = 0
    while n:
        n //= p
        e += n
    return e


def v_factor(n: int, p: int) -> int:
    cnt = 0
    while n % p == 0:
        n //= p
        cnt += 1
    return cnt


def find_primitive_root_5pow(mod: int) -> int:
    phi = mod - mod // 5
    for g in range(2, mod):
        if math.gcd(g, mod) != 1:
            continue
        if pow(g, phi // 2, mod) == 1:
            continue
        if pow(g, phi // 5, mod) == 1:
            continue
        return g
    raise ValueError("primitive root not found")


def build_log_table_5pow(v: int) -> Tuple[int, List[int]]:
    if v == 0:
        return 1, [0]
    mod = 5**v
    phi = 4 * 5 ** (v - 1)
    g = find_primitive_root_5pow(mod)
    log = [-1] * mod
    cur = 1
    for e in range(phi):
        log[cur] = e
        cur = (cur * g) % mod
    return mod, log


def build_map_2pow(u: int) -> Tuple[int, int, List[Tuple[int, int]]]:
    if u <= 1:
        mod = 1 << u
        mp = [(-1, -1)] * mod
        mp[1 % mod] = (0, 0)
        return 1, 1, mp
    mod = 1 << u
    if u == 2:
        mp = [(-1, -1)] * mod
        mp[1] = (0, 0)
        mp[3] = (1, 0)
        return 2, 1, mp
    mod_a = 2
    mod_b = 1 << (u - 2)
    mp = [(-1, -1)] * mod
    for a in range(mod_a):
        sign = -1 if a else 1
        for b in range(mod_b):
            val = (sign * pow(5, b, mod)) % mod
            mp[val] = (a, b)
    return mod_a, mod_b, mp


def lcm(a: int, b: int) -> int:
    return a // math.gcd(a, b) * b


def build_dp(
    n: int,
    primes: List[int],
    exps: Dict[int, int],
    u: int,
    v: int,
    mod: int,
) -> List[List[List[int]]]:
    mod_a, mod_b, map2 = build_map_2pow(u)
    mod2 = 1 << u if u > 0 else 1
    mod5, log5 = build_log_table_5pow(v)
    mod_c = 1 if v == 0 else 4 * 5 ** (v - 1)

    dp = [[[0] * mod_c for _ in range(mod_b)] for _ in range(mod_a)]
    dp[0][0][0] = 1

    for p in primes:
        if p == 2 or p == 5:
            continue
        e = exps[p]
        if u > 0:
            a_p, b_p = map2[p % mod2]
        else:
            a_p, b_p = 0, 0
        if v > 0:
            c_p = log5[p % mod5]
        else:
            c_p = 0

        if a_p == 0 and b_p == 0 and c_p == 0:
            mul = (e + 1) % mod
            for a in range(mod_a):
                for b in range(mod_b):
                    row = dp[a][b]
                    for i in range(mod_c):
                        row[i] = (row[i] * mul) % mod
            continue

        ord_a = 1 if mod_a == 1 or a_p == 0 else 2
        ord_b = 1 if mod_b == 1 or b_p == 0 else mod_b // math.gcd(b_p, mod_b)
        ord_c = 1 if mod_c == 1 or c_p == 0 else mod_c // math.gcd(c_p, mod_c)
        l = lcm(lcm(ord_a, ord_b), ord_c)

        total = e + 1
        use_full_cycle = total > l
        if use_full_cycle:
            q, rem = divmod(total, l)
            residues = range(l)
        else:
            residues = range(total)
            q = rem = 0

        new = [[[0] * mod_c for _ in range(mod_b)] for _ in range(mod_a)]
        for r in residues:
            if use_full_cycle:
                count = q + (1 if r < rem else 0)
            else:
                count = 1
            if count == 0:
                continue
            da = (a_p * r) % mod_a if mod_a > 1 else 0
            db = (b_p * r) % mod_b if mod_b > 1 else 0
            dc = (c_p * r) % mod_c if mod_c > 1 else 0

            count_mod = count % mod
            for a in range(mod_a):
                a_dst = (a + da) % mod_a
                for b in range(mod_b):
                    b_dst = (b + db) % mod_b
                    src = dp[a][b]
                    dst = new[a_dst][b_dst]
                    if dc:
                        rot = src[-dc:] + src[:-dc]
                        for i in range(mod_c):
                            dst[i] = (dst[i] + count_mod * rot[i]) % mod
                    else:
                        for i in range(mod_c):
                            dst[i] = (dst[i] + count_mod * src[i]) % mod

        dp = new

    return dp


def count_F_factorial(n: int, d: int) -> int:
    k = len(str(d))
    t2 = v_factor(d, 2)
    t5 = v_factor(d, 5)

    v2n = exponent_in_factorial(n, 2)
    v5n = exponent_in_factorial(n, 5)

    primes = sieve_primes(n)
    exps = {p: exponent_in_factorial(n, p) for p in primes}

    if t2 < k:
        a_values = [t2]
    else:
        a_values = range(k, v2n + 1)
    if t5 < k:
        b_values = [t5]
    else:
        b_values = range(k, v5n + 1)

    dp_cache: Dict[Tuple[int, int], List[List[List[int]]]] = {}
    total = 0

    mod2_full = 1 << k
    mod5_full = 5**k

    for a in a_values:
        if a > v2n:
            continue
        for b in b_values:
            if b > v5n:
                continue
            if t2 < k and a != t2:
                continue
            if t2 >= k and a < k:
                continue
            if t5 < k and b != t5:
                continue
            if t5 >= k and b < k:
                continue

            u = 0 if a >= k else k - a
            v = 0 if b >= k else k - b

            if u > 0:
                inv5b = pow(pow(5, b, mod2_full), -1, mod2_full)
                r2_full = (d * inv5b) % mod2_full
                r2 = (r2_full >> a) % (1 << u)
            else:
                r2 = 0

            if v > 0:
                inv2a = pow(pow(2, a, mod5_full), -1, mod5_full)
                r5_full = (d * inv2a) % mod5_full
                r5 = (r5_full // (5**b)) % (5**v)
            else:
                r5 = 0

            if u == 0 and v == 0:
                if (u, v) not in dp_cache:
                    dp_cache[(u, v)] = build_dp(n, primes, exps, u, v, MOD)
                dp = dp_cache[(u, v)]
                total = (total + dp[0][0][0]) % MOD
                continue

            if u == 0:
                r = r5
            elif v == 0:
                r = r2
            else:
                m2 = 1 << u
                m5 = 5**v
                inv_m2 = pow(m2, -1, m5)
                r = (r2 + m2 * ((r5 - r2) * inv_m2 % m5)) % (m2 * m5)

            if (u, v) not in dp_cache:
                dp_cache[(u, v)] = build_dp(n, primes, exps, u, v, MOD)
            dp = dp_cache[(u, v)]

            mod_a, mod_b, map2 = build_map_2pow(u)
            mod5, log5 = build_log_table_5pow(v)
            if u > 0:
                a_r, b_r = map2[r % (1 << u)]
                if a_r < 0:
                    continue
            else:
                a_r, b_r = 0, 0
            if v > 0:
                c_r = log5[r % mod5]
                if c_r < 0:
                    continue
            else:
                c_r = 0

            total = (total + dp[a_r][b_r][c_r]) % MOD

    return total % MOD


def main() -> None:
    assert count_F_factorial(12, 12) == 11
    assert count_F_factorial(50, 123) == 17888

    result = count_F_factorial(10**6, 65432)
    print(result % MOD)


if __name__ == "__main__":
    main()
