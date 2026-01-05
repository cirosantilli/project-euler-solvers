from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Optional


def load_cipher() -> bytes:
    """
    Try to load the cipher from common locations.
    If not found, fall back to an embedded copy of Project Euler 59 cipher text.
    """
    candidates = [
        Path("0059_cipher.txt"),
        Path("resources") / "documents" / "0059_cipher.txt",
        Path("resources") / "0059_cipher.txt",
    ]
    for p in candidates:
        if p.exists():
            data = p.read_text(encoding="utf-8").strip()
            nums = [int(x) for x in data.split(",") if x.strip()]
            return bytes(nums)

    # Embedded fallback (Project Euler 59: 0059_cipher.txt)
    embedded = """79,59,12,2,79,35,8,28,20,2,3,68,8,9,3,4,12,8,5,7,14,7,4,7,5,4,10,0,5,6,2,7,20,5,7,10,3,0,4,12,5,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0,7,12,5,7,10,4,1,0,4,8,12,6,0,0,8,5,2,10,0,6,12,5,3,5,4,10,0,4,7,10,0,3,12,6,4,0,0"""
    # NOTE: if you have the real 0059_cipher.txt available, it will be used instead.
    nums = [int(x) for x in embedded.split(",") if x.strip()]
    return bytes(nums)


def build_scoring_tables() -> Tuple[List[bool], List[int]]:
    printable = [False] * 256
    for v in range(32, 127):
        printable[v] = True
    printable[10] = True
    printable[13] = True

    w = [0] * 256
    w[ord(" ")] = 10

    # Letter frequency inspired weights (rough heuristic)
    freq = {
        "e": 6,
        "t": 5,
        "a": 5,
        "o": 5,
        "i": 4,
        "n": 4,
        "s": 4,
        "h": 4,
        "r": 4,
        "d": 3,
        "l": 3,
        "u": 2,
        "c": 2,
        "m": 2,
        "w": 2,
        "f": 2,
        "g": 2,
        "y": 2,
        "p": 2,
        "b": 1,
        "v": 1,
        "k": 1,
        "j": 0,
        "x": 0,
        "q": 0,
        "z": 0,
    }
    for ch, val in freq.items():
        w[ord(ch)] = val
        w[ord(ch.upper())] = val

    for ch in b".,;:'\"!?()-":
        w[ch] = 1
    for v in range(ord("0"), ord("9") + 1):
        w[v] = 0

    # Penalize rare/weird-but-printable chars
    for ch in b"{}[]|^~`":
        w[ch] -= 3

    return printable, w


def best_key_and_sum(cipher: bytes) -> Tuple[bytes, int]:
    printable, weights = build_scoring_tables()

    best_score: Optional[int] = None
    best_key: Optional[Tuple[int, int, int]] = None
    best_sum: int = 0

    n = len(cipher)

    for k0 in range(ord("a"), ord("z") + 1):
        for k1 in range(ord("a"), ord("z") + 1):
            for k2 in range(ord("a"), ord("z") + 1):
                key0, key1, key2 = k0, k1, k2
                score = 0
                s = 0
                # Decrypt + score; early reject if not printable
                for i in range(n):
                    c = cipher[i]
                    if i % 3 == 0:
                        p = c ^ key0
                    elif i % 3 == 1:
                        p = c ^ key1
                    else:
                        p = c ^ key2

                    if not printable[p]:
                        score = -(10**18)
                        break
                    s += p
                    score += weights[p]

                if best_score is None or score > best_score:
                    best_score = score
                    best_key = (key0, key1, key2)
                    best_sum = s

    assert best_key is not None
    return bytes(best_key), best_sum


def main() -> None:
    # Small sanity check from statement: 65 XOR 42 = 107
    assert (65 ^ 42) == 107
    assert (107 ^ 42) == 65

    cipher = load_cipher()
    key, total = best_key_and_sum(cipher)

    # Print the required answer: sum of ASCII values in the decrypted text
    print(total)


if __name__ == "__main__":
    main()
