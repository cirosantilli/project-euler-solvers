from typing import Final


def last_ten_digits() -> int:
    MOD: Final[int] = 10**10
    # Compute (28433 * 2^7830457 + 1) mod 10^10
    return (28433 * pow(2, 7830457, MOD) + 1) % MOD


def main() -> None:
    ans = last_ten_digits()
    # Project Euler #97 known result
    assert ans == 8739992577
    print(ans)


if __name__ == "__main__":
    main()
