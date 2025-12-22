from typing import List


def build_sum_sq_table(limit: int) -> List[int]:
    sq = [d * d for d in range(10)]
    t = [0] * (limit + 1)
    for i in range(1, limit + 1):
        t[i] = t[i // 10] + sq[i % 10]
    return t


def build_terminal_for_sums(sum_sq: List[int], max_sum: int = 567) -> List[int]:
    # terminal[x] in {0,1,89}, for x in [0..max_sum]
    terminal = [0] * (max_sum + 1)
    terminal[1] = 1
    terminal[89] = 89

    for start in range(1, max_sum + 1):
        if terminal[start]:
            continue
        path: List[int] = []
        x = start
        while x <= max_sum and terminal[x] == 0:
            path.append(x)
            x = sum_sq[x]  # x stays small; sum_sq table covers it
        end = terminal[x] if x <= max_sum else 0

        # For safety, if x jumped out of [0..max_sum], continue iterating until 1/89.
        if end == 0:
            y = x
            while y not in (1, 89):
                y = sum_sq[y]
            end = y

        for v in path:
            terminal[v] = end

    return terminal


def count_ending_at_89(limit_exclusive: int = 10_000_000) -> int:
    # For numbers < 10,000,000 we have at most 7 digits, so max digit-square-sum is 7*81=567.
    MAX_SUM = 7 * 81

    # Precompute digit-square-sum for 0..9999; use block-splitting into (high, low) 4-digit blocks.
    sum_sq = build_sum_sq_table(9999)

    terminal = build_terminal_for_sums(sum_sq, MAX_SUM)

    # Small sanity checks from statement examples
    def end_from_number(n: int) -> int:
        x = n
        while x not in (1, 89):
            x = sum_sq[x]
        return x

    assert end_from_number(44) == 1
    assert end_from_number(85) == 89

    # Count numbers 1..9,999,999 by iterating over 3-digit high block and 4-digit low block.
    # n = high*10000 + low, where high in [0..999], low in [0..9999]
    count = 0
    t = sum_sq
    term = terminal

    for high in range(0, 1000):
        hs = t[high]
        start_low = 1 if high == 0 else 0  # exclude n=0
        for low in range(start_low, 10000):
            if term[hs + t[low]] == 89:
                count += 1

    # limit_exclusive is fixed to 10,000,000 for this problem; the loop above matches it.
    assert limit_exclusive == 10_000_000
    return count


def main() -> None:
    result = count_ending_at_89(10_000_000)
    print(result)


if __name__ == "__main__":
    main()
