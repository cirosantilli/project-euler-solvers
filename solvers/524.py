# Project Euler 524 - First Sort II
# Solution by bitmask DFS + memoization + lexicographic rank
# No external libraries.

def F_of_perm(p):
    """Compute F(P) directly from the definition using rank-counts.
    O(n^2) but only used on tiny test instances."""
    n = len(p)
    m = p[0]
    f = 0
    for i in range(1, n):
        x = p[i]
        if x > m:
            m = x
        else:
            r = 0
            for j in range(i):
                if p[j] < x:
                    r += 1
            f += 1 << r
    return f


def lexicographic_rank(perm):
    """1-indexed rank of perm among all permutations of 1..n in lexicographic order."""
    n = len(perm)
    # factorials
    fact = [1] * (n + 1)
    for i in range(2, n + 1):
        fact[i] = fact[i - 1] * i
    # available numbers as bitmask
    avail = (1 << n) - 1
    rank0 = 0  # 0-indexed
    for i, x in enumerate(perm):
        lower_mask = avail & ((1 << (x - 1)) - 1)
        cnt_smaller = lower_mask.bit_count()
        rank0 += cnt_smaller * fact[n - 1 - i]
        avail &= ~(1 << (x - 1))
    return rank0 + 1


def find_lexicographically_first_perm(n, k):
    """Return the lexicographically first permutation of 1..n with F(P) = k.

    Uses DFS in lexicographic order with memoization of failed states.

    State is (mask, remaining_k). The current prefix maximum is simply mask.bit_length().
    """
    full_mask = (1 << n) - 1
    failed = set()

    def dfs(mask, rem_k):
        if mask == full_mask:
            return [] if rem_k == 0 else None
        key = (mask, rem_k)
        if key in failed:
            return None

        prefix_max = mask.bit_length()  # maximum value already placed

        for v in range(1, n + 1):
            bit = 1 << (v - 1)
            if mask & bit:
                continue

            # rank r = how many already-used values are < v
            lower_used = mask & ((1 << (v - 1)) - 1)
            r = lower_used.bit_count()

            if v > prefix_max:
                contrib = 0
            else:
                contrib = 1 << r

            if contrib > rem_k:
                continue

            res = dfs(mask | bit, rem_k - contrib)
            if res is not None:
                return [v] + res

        failed.add(key)
        return None

    ans = dfs(0, k)
    if ans is None:
        raise ValueError("No permutation found — should not happen for valid (n,k).")
    return tuple(ans)


def Q(n, k):
    """Compute Q(n,k) as defined in the problem."""
    perm = find_lexicographically_first_perm(n, k)
    return lexicographic_rank(perm)


def R_of_k(k):
    """Compute R(k) = min_n Q(n,k).

    A key property used: if k is even, then Q(n,k) = Q(n-1,k/2).
    So we can strip powers of 2 from k while decreasing n, without changing the rank.

    We work directly at the minimal n needed after this reduction.
    """
    # Minimal n such that k < 2^(n-1)
    n = k.bit_length() + 1
    while k % 2 == 0:
        k //= 2
        n -= 1
    return Q(n, k)


def run_tests():
    # Example given in statement
    assert F_of_perm((4, 1, 3, 2)) == 5

    # All Q(4,k) values given in statement
    expected = {
        0: 1,
        4: 2,
        2: 3,
        6: 5,
        1: 7,
        5: 8,
        3: 12,
        7: 19,
    }
    for k, ans in expected.items():
        got = Q(4, k)
        assert got == ans, (k, got, ans)


def main():
    run_tests()
    k = 12 ** 12
    ans = R_of_k(k)
    print(ans)


if __name__ == "__main__":
    main()

