from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Tuple


Square = int
Doubles = int
State = int  # encoded as pos*3 + doubles_count
SentToJail = bool


CC_SQUARES = {2, 17, 33}
CH_SQUARES = {7, 22, 36}
G2J = 30
JAIL = 10

RAILWAYS = [5, 15, 25, 35]
UTILITIES = [12, 28]


def next_railway(pos: int) -> int:
    for r in RAILWAYS:
        if r > pos:
            return r
    return RAILWAYS[0]


def next_utility(pos: int) -> int:
    for u in UTILITIES:
        if u > pos:
            return u
    return UTILITIES[0]


def dice_outcomes(sides: int) -> List[Tuple[int, bool, float]]:
    p = 1.0 / (sides * sides)
    out: List[Tuple[int, bool, float]] = []
    for d1 in range(1, sides + 1):
        for d2 in range(1, sides + 1):
            out.append((d1 + d2, d1 == d2, p))
    return out


@lru_cache(None)
def resolve_landing(square: Square) -> Dict[Tuple[Square, SentToJail], float]:
    """
    Distribution over final squares after applying immediate effects of landing on `square`.
    For JAIL we distinguish:
      - (10, True)  : sent to jail by a rule/card (doubles count resets)
      - (10, False) : merely landed on square 10 normally
    """
    if square == G2J:
        return {(JAIL, True): 1.0}

    if square in CC_SQUARES:
        dist: Dict[Tuple[Square, SentToJail], float] = {}
        # 14/16: no movement; stay on CC (do not draw again)
        dist[(square, False)] = dist.get((square, False), 0.0) + 14.0 / 16.0
        # 1/16: advance to GO
        dist[(0, False)] = dist.get((0, False), 0.0) + 1.0 / 16.0
        # 1/16: go to JAIL (forced)
        dist[(JAIL, True)] = dist.get((JAIL, True), 0.0) + 1.0 / 16.0
        return dist

    if square in CH_SQUARES:
        dist: Dict[Tuple[Square, SentToJail], float] = {}
        # 6/16: no movement; stay on CH (do not draw again)
        dist[(square, False)] = dist.get((square, False), 0.0) + 6.0 / 16.0

        def add_move(dest: int, prob: float) -> None:
            # After moving, we "land" on dest and must apply its effect if any.
            if dest in CC_SQUARES or dest in CH_SQUARES or dest == G2J:
                sub = resolve_landing(dest)
                for (sq, sent), p2 in sub.items():
                    dist[(sq, sent)] = dist.get((sq, sent), 0.0) + prob * p2
            else:
                dist[(dest, False)] = dist.get((dest, False), 0.0) + prob

        # 10 movement cards, each 1/16
        p = 1.0 / 16.0
        add_move(0, p)  # GO
        dist[(JAIL, True)] = dist.get((JAIL, True), 0.0) + p  # JAIL (forced)
        add_move(11, p)  # C1
        add_move(24, p)  # E3
        add_move(39, p)  # H2
        add_move(5, p)  # R1
        add_move(next_railway(square), p)  # next R
        add_move(next_railway(square), p)  # next R
        add_move(next_utility(square), p)  # next U
        add_move((square - 3) % 40, p)  # back 3 squares

        return dist

    # Normal square (including JAIL as a normal landing)
    return {(square, False): 1.0}


def build_transition(sides: int) -> List[List[Tuple[State, float]]]:
    outcomes = dice_outcomes(sides)
    n_states = 40 * 3
    P: List[List[Tuple[State, float]]] = []

    for pos in range(40):
        for doubles_count in range(3):
            acc: Dict[State, float] = {}

            for move, is_double, pr in outcomes:
                if is_double and doubles_count == 2:
                    # third consecutive double => go to jail, no movement
                    to_state = JAIL * 3 + 0
                    acc[to_state] = acc.get(to_state, 0.0) + pr
                    continue

                new_dc = doubles_count + 1 if is_double else 0
                nxt = (pos + move) % 40

                for (final_sq, sent), pr2 in resolve_landing(nxt).items():
                    if sent:
                        to_state = JAIL * 3 + 0
                    else:
                        to_state = final_sq * 3 + new_dc
                    acc[to_state] = acc.get(to_state, 0.0) + pr * pr2

            # Convert to sparse row
            row = list(acc.items())
            P.append(row)

    return P


def stationary_distribution(P: List[List[Tuple[State, float]]]) -> List[float]:
    n = len(P)
    v = [1.0 / n] * n
    for it in range(1, 5000):
        v2 = [0.0] * n
        for i, row in enumerate(P):
            vi = v[i]
            if vi == 0.0:
                continue
            for j, p in row:
                v2[j] += vi * p

        diff = max(abs(v2[k] - v[k]) for k in range(n))
        v = v2
        if it > 50 and diff < 1e-15:
            break

    # normalize (guard against tiny drift)
    s = sum(v)
    if s != 0.0:
        v = [x / s for x in v]
    return v


def modal_string(sides: int) -> str:
    P = build_transition(sides)
    v = stationary_distribution(P)

    sq_prob = [0.0] * 40
    for pos in range(40):
        sq_prob[pos] = v[pos * 3] + v[pos * 3 + 1] + v[pos * 3 + 2]

    top3 = sorted(range(40), key=lambda i: (-sq_prob[i], i))[:3]
    return "".join(f"{i:02d}" for i in top3)


def main() -> None:
    # Check the example from the statement (standard dice)
    assert modal_string(6) == "102400"

    ans = modal_string(4)
    print(ans)


if __name__ == "__main__":
    main()
