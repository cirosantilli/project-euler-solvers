from typing import Tuple


def last_k_digits_self_powers(n: int, k: int = 10) -> str:
    mod = 10**k
    s = 0
    for i in range(1, n + 1):
        s = (s + pow(i, i, mod)) % mod
    return str(s).zfill(k)


def exact_self_powers_sum(n: int) -> int:
    return sum(pow(i, i) for i in range(1, n + 1))


def main() -> None:
    # Test case from the problem statement:
    # 1^1 + 2^2 + ... + 10^10 = 10405071317
    assert exact_self_powers_sum(10) == 10405071317
    assert last_k_digits_self_powers(10, 10) == "0405071317"

    # Required result:
    ans = last_k_digits_self_powers(1000, 10)
    print(ans)


if __name__ == "__main__":
    main()
