#!/usr/bin/env python3
"""
Project Euler 680: Yarra Gnisrever

We maintain the array A as a *rope* of arithmetic-progression segments (step +1 or -1),
stored in an implicit treap (randomized balanced binary tree by position).
Each operation reverses a range of positions, implemented by two splits + lazy reversal + two merges.

No external libraries are used.
"""

from array import array


def compute_R(N: int, K: int, mod: int | None = None) -> int:
    """
    Compute R(N, K). If mod is provided, all accumulated sums are kept modulo `mod`
    (suitable for huge N like 1e18).
    """
    MOD = mod
    use_mod = MOD is not None

    # Treap arrays (index 0 is "null")
    lch = array("I", [0])
    rch = array("I", [0])
    prio = array("I", [0])

    seg_len = array("Q", [0])  # length of the segment stored in the node
    seg_start = array("Q", [0])  # first value of the segment (value at offset 0)
    seg_dir = array("b", [0])  # +1 or -1
    rev = array("b", [0])  # lazy reversal flag for subtree
    tot_len = array("Q", [0])  # total number of elements in subtree

    if use_mod:
        # all sums fit into < 2^32 because mod=1e9
        seg_sum = array("I", [0])  # sum of values in node segment (mod MOD)
        seg_k = array("I", [0])  # sum of (k * value_k) within node segment (mod MOD)
        sum_val = array("I", [0])  # subtree sum of values (mod MOD)
        sum_pos = array(
            "I", [0]
        )  # subtree sum of (pos * value_pos), pos from 0 (mod MOD)
    else:
        # exact (used only for the small testcases in this script)
        seg_sum = array("q", [0])
        seg_k = array("q", [0])
        sum_val = array("q", [0])
        sum_pos = array("q", [0])

    # Fast deterministic RNG (xorshift32) for treap priorities
    seed = 2463534242

    def rng32() -> int:
        nonlocal seed
        seed ^= (seed << 13) & 0xFFFFFFFF
        seed ^= (seed >> 17) & 0xFFFFFFFF
        seed ^= (seed << 5) & 0xFFFFFFFF
        return seed & 0xFFFFFFFF

    # Segment sums for arithmetic progression: start + dir*k, k=0..L-1
    if use_mod:

        def tri_mod(L: int) -> int:
            # L*(L-1)/2 mod MOD, computed without modular inverses
            a = L
            b = L - 1
            if a & 1 == 0:
                a //= 2
            else:
                b //= 2
            return (a % MOD) * (b % MOD) % MOD

        def sqsum_mod(L: int) -> int:
            # (L-1)*L*(2L-1)/6 mod MOD, divide by 2 and 3 before multiplying
            a = L - 1
            b = L
            c = 2 * L - 1
            # divide by 2
            if a & 1 == 0:
                a //= 2
            else:
                b //= 2
            # divide by 3
            if a % 3 == 0:
                a //= 3
            elif b % 3 == 0:
                b //= 3
            else:
                c //= 3
            return ((a % MOD) * (b % MOD) % MOD) * (c % MOD) % MOD

        def seg_sums(L: int, start: int, direction: int) -> tuple[int, int]:
            st = start % MOD
            Lm = L % MOD
            tr = tri_mod(L)
            sq = sqsum_mod(L)
            if direction == 1:
                s = (st * Lm + tr) % MOD
                k = (st * tr + sq) % MOD
            else:
                s = (st * Lm - tr) % MOD
                k = (st * tr - sq) % MOD
            return s, k

    else:

        def seg_sums(L: int, start: int, direction: int) -> tuple[int, int]:
            tr = L * (L - 1) // 2
            sq = (L - 1) * L * (2 * L - 1) // 6
            if direction == 1:
                s = start * L + tr
                k = start * tr + sq
            else:
                s = start * L - tr
                k = start * tr - sq
            return s, k

    def new_node(L: int, start: int, direction: int) -> int:
        idx = len(lch)
        lch.append(0)
        rch.append(0)
        prio.append(rng32())
        seg_len.append(L)
        seg_start.append(start)
        seg_dir.append(direction)
        rev.append(0)
        tot_len.append(L)

        s, k = seg_sums(L, start, direction)
        seg_sum.append(s)
        seg_k.append(k)
        sum_val.append(s)
        sum_pos.append(k)
        return idx

    def apply_rev(node: int) -> None:
        """Reverse the entire subtree rooted at node (lazy flag + O(1) aggregate updates)."""
        if node == 0:
            return

        # swap children
        l = lch[node]
        r = rch[node]
        lch[node], rch[node] = r, l
        rev[node] ^= 1

        # reverse the node's own segment (flip direction, move start to the old last value)
        L = seg_len[node]
        d = seg_dir[node]
        if L > 1:
            seg_start[node] = seg_start[node] + (d * (L - 1))
        seg_dir[node] = -d

        # update segment-internal k-sum
        if use_mod:
            seg_k[node] = (((L - 1) % MOD) * seg_sum[node] - seg_k[node]) % MOD
        else:
            seg_k[node] = (L - 1) * seg_sum[node] - seg_k[node]

        # update subtree positional sum: reversing positions turns Σ p*v into (L-1)*Σv - Σ p*v
        if use_mod:
            sum_pos[node] = (
                ((tot_len[node] - 1) % MOD) * sum_val[node] - sum_pos[node]
            ) % MOD
        else:
            sum_pos[node] = (tot_len[node] - 1) * sum_val[node] - sum_pos[node]

    def push(node: int) -> None:
        """Push lazy reversal into children."""
        if node and rev[node]:
            l = lch[node]
            r = rch[node]
            if l:
                apply_rev(l)
            if r:
                apply_rev(r)
            rev[node] = 0

    def upd(node: int) -> None:
        """Recompute aggregates for node from its children and segment."""
        if node == 0:
            return
        l = lch[node]
        r = rch[node]

        lenL = tot_len[l] if l else 0
        lenR = tot_len[r] if r else 0
        tot_len[node] = lenL + seg_len[node] + lenR

        sL = sum_val[l] if l else 0
        sR = sum_val[r] if r else 0
        pL = sum_pos[l] if l else 0
        pR = sum_pos[r] if r else 0

        segS = seg_sum[node]
        segK = seg_k[node]

        if use_mod:
            lenL_m = lenL % MOD
            off_m = (lenL + seg_len[node]) % MOD
            sum_val[node] = (sL + segS + sR) % MOD
            sum_pos[node] = (
                pL + (lenL_m * segS + segK) % MOD + pR + (off_m * sR) % MOD
            ) % MOD
        else:
            sum_val[node] = sL + segS + sR
            sum_pos[node] = pL + lenL * segS + segK + pR + (lenL + seg_len[node]) * sR

    def merge(a: int, b: int) -> int:
        """Merge treaps a then b (all positions in a come before all positions in b)."""
        if a == 0:
            return b
        if b == 0:
            return a

        stack: list[tuple[int, int]] = []
        while a and b:
            if prio[a] < prio[b]:
                push(a)
                stack.append((a, 1))  # went right
                a = rch[a]
            else:
                push(b)
                stack.append((b, 0))  # went left
                b = lch[b]

        root = a or b
        while stack:
            node, went_right = stack.pop()
            if went_right:
                rch[node] = root
            else:
                lch[node] = root
            upd(node)
            root = node
        return root

    def split(root: int, k: int) -> tuple[int, int]:
        """
        Split treap into (left, right) where left has first k elements.
        """
        if root == 0:
            return 0, 0

        lstack: list[int] = []
        rstack: list[int] = []

        while root:
            push(root)
            l = lch[root]
            lsize = tot_len[l] if l else 0
            Lseg = seg_len[root]

            if k < lsize:
                rstack.append(root)
                root = l
            elif k > lsize + Lseg:
                k -= lsize + Lseg
                lstack.append(root)
                root = rch[root]
            else:
                # boundary is inside this node (possibly within its segment)
                if k == lsize:
                    left_res = l
                    lch[root] = 0
                    upd(root)
                    right_res = root
                elif k == lsize + Lseg:
                    right_res = rch[root]
                    rch[root] = 0
                    upd(root)
                    left_res = root
                else:
                    # split within the node's segment
                    x = k - lsize  # left part length inside this segment

                    old_right = rch[root]
                    old_len = Lseg
                    old_start = seg_start[root]
                    old_dir = seg_dir[root]

                    # left part stays in this node
                    seg_len[root] = x
                    s, kk = seg_sums(x, old_start, old_dir)
                    seg_sum[root] = s
                    seg_k[root] = kk

                    # right part becomes a new node, then merged in front of the old right subtree
                    start2 = old_start + old_dir * x
                    len2 = old_len - x
                    node2 = new_node(len2, start2, old_dir)
                    right_res = merge(node2, old_right)

                    rch[root] = 0
                    upd(root)
                    left_res = root
                break
        else:
            left_res = right_res = 0

        # rebuild from stacks
        while lstack:
            node = lstack.pop()
            rch[node] = left_res
            upd(node)
            left_res = node

        while rstack:
            node = rstack.pop()
            lch[node] = right_res
            upd(node)
            right_res = node

        return left_res, right_res

    def reverse_range(root: int, l: int, r: int) -> int:
        """Reverse positions l..r inclusive."""
        a, bc = split(root, l)
        b, c = split(bc, r - l + 1)
        if b:
            apply_rev(b)
        return merge(merge(a, b), c)

    # Initial array A[i] = i is a single increasing segment.
    root = new_node(N, 0, 1)

    # Fibonacci generation: (a,b) = (F_{2j-1} mod N, F_{2j} mod N) at each step j
    a = 1 % N
    b = 1 % N
    for _ in range(K):
        if a < b:
            l = a
            r = b
        else:
            l = b
            r = a
        root = reverse_range(root, l, r)

        # advance by two Fibonacci steps mod N, using conditional subtraction instead of %
        s = a + b
        if s >= N:
            s -= N
        a, b = b, s

        s = a + b
        if s >= N:
            s -= N
        a, b = b, s

    return int(sum_pos[root] % MOD) if use_mod else int(sum_pos[root])


def main() -> None:
    # Test values from the problem statement
    assert compute_R(5, 4) == 27
    assert compute_R(10**2, 10**2) == 246597
    assert compute_R(10**4, 10**4) == 249275481640

    # Required answer
    MOD = 10**9
    ans = compute_R(10**18, 10**6, mod=MOD)
    print(ans)


if __name__ == "__main__":
    main()
