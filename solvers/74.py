from __future__ import annotations

from array import array
from typing import List


def main() -> None:
    # Upper bound:
    # For any number with d digits, sum of digit factorials <= d * 9!
    # Starting numbers < 1_000_000 have at most 6 digits, so first step <= 6*9! (7 digits).
    # Thereafter values are at most 7*9! = 2_540_160.
    FACT9 = 362880
    LIMIT = 7 * FACT9  # 2_540_160

    fact: List[int] = [1] * 10
    for i in range(2, 10):
        fact[i] = fact[i - 1] * i

    # nxt[n] = sum of factorials of digits of n
    # Recurrence: nxt[n] = nxt[n//10] + fact[n%10], with nxt[0] = 0 (suitable for n>=1).
    nxt = array("I", [0]) * (LIMIT + 1)
    f = fact
    for i in range(1, LIMIT + 1):
        nxt[i] = nxt[i // 10] + f[i % 10]

    # memoized chain lengths (number of non-repeating terms)
    lens = array("h", [-1]) * (LIMIT + 1)

    # For detecting loops within the current chain without per-chain dict allocations:
    seen_stamp = array("I", [0]) * (LIMIT + 1)
    seen_pos = array("B", [0]) * (LIMIT + 1)
    stamp = 0

    def chain_len(start: int) -> int:
        nonlocal stamp
        if start <= 0:
            raise ValueError("start must be positive")
        if lens[start] != -1:
            return lens[start]

        stamp += 1
        seq: List[int] = []
        cur = start

        while True:
            lc = lens[cur]
            if lc != -1:
                # We reached a node with known chain length.
                known = lc
                for v in reversed(seq):
                    known += 1
                    lens[v] = known
                return lens[start]

            if seen_stamp[cur] == stamp:
                # Found a loop within seq.
                loop_start = seen_pos[cur]
                loop_len = len(seq) - loop_start

                # Nodes in the loop have chain length = loop length.
                for i in range(loop_start, len(seq)):
                    lens[seq[i]] = loop_len

                # Nodes before the loop: chain length is "remaining unique terms".
                # Since seq contains only unique terms, for index i < loop_start:
                # length = len(seq) - i
                total = len(seq)
                for i in range(loop_start - 1, -1, -1):
                    lens[seq[i]] = total - i

                return lens[start]

            seen_stamp[cur] = stamp
            seen_pos[cur] = len(seq)
            seq.append(cur)

            cur = nxt[cur]
            # Safety (should always hold by construction of LIMIT)
            # If it ever fails, increase LIMIT and/or compute nxt on the fly.
            if cur > LIMIT:
                raise RuntimeError("Exceeded LIMIT; bound was insufficient.")

    # Asserts from the problem statement examples
    assert chain_len(69) == 5
    assert chain_len(78) == 4
    assert chain_len(540) == 2
    assert chain_len(169) == 3

    count = 0
    for n in range(1, 1_000_000):
        ln = lens[n]
        if ln == -1:
            ln = chain_len(n)
        if ln == 60:
            count += 1

    print(count)


if __name__ == "__main__":
    main()
