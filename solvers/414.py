from array import array

MOD = 10**18


def kaprekar_constant_digits(b: int) -> tuple[int, int, int, int, int]:
    """
    For 5 digits and base b = 6t+3 != 9, the Kaprekar constant C_b (as 5 base-b digits)
    is (4t+2, 2t, b-1, 4t+1, 2t+1).
    """
    t = (b - 3) // 6
    if b != 6 * t + 3 or b == 9:
        raise ValueError("This problem assumes bases b = 6t+3 with b != 9.")
    return (4 * t + 2, 2 * t, b - 1, 4 * t + 1, 2 * t + 1)


def solve() -> int:
    total = 0
    for k in range(2, 301):
        b = 6 * k + 3
        total = (total + S_base(b)) % MOD
    return total


def S_base(b: int) -> int:
    # b = 6t + 3 != 9 (in this problem b >= 15 anyway)
    t = (b - 3) // 6

    # Target state (p*, q*) induced by the Kaprekar constant digit-multiset
    p_star = 4 * t + 2
    q_star = 2 * t + 1

    # Triangular indexing for all valid states (p,q) with 0 <= q <= p <= b-1:
    # idx(p,q) = p(p+1)/2 + q
    def idx(p: int, q: int) -> int:
        return (p * (p + 1)) // 2 + q

    size = b * (b + 1) // 2
    target = idx(p_star, q_star)

    nxt = array("I", [0]) * size  # next state index
    w = array("Q", [0]) * size  # weight (# of i mapping to this state)

    # Build transitions + weights for all p >= 1 (p=0 => all digits equal => sb(i)=0)
    for p in range(1, b):
        base = (p * (p + 1)) // 2
        bp = b - p

        # -------- q = 0 --------
        # Result digits are (p-1, b-1, b-1, b-1, b-p) before re-sorting.
        c = p - 1
        a = bp
        if c > a:
            mn, mx = a, c
        else:
            mn, mx = c, a
        p2 = b - 1 - mn
        q2 = b - 1 - mx
        nxt[base + 0] = idx(p2, q2)

        # Count of numbers for (p,0): (b-p) * (20p - 10)
        w[base + 0] = bp * (20 * p - 10)

        # -------- 1 <= q <= p-1 --------
        for q in range(1, p):
            a1 = p
            a2 = bp
            a3 = q - 1
            a4 = b - q - 1

            # sorting network for 4 values -> a1 <= a2 <= a3 <= a4
            if a1 > a2:
                a1, a2 = a2, a1
            if a3 > a4:
                a3, a4 = a4, a3
            if a1 > a3:
                a1, a3 = a3, a1
            if a2 > a4:
                a2, a4 = a4, a2
            if a2 > a3:
                a2, a3 = a3, a2

            p2 = b - 1 - a1
            q2 = a4 - a2
            nxt[base + q] = idx(p2, q2)

            # Count for 0<q<p: (b-p) * (120*q*(p-q) - 20)
            w[base + q] = bp * (120 * q * (p - q) - 20)

        # -------- q = p --------
        q = p
        a1 = p
        a2 = bp
        a3 = q - 1
        a4 = b - q - 1

        if a1 > a2:
            a1, a2 = a2, a1
        if a3 > a4:
            a3, a4 = a4, a3
        if a1 > a3:
            a1, a3 = a3, a1
        if a2 > a4:
            a2, a4 = a4, a2
        if a2 > a3:
            a2, a3 = a3, a2

        p2 = b - 1 - a1
        q2 = a4 - a2
        nxt[base + p] = idx(p2, q2)

        # Count for q=p: (b-p) * (30p - 10)
        w[base + p] = bp * (30 * p - 10)

    # Distances to target in the functional graph
    dist = array("h", [-1]) * size
    dist[0] = 0
    dist[target] = 0

    total = 0
    for i in range(1, size):
        if dist[i] != -1:
            continue
        cur = i
        path = []
        while dist[cur] == -1:
            path.append(cur)
            cur = nxt[cur]
        d = dist[cur]
        for node in reversed(path):
            d += 1
            dist[node] = d
            # sb = dist + 1 for all non-constant numbers in this class
            total += w[node] * (d + 1)

    # Target state's contribution: sb = 1 for the whole target class...
    total += w[target] * 1
    # ...except for i == C_b itself where sb(C_b)=0, so subtract 1.
    total -= 1

    return total % MOD


if __name__ == "__main__":
    # --- Examples given in the statement ---
    assert kaprekar_constant_digits(15) == (10, 4, 14, 9, 5)
    assert kaprekar_constant_digits(21) == (14, 6, 20, 13, 7)

    assert S_base(15) == 5_274_369
    assert S_base(111) == 400_668_930_299

    print(solve())
