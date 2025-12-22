from typing import List


NUMBER_STR = (
    "73167176531330624919225119674426574742355349194934"
    "96983520312774506326239578318016984801869478851843"
    "85861560789112949495459501737958331952853208805511"
    "12540698747158523863050715693290963295227443043557"
    "66896648950445244523161731856403098711121722383113"
    "62229893423380308135336276614282806444486645238749"
    "30358907296290491560440772390713810515859307960866"
    "70172427121883998797908792274921901699720888093776"
    "65727333001053367881220235421809751254540594752243"
    "52584907711670556013604839586446706324415722155397"
    "53697817977846174064955149290862569321978468622482"
    "83972241375657056057490261407972968652414535100474"
    "82166370484403199890008895243450658541227588666881"
    "16427171479924442928230863465674813919123162824586"
    "17866458359124566529476545682848912883142607690042"
    "24219022671055626321111109370544217506941658960408"
    "07198403850962455444362981230987879927244284909188"
    "84580156166097919133875499200524063689912560717606"
    "05886116467109405077541002256983155200055935729725"
    "71636269561882670428252483600823257530420752963450"
)


def max_adjacent_product(num: str, k: int) -> int:
    digits: List[int] = [ord(c) - 48 for c in num.strip()]
    n = len(digits)

    best = 0
    i = 0
    while i < n:
        # Skip zeros (any window containing a 0 has product 0)
        while i < n and digits[i] == 0:
            i += 1
        if i >= n:
            break

        # Process maximal zero-free segment [i, j)
        j = i
        while j < n and digits[j] != 0:
            j += 1

        seg_len = j - i
        if seg_len >= k:
            prod = 1
            for t in range(i, i + k):
                prod *= digits[t]
            if prod > best:
                best = prod

            for t in range(i + k, j):
                prod = (prod // digits[t - k]) * digits[t]
                if prod > best:
                    best = prod

        i = j  # continue after the segment (next loop will skip zeros if any)

    return best


def main() -> None:
    # Test case from the statement (4 adjacent digits)
    assert max_adjacent_product(NUMBER_STR, 4) == 5832

    ans = max_adjacent_product(NUMBER_STR, 13)
    print(ans)


if __name__ == "__main__":
    main()
