#!/usr/bin/env python3
"""
Project Euler 660
Pandigital triangles in base n with a 120° angle.

We must sum the largest sides c of all n-pandigital integer triangles (a,b,c) with
c^2 = a^2 + a*b + b^2, for 9 <= n <= 18, where the base-n digits used across a, b, c
are exactly {0,1,...,n-1} (each exactly once, no leading zeros).
"""

from __future__ import annotations


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def to_base_digits(x: int, base: int) -> list[int]:
    """Return digits of x in the given base, most-significant first."""
    if x == 0:
        return [0]
    out: list[int] = []
    while x:
        x, r = divmod(x, base)
        out.append(r)
    out.reverse()
    return out


def is_n_pandigital_triangle(n: int, a: int, b: int, c: int) -> bool:
    """Check equation and n-pandigital digit condition in base n."""
    if not (a > 0 and b > 0 and c > 0):
        return False
    # 120-degree condition with c opposite 120°
    if a * a + a * b + b * b != c * c:
        return False

    da = to_base_digits(a, n)
    db = to_base_digits(b, n)
    dc = to_base_digits(c, n)

    if da[0] == 0 or db[0] == 0 or dc[0] == 0:
        return False
    if len(da) + len(db) + len(dc) != n:
        return False

    seen = [0] * n
    for d in da + db + dc:
        if d < 0 or d >= n:
            return False
        seen[d] += 1
        if seen[d] > 1:
            return False
    return all(v == 1 for v in seen)


def _iter_bits(mask: int):
    """Yield set bit indices in increasing order."""
    while mask:
        lsb = mask & -mask
        yield lsb.bit_length() - 1
        mask ^= lsb


