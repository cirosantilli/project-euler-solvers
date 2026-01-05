from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Sequence, Tuple


VALUE_MAP = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


def parse_card(token: str) -> Tuple[int, str]:
    # Euler 54 format: e.g. "5H", "TD", "AC"
    v = VALUE_MAP[token[0]]
    s = token[1]
    return v, s


def hand_rank(cards: Sequence[str]) -> Tuple:
    """
    Return a tuple comparable lexicographically; higher is better.

    Category order (low->high):
      0 High card
      1 One pair
      2 Two pairs
      3 Three of a kind
      4 Straight
      5 Flush
      6 Full house
      7 Four of a kind
      8 Straight flush (includes royal flush)
    """
    values: List[int] = []
    suits: List[str] = []
    for c in cards:
        v, s = parse_card(c)
        values.append(v)
        suits.append(s)

    values.sort(reverse=True)
    is_flush = len(set(suits)) == 1

    uniq = sorted(set(values))
    is_straight = False
    straight_high = 0
    if len(uniq) == 5:
        if uniq[-1] - uniq[0] == 4:
            is_straight = True
            straight_high = uniq[-1]
        # Wheel straight: A-2-3-4-5
        elif uniq == [2, 3, 4, 5, 14]:
            is_straight = True
            straight_high = 5

    if is_straight and is_flush:
        return (8, straight_high)

    cnt = Counter(values)
    # sort primarily by frequency desc, then value desc
    groups = sorted(((c, v) for v, c in cnt.items()), reverse=True)

    if groups[0][0] == 4:
        four_val = groups[0][1]
        kicker = max(v for v in values if v != four_val)
        return (7, four_val, kicker)

    if groups[0][0] == 3 and groups[1][0] == 2:
        trip_val = groups[0][1]
        pair_val = groups[1][1]
        return (6, trip_val, pair_val)

    if is_flush:
        return (5, tuple(values))

    if is_straight:
        return (4, straight_high)

    if groups[0][0] == 3:
        trip_val = groups[0][1]
        kickers = sorted((v for v in values if v != trip_val), reverse=True)
        return (3, trip_val, tuple(kickers))

    if groups[0][0] == 2 and groups[1][0] == 2:
        pair_high = max(groups[0][1], groups[1][1])
        pair_low = min(groups[0][1], groups[1][1])
        kicker = max(v for v in values if v != pair_high and v != pair_low)
        return (2, pair_high, pair_low, kicker)

    if groups[0][0] == 2:
        pair_val = groups[0][1]
        kickers = sorted((v for v in values if v != pair_val), reverse=True)
        return (1, pair_val, tuple(kickers))

    return (0, tuple(values))


def player1_wins(line: str) -> bool:
    parts = line.strip().split()
    if not parts:
        return False
    h1 = parts[:5]
    h2 = parts[5:]
    return hand_rank(h1) > hand_rank(h2)


def _run_sample_asserts() -> None:
    # Samples from the statement:
    # 1) Player 2
    assert player1_wins("5H 5C 6S 7S KD 2C 3S 8S 8D TD") is False
    # 2) Player 1
    assert player1_wins("5D 8C 9S JS AC 2C 5C 7D 8S QH") is True
    # 3) Player 2
    assert player1_wins("2D 9C AS AH AC 3D 6D 7D TD QD") is False
    # 4) Player 1
    assert player1_wins("4D 6S 9H QH QC 3D 6D 7H QD QS") is True
    # 5) Player 1
    assert player1_wins("2H 2D 4C 4D 4S 3C 3D 3S 9S 9D") is True

    # Extra sanity: wheel straight beats high card
    assert hand_rank(["AS", "2D", "3H", "4C", "5S"]) > hand_rank(
        ["KS", "QD", "9H", "4C", "3S"]
    )


def _read_input_lines() -> List[str]:
    with open("0054_poker.txt", "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def main() -> None:
    _run_sample_asserts()
    lines = _read_input_lines()
    wins = sum(1 for ln in lines if player1_wins(ln))
    print(wins)


if __name__ == "__main__":
    main()
