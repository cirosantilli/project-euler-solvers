import math
from typing import List, Tuple


def precompute_mu_phi(n: int) -> Tuple[List[int], List[int]]:
    mu = [0] * (n + 1)
    phi = [0] * (n + 1)
    primes: List[int] = []
    is_comp = [False] * (n + 1)
    mu[1] = 1
    phi[1] = 1
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
            phi[i] = i - 1
        for p in primes:
            v = i * p
            if v > n:
                break
            is_comp[v] = True
            if i % p == 0:
                mu[v] = 0
                phi[v] = phi[i] * p
                break
            mu[v] = -mu[i]
            phi[v] = phi[i] * (p - 1)
    return mu, phi


def compute_T(n: int) -> int:
    mu, phi = precompute_mu_phi(n)

    s_abs_all = [0] * (n + 1)
    for t in range(1, n + 1):
        if t % 2 == 0:
            m = t // 2
            s_abs_all[t] = 2 * m * (m - 1)
        else:
            m = t // 2
            s_abs_all[t] = 2 * m * m

    s_abs = [0] * (n + 1)
    for d in range(1, n + 1):
        md = mu[d]
        if md == 0:
            continue
        coeff = md * d
        limit = n // d
        for t in range(1, limit + 1):
            s_abs[d * t] += coeff * s_abs_all[t]

    total = 0
    for s in range(3, n + 1):
        m = n // s
        sum_g = m * (m + 1) // 2
        phi_half = phi[s] // 2
        base = phi_half * s

        total += base * sum_g  # gamma = 1
        if s % 2 == 0:
            total += base * sum_g  # gamma = -1
        else:
            total += (s_abs[s] // 2) * sum_g

        if s % 4 == 2:
            lsum = s_abs[s] // 2
        else:
            lsum = base
        total += 2 * lsum * sum_g  # gamma = +/- i

    n_max = 2 * int((n // 3) ** 0.5) + 2
    lim = int(n_max**0.5) + 2
    pairs: List[Tuple[int, int, int]] = []
    for a in range(1, lim):
        for b in range(1, lim):
            nn = a * a + b * b
            if nn < 5 or nn > n_max:
                continue
            if math.gcd(a, b) != 1:
                continue
            pairs.append((a, b, nn))

    for a, b, nn in pairs:
        d0 = nn if nn % 2 == 1 else nn // 2
        if nn % 2 == 1:
            c1 = b * b - a * a
            s1 = 2 * a * b
        else:
            # a and b are odd here; divide by 2 to match denominator d0
            c1 = (b * b - a * a) // 2
            s1 = a * b

        powers = [1]
        while powers[-1] * d0 <= n:
            powers.append(powers[-1] * d0)

        p_max = 0
        for k in range(2, len(powers)):
            if powers[k] * (k + 1) <= n:
                p_max = k
        if p_max < 2:
            continue

        c_nums = [0] * (p_max + 1)
        s_nums = [0] * (p_max + 1)
        c_nums[1] = c1
        s_nums[1] = s1
        for k in range(2, p_max + 1):
            c_nums[k] = c_nums[k - 1] * c1 - s_nums[k - 1] * s1
            s_nums[k] = s_nums[k - 1] * c1 + c_nums[k - 1] * s1

        for p in range(2, p_max + 1):
            d = powers[p]
            for q in range(1, p):
                if math.gcd(p, q) != 1:
                    continue
                m = n // (d * (p + q))
                if m == 0:
                    continue
                factor = powers[p - q]
                a_re = p * c_nums[q] * factor + q * c_nums[p]
                a_im = p * s_nums[q] * factor - q * s_nums[p]
                lval = abs(a_re) + abs(a_im)
                total += 2 * lval * (m * (m + 1) // 2)

    return total


def main() -> None:
    assert compute_T(3) == 10
    assert compute_T(10) == 524
    assert compute_T(100) == 580442
    assert compute_T(1000) == 583108600

    result = compute_T(1_000_000)
    print(result)


if __name__ == "__main__":
    main()