def solve_base(n: int) -> list[tuple[int, int, int]]:
    """
    Find all n-pandigital triangles for a given base n.

    Digit-by-digit construction in base n (least significant to most significant),
    using a carry variable G:
        F = a^2 + a*b + b^2 - c^2
    Maintaining that F is divisible by n^p after fixing p least-significant digits.

    For p >= 1, the next-digit constraint becomes a linear congruence mod n.
    We use bitmasks to track unused digits and (when possible) modular inverses
    to solve the congruence with minimal branching.
    """
    full_mask = (1 << n) - 1

    # Precompute residue->digits masks for k*d (mod n) and modular inverses when gcd(k,n)=1.
    res_masks = [[0] * n for _ in range(n)]
    inv = [0] * n
    has_inv = [False] * n
    for k in range(n):
        if gcd(k, n) == 1:
            for x in range(1, n):
                if (k * x) % n == 1:
                    inv[k] = x
                    has_inv[k] = True
                    break
        arr = res_masks[k]
        for d in range(n):
            arr[(k * d) % n] |= 1 << d

    sols: set[tuple[int, int, int]] = set()

    # Length partitions: la + lb + lc = n, with la <= lb <= lc (c is always the largest side)
    for la in range(1, n - 1):
        for lb in range(la, n - la):
            lc = n - la - lb
            if lc <= 0 or lc < lb:
                continue

            # Powers of n needed up to lc digits
            pow_n = [1] * (lc + 1)
            for i in range(1, lc + 1):
                pow_n[i] = pow_n[i - 1] * n

            # Choose least significant digits (a0,b0,c0)
            for a0 in range(n):
                if la == 1 and a0 == 0:
                    continue
                for b0 in range(n):
                    if b0 == a0 or (lb == 1 and b0 == 0):
                        continue
                    # Symmetry break when la==lb: swapping a,b gives the same triangle.
                    if la == lb and b0 < a0:
                        continue
                    for c0 in range(n):
                        if c0 == a0 or c0 == b0 or (lc == 1 and c0 == 0):
                            continue

                        F = a0 * a0 + a0 * b0 + b0 * b0 - c0 * c0
                        if F % n:
                            continue
                        G = F // n  # carry after fixing digit 0

                        avail = full_mask ^ (1 << a0) ^ (1 << b0) ^ (1 << c0)

                        # Current prefixes (p digits fixed, starting at p=1)
                        A = a0
                        B = b0
                        C = c0

                        # Maintain these to update the carry efficiently:
                        # X = 2A + B, Y = A + 2B, Z = 2C
                        X = 2 * A + B
                        Y = A + 2 * B
                        Z = 2 * C

                        # Congruence coefficients mod n are constant for all higher digits:
                        alpha = X % n
                        beta = Y % n
                        delta = (
                            -Z
                        ) % n  # because mod equation uses -2C for the c-digit term

                        # Stack for DFS: (p, A, B, C, X, Y, Z, G, avail_mask)
                        stack = [(1, A, B, C, X, Y, Z, G, avail)]

                        while stack:
                            p, A, B, C, X, Y, Z, G, avail = stack.pop()

                            if p == lc:
                                # All digits fixed; equation holds iff final carry is 0, and all digits used.
                                if avail == 0 and G == 0:
                                    a, b = (A, B) if A <= B else (B, A)
                                    sols.add((a, b, C))
                                continue

                            P = pow_n[p]  # n^p

                            a_act = p < la
                            b_act = p < lb

                            lead_a = a_act and (p == la - 1)
                            lead_b = b_act and (p == lb - 1)
                            lead_c = p == lc - 1

                            # Right-hand side of the linear congruence:
                            # alpha*da + beta*db + delta*dc ≡ (-G) (mod n)
                            t = (-G) % n

                            # Candidate digit masks (apply non-leading-zero rule when needed)
                            mask_c = avail & (~1 if lead_c else full_mask)
                            mask_a = (
                                (avail & (~1 if lead_a else full_mask)) if a_act else 0
                            )
                            mask_b = (
                                (avail & (~1 if lead_b else full_mask)) if b_act else 0
                            )

                            if a_act and b_act:
                                # 3 variables: choose which one to solve for (prefer invertible coefficient).
                                cand = []
                                if alpha:
                                    cand.append(("a", alpha, mask_a))
                                if beta:
                                    cand.append(("b", beta, mask_b))
                                if delta:
                                    cand.append(("c", delta, mask_c))
                                if not cand:
                                    continue

                                # Prefer variables with modular inverse (unique solution), then smaller domain.
                                solve_name, solve_k, solve_mask = min(
                                    cand,
                                    key=lambda x: (
                                        0 if has_inv[x[1]] else 1,
                                        x[2].bit_count(),
                                    ),
                                )

                                if solve_name == "c":
                                    for da in _iter_bits(mask_a):
                                        avail1 = avail ^ (1 << da)
                                        mb = mask_b & ~(1 << da)
                                        for db in _iter_bits(mb):
                                            rhs = (t - (alpha * da + beta * db)) % n

                                            if has_inv[delta]:
                                                dc = (inv[delta] * rhs) % n
                                                if (
                                                    ((mask_c >> dc) & 1)
                                                    and dc != da
                                                    and dc != db
                                                ):
                                                    L = da * X + db * Y - dc * Z
                                                    Q = (
                                                        da * da
                                                        + da * db
                                                        + db * db
                                                        - dc * dc
                                                    )
                                                    newG = (G + L + P * Q) // n

                                                    newA = A + da * P
                                                    newB = B + db * P
                                                    newC = C + dc * P
                                                    newX = X + (2 * da + db) * P
                                                    newY = Y + (da + 2 * db) * P
                                                    newZ = Z + 2 * dc * P
                                                    stack.append(
                                                        (
                                                            p + 1,
                                                            newA,
                                                            newB,
                                                            newC,
                                                            newX,
                                                            newY,
                                                            newZ,
                                                            newG,
                                                            avail1
                                                            ^ (1 << db)
                                                            ^ (1 << dc),
                                                        )
                                                    )
                                            else:
                                                cm = (
                                                    res_masks[delta][rhs]
                                                    & mask_c
                                                    & ~(1 << da)
                                                    & ~(1 << db)
                                                )
                                                for dc in _iter_bits(cm):
                                                    L = da * X + db * Y - dc * Z
                                                    Q = (
                                                        da * da
                                                        + da * db
                                                        + db * db
                                                        - dc * dc
                                                    )
                                                    newG = (G + L + P * Q) // n

                                                    newA = A + da * P
                                                    newB = B + db * P
                                                    newC = C + dc * P
                                                    newX = X + (2 * da + db) * P
                                                    newY = Y + (da + 2 * db) * P
                                                    newZ = Z + 2 * dc * P
                                                    stack.append(
                                                        (
                                                            p + 1,
                                                            newA,
                                                            newB,
                                                            newC,
                                                            newX,
                                                            newY,
                                                            newZ,
                                                            newG,
                                                            avail1
                                                            ^ (1 << db)
                                                            ^ (1 << dc),
                                                        )
                                                    )

                                elif solve_name == "a":
                                    for db in _iter_bits(mask_b):
                                        avail1 = avail ^ (1 << db)
                                        mc = mask_c & ~(1 << db)
                                        for dc in _iter_bits(mc):
                                            rhs = (t - (beta * db + delta * dc)) % n

                                            if has_inv[alpha]:
                                                da = (inv[alpha] * rhs) % n
                                                if (
                                                    ((mask_a >> da) & 1)
                                                    and da != db
                                                    and da != dc
                                                ):
                                                    L = da * X + db * Y - dc * Z
                                                    Q = (
                                                        da * da
                                                        + da * db
                                                        + db * db
                                                        - dc * dc
                                                    )
                                                    newG = (G + L + P * Q) // n

                                                    newA = A + da * P
                                                    newB = B + db * P
                                                    newC = C + dc * P
                                                    newX = X + (2 * da + db) * P
                                                    newY = Y + (da + 2 * db) * P
                                                    newZ = Z + 2 * dc * P
                                                    stack.append(
                                                        (
                                                            p + 1,
                                                            newA,
                                                            newB,
                                                            newC,
                                                            newX,
                                                            newY,
                                                            newZ,
                                                            newG,
                                                            avail1
                                                            ^ (1 << dc)
                                                            ^ (1 << da),
                                                        )
                                                    )
                                            else:
                                                am = (
                                                    res_masks[alpha][rhs]
                                                    & mask_a
                                                    & ~(1 << db)
                                                    & ~(1 << dc)
                                                )
                                                for da in _iter_bits(am):
                                                    L = da * X + db * Y - dc * Z
                                                    Q = (
                                                        da * da
                                                        + da * db
                                                        + db * db
                                                        - dc * dc
                                                    )
                                                    newG = (G + L + P * Q) // n

                                                    newA = A + da * P
                                                    newB = B + db * P
                                                    newC = C + dc * P
                                                    newX = X + (2 * da + db) * P
                                                    newY = Y + (da + 2 * db) * P
                                                    newZ = Z + 2 * dc * P
                                                    stack.append(
                                                        (
                                                            p + 1,
                                                            newA,
                                                            newB,
                                                            newC,
                                                            newX,
                                                            newY,
                                                            newZ,
                                                            newG,
                                                            avail1
                                                            ^ (1 << dc)
                                                            ^ (1 << da),
                                                        )
                                                    )
                                else:  # solve_name == "b"
                                    for da in _iter_bits(mask_a):
                                        avail1 = avail ^ (1 << da)
                                        mc = mask_c & ~(1 << da)
                                        for dc in _iter_bits(mc):
                                            rhs = (t - (alpha * da + delta * dc)) % n

                                            if has_inv[beta]:
                                                db = (inv[beta] * rhs) % n
                                                if (
                                                    ((mask_b >> db) & 1)
                                                    and db != da
                                                    and db != dc
                                                ):
                                                    L = da * X + db * Y - dc * Z
                                                    Q = (
                                                        da * da
                                                        + da * db
                                                        + db * db
                                                        - dc * dc
                                                    )
                                                    newG = (G + L + P * Q) // n

                                                    newA = A + da * P
                                                    newB = B + db * P
                                                    newC = C + dc * P
                                                    newX = X + (2 * da + db) * P
                                                    newY = Y + (da + 2 * db) * P
                                                    newZ = Z + 2 * dc * P
                                                    stack.append(
                                                        (
                                                            p + 1,
                                                            newA,
                                                            newB,
                                                            newC,
                                                            newX,
                                                            newY,
                                                            newZ,
                                                            newG,
                                                            avail1
                                                            ^ (1 << dc)
                                                            ^ (1 << db),
                                                        )
                                                    )
                                            else:
                                                bm = (
                                                    res_masks[beta][rhs]
                                                    & mask_b
                                                    & ~(1 << da)
                                                    & ~(1 << dc)
                                                )
                                                for db in _iter_bits(bm):
                                                    L = da * X + db * Y - dc * Z
                                                    Q = (
                                                        da * da
                                                        + da * db
                                                        + db * db
                                                        - dc * dc
                                                    )
                                                    newG = (G + L + P * Q) // n

                                                    newA = A + da * P
                                                    newB = B + db * P
                                                    newC = C + dc * P
                                                    newX = X + (2 * da + db) * P
                                                    newY = Y + (da + 2 * db) * P
                                                    newZ = Z + 2 * dc * P
                                                    stack.append(
                                                        (
                                                            p + 1,
                                                            newA,
                                                            newB,
                                                            newC,
                                                            newX,
                                                            newY,
                                                            newZ,
                                                            newG,
                                                            avail1
                                                            ^ (1 << dc)
                                                            ^ (1 << db),
                                                        )
                                                    )

                            elif a_act and not b_act:
                                # 2 variables: alpha*da + delta*dc ≡ t
                                if has_inv[alpha]:
                                    for dc in _iter_bits(mask_c):
                                        rhs = (t - delta * dc) % n
                                        da = (inv[alpha] * rhs) % n
                                        if ((mask_a >> da) & 1) and da != dc:
                                            L = da * X - dc * Z
                                            Q = da * da - dc * dc
                                            newG = (G + L + P * Q) // n

                                            newA = A + da * P
                                            newC = C + dc * P
                                            newX = X + 2 * da * P
                                            newY = Y + da * P
                                            newZ = Z + 2 * dc * P
                                            stack.append(
                                                (
                                                    p + 1,
                                                    newA,
                                                    B,
                                                    newC,
                                                    newX,
                                                    newY,
                                                    newZ,
                                                    newG,
                                                    avail ^ (1 << dc) ^ (1 << da),
                                                )
                                            )
                                else:
                                    for da in _iter_bits(mask_a):
                                        avail1 = avail ^ (1 << da)
                                        rhs = (t - alpha * da) % n
                                        if has_inv[delta]:
                                            dc = (inv[delta] * rhs) % n
                                            if ((mask_c >> dc) & 1) and dc != da:
                                                L = da * X - dc * Z
                                                Q = da * da - dc * dc
                                                newG = (G + L + P * Q) // n

                                                newA = A + da * P
                                                newC = C + dc * P
                                                newX = X + 2 * da * P
                                                newY = Y + da * P
                                                newZ = Z + 2 * dc * P
                                                stack.append(
                                                    (
                                                        p + 1,
                                                        newA,
                                                        B,
                                                        newC,
                                                        newX,
                                                        newY,
                                                        newZ,
                                                        newG,
                                                        avail1 ^ (1 << dc),
                                                    )
                                                )
                                        else:
                                            cm = (
                                                res_masks[delta][rhs]
                                                & mask_c
                                                & ~(1 << da)
                                            )
                                            for dc in _iter_bits(cm):
                                                L = da * X - dc * Z
                                                Q = da * da - dc * dc
                                                newG = (G + L + P * Q) // n

                                                newA = A + da * P
                                                newC = C + dc * P
                                                newX = X + 2 * da * P
                                                newY = Y + da * P
                                                newZ = Z + 2 * dc * P
                                                stack.append(
                                                    (
                                                        p + 1,
                                                        newA,
                                                        B,
                                                        newC,
                                                        newX,
                                                        newY,
                                                        newZ,
                                                        newG,
                                                        avail1 ^ (1 << dc),
                                                    )
                                                )

                            elif (not a_act) and b_act:
                                # 2 variables: beta*db + delta*dc ≡ t
                                if has_inv[beta]:
                                    for dc in _iter_bits(mask_c):
                                        rhs = (t - delta * dc) % n
                                        db = (inv[beta] * rhs) % n
                                        if ((mask_b >> db) & 1) and db != dc:
                                            L = db * Y - dc * Z
                                            Q = db * db - dc * dc
                                            newG = (G + L + P * Q) // n

                                            newB = B + db * P
                                            newC = C + dc * P
                                            newX = X + db * P
                                            newY = Y + 2 * db * P
                                            newZ = Z + 2 * dc * P
                                            stack.append(
                                                (
                                                    p + 1,
                                                    A,
                                                    newB,
                                                    newC,
                                                    newX,
                                                    newY,
                                                    newZ,
                                                    newG,
                                                    avail ^ (1 << dc) ^ (1 << db),
                                                )
                                            )
                                else:
                                    for db in _iter_bits(mask_b):
                                        avail1 = avail ^ (1 << db)
                                        rhs = (t - beta * db) % n
                                        if has_inv[delta]:
                                            dc = (inv[delta] * rhs) % n
                                            if ((mask_c >> dc) & 1) and dc != db:
                                                L = db * Y - dc * Z
                                                Q = db * db - dc * dc
                                                newG = (G + L + P * Q) // n

                                                newB = B + db * P
                                                newC = C + dc * P
                                                newX = X + db * P
                                                newY = Y + 2 * db * P
                                                newZ = Z + 2 * dc * P
                                                stack.append(
                                                    (
                                                        p + 1,
                                                        A,
                                                        newB,
                                                        newC,
                                                        newX,
                                                        newY,
                                                        newZ,
                                                        newG,
                                                        avail1 ^ (1 << dc),
                                                    )
                                                )
                                        else:
                                            cm = (
                                                res_masks[delta][rhs]
                                                & mask_c
                                                & ~(1 << db)
                                            )
                                            for dc in _iter_bits(cm):
                                                L = db * Y - dc * Z
                                                Q = db * db - dc * dc
                                                newG = (G + L + P * Q) // n

                                                newB = B + db * P
                                                newC = C + dc * P
                                                newX = X + db * P
                                                newY = Y + 2 * db * P
                                                newZ = Z + 2 * dc * P
                                                stack.append(
                                                    (
                                                        p + 1,
                                                        A,
                                                        newB,
                                                        newC,
                                                        newX,
                                                        newY,
                                                        newZ,
                                                        newG,
                                                        avail1 ^ (1 << dc),
                                                    )
                                                )

                            else:
                                # Only c still has digits: delta*dc ≡ t
                                rhs = t
                                if has_inv[delta]:
                                    dc = (inv[delta] * rhs) % n
                                    if (mask_c >> dc) & 1:
                                        L = -dc * Z
                                        Q = -dc * dc
                                        newG = (G + L + P * Q) // n

                                        newC = C + dc * P
                                        newZ = Z + 2 * dc * P
                                        stack.append(
                                            (
                                                p + 1,
                                                A,
                                                B,
                                                newC,
                                                X,
                                                Y,
                                                newZ,
                                                newG,
                                                avail ^ (1 << dc),
                                            )
                                        )
                                else:
                                    cm = res_masks[delta][rhs] & mask_c
                                    for dc in _iter_bits(cm):
                                        L = -dc * Z
                                        Q = -dc * dc
                                        newG = (G + L + P * Q) // n

                                        newC = C + dc * P
                                        newZ = Z + 2 * dc * P
                                        stack.append(
                                            (
                                                p + 1,
                                                A,
                                                B,
                                                newC,
                                                X,
                                                Y,
                                                newZ,
                                                newG,
                                                avail ^ (1 << dc),
                                            )
                                        )

    return sorted(sols)


def solve_all() -> int:
    total = 0
    for n in range(9, 19):
        sols = solve_base(n)
        total += sum(c for _, _, c in sols)
    return total


def _run_asserts_from_statement() -> None:
    # From the problem statement:
    # (217,248,403) is a 9-pandigital triangle, and in base 9:
    # 217 = 261_9, 248 = 305_9, 403 = 487_9
    assert to_base_digits(217, 9) == [2, 6, 1]
    assert to_base_digits(248, 9) == [3, 0, 5]
    assert to_base_digits(403, 9) == [4, 8, 7]
    assert is_n_pandigital_triangle(9, 217, 248, 403)


def main() -> None:
    _run_asserts_from_statement()
    ans = solve_all()
    print(ans)


if __name__ == "__main__":
    main()
