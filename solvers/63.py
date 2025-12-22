from typing import Final


def count_n_digit_nth_powers() -> int:
    """
    Counts pairs (a, n) with a^n having exactly n decimal digits,
    where a is a positive integer.
    Observation: only a in [1..9] can work (since 10^n has n+1 digits).
    We iterate n until even 9^n has fewer than n digits (then no larger n can work).
    """
    total = 0
    for n in range(1, 200):  # 200 is far beyond what is needed
        if len(str(pow(9, n))) < n:
            break
        for a in range(1, 10):
            if len(str(pow(a, n))) == n:
                total += 1
    return total


def main() -> None:
    # Examples from the statement
    assert len(str(pow(7, 5))) == 5
    assert len(str(pow(8, 9))) == 9

    ans: Final[int] = count_n_digit_nth_powers()
    print(ans)


if __name__ == "__main__":
    main()
