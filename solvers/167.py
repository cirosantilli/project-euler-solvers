from array import array


def ulam_sequence(a: int, b: int, n_terms: int) -> list[int]:
    """
    Slow but simple generator for small n_terms (used only for problem-statement asserts).
    """
    seq = [a, b]
    while len(seq) < n_terms:
        x = seq[-1] + 1
        while True:
            # count representations x = seq[i] + seq[j] with i < j (two-pointer since seq is sorted)
            i, j = 0, len(seq) - 1
            reps = 0
            while i < j:
                s = seq[i] + seq[j]
                if s == x:
                    reps += 1
                    if reps > 1:
                        break
                    i += 1
                    j -= 1
                elif s < x:
                    i += 1
                else:
                    j -= 1
            if reps == 1:
                seq.append(x)
                break
            x += 1
    return seq


def ulam_2_v_k(v: int, k: int) -> int:
    """
    Compute U(2, v)_k for odd v >= 5.

    After the second even term (which is 2v+2), all terms are odd.
    For an odd x, the only possible representations are:
        x = 2 + (x-2)     and/or     x = (2v+2) + (x-2v-2)
    so x is in the sequence iff exactly one of (x-2) and (x-2v-2) is in the sequence.
    This becomes an XOR recurrence over odd indices, i.e. an LFSR, hence purely periodic.
    """
    if k == 1:
        return 2
    if k == 2:
        return v

    # For k beyond the early small terms, the k-th term is the (k-2)-th odd term overall
    # because there are exactly two even terms in the whole sequence.
    target_odd = k - 2  # 1-indexed among odd terms

    m = v + 1  # recurrence order; second even term is 2v+2 = 2m
    n = (v - 1) // 2

    # f[t] = 1 iff odd number (2t+1) is in U(2,v).
    # Initially, odds v, v+2, ..., 2v+1 are all included => indices t = n..2n+1 are 1.
    init_bits = bytearray(m)  # f[0..m-1] covers odds up to 2m-1 = 2v+1
    for t in range(n, 2 * n + 2):  # t = n..2n+1
        init_bits[t] = 1

    # State: last m bits, with bit0=newest=f[m-1], bit(m-1)=oldest=f[0]
    state = 0
    for i in range(m):
        state |= init_bits[m - 1 - i] << i
    init_state = state
    mask = (1 << m) - 1

    # Generate bits until the state repeats; period is then found.
    bits = bytearray(init_bits)
    period = 0
    while True:
        new_bit = (state & 1) ^ ((state >> (m - 1)) & 1)  # newest XOR oldest
        state = ((state << 1) & mask) | new_bit
        bits.append(new_bit)
        period += 1
        if state == init_state:
            break

    cycle = bits[:period]  # one full period of f[0..]
    ones_pos = array("I", (i for i, b in enumerate(cycle) if b))
    ones_per_period = len(ones_pos)

    q, r = divmod(target_odd - 1, ones_per_period)  # r is 0-indexed inside the period
    t = q * period + ones_pos[r]  # index of the target odd number
    return 2 * t + 1


def solve(k: int = 10**11) -> int:
    return sum(ulam_2_v_k(2 * n + 1, k) for n in range(2, 11))


if __name__ == "__main__":
    # Problem statement example: U(1,2) begins with 1,2,3,4,6,8,11
    assert ulam_sequence(1, 2, 7) == [1, 2, 3, 4, 6, 8, 11]

    print(solve())
