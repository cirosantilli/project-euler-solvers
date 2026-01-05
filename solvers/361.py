from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

MOD = 10**9


@lru_cache(maxsize=None)
def count_start1(length: int) -> int:
    """Number of Thue-Morse factors of given length starting with 1."""
    if length == 1:
        return 1
    if length == 2:
        return 2
    if length == 3:
        return 3
    if length % 2 == 0:
        half = length // 2
        return count_start1(half) + count_start1(half + 1)
    half = length // 2
    return 2 * count_start1(half + 1)


@lru_cache(maxsize=None)
def count_start1_prefix_sum(length: int) -> int:
    """Sum of count_start1(1..length)."""
    if length == 0:
        return 0
    if length == 1:
        return 1
    if length == 2:
        return 3
    if length == 3:
        return 6
    if length % 2 == 0:
        half = length // 2
        return 3 * count_start1_prefix_sum(half) + count_start1_prefix_sum(half + 1) - 4
    half = length // 2
    return count_start1_prefix_sum(2 * half) + 2 * count_start1(half + 1)


def find_length_by_index(index: int) -> int:
    """Smallest length L such that sum_{l<=L} count_start1(l) >= index."""
    lo = 1
    hi = 1
    while count_start1_prefix_sum(hi) < index:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if count_start1_prefix_sum(mid) >= index:
            hi = mid
        else:
            lo = mid + 1
    return lo


class Node:
    __slots__ = ("kind", "child", "length", "value")

    def __init__(
        self, kind: str, child: Node | None, length: int, value: str | None = None
    ) -> None:
        self.kind = kind
        self.child = child
        self.length = length
        self.value = value


EMPTY = Node("lit", None, 0, "")


def node_lit(s: str) -> Node:
    return Node("lit", None, len(s), s)


def node_comp(child: Node) -> Node:
    if child.length == 0:
        return child
    return Node("comp", child, child.length)


def node_even(child: Node, length: int) -> Node:
    return Node("even", child, length)


def node_odd(child: Node, length: int) -> Node:
    return Node("odd", child, length)


first_cache: Dict[Node, int] = {}
last_cache: Dict[Node, int] = {}


def first_bit(node: Node) -> int:
    if node in first_cache:
        return first_cache[node]
    if node.length == 0:
        raise ValueError("Empty node has no first bit")
    if node.kind == "lit":
        val = int(node.value[0])  # type: ignore[index]
    elif node.kind == "comp":
        val = 1 - first_bit(node.child)  # type: ignore[arg-type]
    elif node.kind == "even":
        val = first_bit(node.child)  # type: ignore[arg-type]
    else:  # "odd"
        val = 1 - first_bit(node.child)  # type: ignore[arg-type]
    first_cache[node] = val
    return val


def last_bit(node: Node) -> int:
    if node in last_cache:
        return last_cache[node]
    if node.length == 0:
        raise ValueError("Empty node has no last bit")
    if node.kind == "lit":
        val = int(node.value[-1])  # type: ignore[index]
    elif node.kind == "comp":
        val = 1 - last_bit(node.child)  # type: ignore[arg-type]
    elif node.kind == "even":
        val = 1 - last_bit(node.child) if node.length % 2 == 0 else last_bit(node.child)  # type: ignore[arg-type]
    else:  # "odd"
        val = last_bit(node.child) if node.length % 2 == 0 else 1 - last_bit(node.child)  # type: ignore[arg-type]
    last_cache[node] = val
    return val


_drop_first_cache: Dict[Node, Node] = {}
_drop_last_cache: Dict[Node, Node] = {}


def drop_first(node: Node) -> Node:
    if node.length == 0:
        return node
    if node.length == 1:
        return EMPTY
    if node in _drop_first_cache:
        return _drop_first_cache[node]
    if node.kind == "lit":
        res = node_lit(node.value[1:])  # type: ignore[index]
    elif node.kind == "comp":
        res = node_comp(drop_first(node.child))  # type: ignore[arg-type]
    elif node.kind == "even":
        res = node_odd(node.child, node.length - 1)  # type: ignore[arg-type]
    else:  # "odd"
        res = node_even(drop_first(node.child), node.length - 1)  # type: ignore[arg-type]
    _drop_first_cache[node] = res
    return res


def drop_last(node: Node) -> Node:
    if node.length == 0:
        return node
    if node.length == 1:
        return EMPTY
    if node in _drop_last_cache:
        return _drop_last_cache[node]
    if node.kind == "lit":
        res = node_lit(node.value[:-1])  # type: ignore[index]
    elif node.kind == "comp":
        res = node_comp(drop_last(node.child))  # type: ignore[arg-type]
    elif node.kind == "even":
        if node.length % 2 == 0:
            res = node_even(node.child, node.length - 1)  # type: ignore[arg-type]
        else:
            res = node_even(drop_last(node.child), node.length - 1)  # type: ignore[arg-type]
    else:  # "odd"
        if node.length % 2 == 0:
            res = node_odd(drop_last(node.child), node.length - 1)  # type: ignore[arg-type]
        else:
            res = node_odd(node.child, node.length - 1)  # type: ignore[arg-type]
    _drop_last_cache[node] = res
    return res


def max_depth(length: int) -> int:
    depth = 0
    while length > 3:
        length = length // 2 + 1
        depth += 1
    return depth


def build_eval_context() -> int:
    max_len = 0
    for k in range(1, 19):
        max_len = max(max_len, find_length_by_index(10**k))
    return max_depth(max_len) + 2


KMAX = build_eval_context()
X_POWERS = [pow(2, 2**k, MOD) for k in range(KMAX + 2)]


_pow_cache: Dict[tuple[int, int], int] = {}


def pow_x(k: int, exp: int) -> int:
    key = (k, exp)
    if key in _pow_cache:
        return _pow_cache[key]
    val = pow(X_POWERS[k], exp, MOD)
    _pow_cache[key] = val
    return val


_geom_cache: Dict[tuple[int, int], int] = {}


def geom_sum(base: int, count: int) -> int:
    key = (base, count)
    if key in _geom_cache:
        return _geom_cache[key]
    if count == 0:
        return 0
    if count == 1:
        return 1
    if count % 2 == 0:
        half = geom_sum(base, count // 2)
        res = (half + pow(base, count // 2, MOD) * half) % MOD
    else:
        res = (geom_sum(base, count - 1) + pow(base, count - 1, MOD)) % MOD
    _geom_cache[key] = res
    return res


eval_cache: Dict[Node, List[int]] = {}
mu_cache: Dict[Node, List[int]] = {}


def evals(node: Node) -> List[int]:
    if node in eval_cache:
        return eval_cache[node]
    if node.length == 0:
        arr = [0] * (KMAX + 2)
        eval_cache[node] = arr
        return arr
    if node.kind == "lit":
        arr = []
        for k in range(KMAX + 2):
            val = 0
            for ch in node.value:  # type: ignore[union-attr]
                val = (val * X_POWERS[k] + (ch == "1")) % MOD
            arr.append(val)
    elif node.kind == "comp":
        child = evals(node.child)  # type: ignore[arg-type]
        arr = []
        for k in range(KMAX + 2):
            total = geom_sum(X_POWERS[k], node.length)
            arr.append((total - child[k]) % MOD)
    elif node.kind == "even":
        length = node.length
        if length % 2 == 0:
            len_u = length // 2
            child = evals(node.child)  # type: ignore[arg-type]
            arr = []
            for k in range(KMAX + 2):
                if k + 1 >= KMAX + 2:
                    val = 0
                else:
                    val = (
                        (X_POWERS[k] - 1) * child[k + 1]
                        + geom_sum((X_POWERS[k] * X_POWERS[k]) % MOD, len_u)
                    ) % MOD
                arr.append(val)
        else:
            u_prefix = drop_last(node.child)  # type: ignore[arg-type]
            u_last = last_bit(node.child)  # type: ignore[arg-type]
            mu_pref = mu_evals(u_prefix)
            arr = [(mu_pref[k] * X_POWERS[k] + u_last) % MOD for k in range(KMAX + 2)]
    else:  # "odd"
        length = node.length
        half = length // 2
        u_first = first_bit(node.child)  # type: ignore[arg-type]
        u_last = last_bit(node.child)  # type: ignore[arg-type]
        if length % 2 == 1:
            u_tail = drop_first(node.child)  # type: ignore[arg-type]
            mu_tail = mu_evals(u_tail)
            arr = [
                ((1 - u_first) * pow_x(k, 2 * half) + mu_tail[k]) % MOD
                for k in range(KMAX + 2)
            ]
        else:
            u_mid = drop_last(drop_first(node.child))  # type: ignore[arg-type]
            mu_mid = mu_evals(u_mid)
            arr = [
                (
                    (1 - u_first) * pow_x(k, 2 * half - 1)
                    + mu_mid[k] * X_POWERS[k]
                    + u_last
                )
                % MOD
                for k in range(KMAX + 2)
            ]
    eval_cache[node] = arr
    return arr


def mu_evals(node: Node) -> List[int]:
    if node in mu_cache:
        return mu_cache[node]
    base = evals(node)
    arr = []
    for k in range(KMAX + 2):
        if k + 1 >= KMAX + 2:
            val = 0
        else:
            val = (
                (X_POWERS[k] - 1) * base[k + 1]
                + geom_sum((X_POWERS[k] * X_POWERS[k]) % MOD, node.length)
            ) % MOD
        arr.append(val)
    mu_cache[node] = arr
    return arr


PRE_WORDS = {
    1: ["1"],
    2: ["10", "11"],
    3: ["100", "101", "110"],
}


def kth_word(length: int, rank: int, start_bit: int) -> Node:
    if start_bit == 0:
        total = count_start1(length)
        return node_comp(kth_word(length, total - 1 - rank, 1))
    if length <= 3:
        return node_lit(PRE_WORDS[length][rank])
    half_even = (length + 1) // 2
    count_even = count_start1(half_even)
    if rank < count_even:
        child = kth_word(half_even, rank, 1)
        return node_even(child, length)
    half_odd = length // 2 + 1
    child = kth_word(half_odd, rank - count_even, 0)
    return node_odd(child, length)


def node_to_string(node: Node) -> str:
    if node.length == 0:
        return ""
    if node.kind == "lit":
        return node.value  # type: ignore[return-value]
    if node.kind == "comp":
        s = node_to_string(node.child)  # type: ignore[arg-type]
        return "".join("1" if c == "0" else "0" for c in s)
    if node.kind == "even":
        u = node_to_string(node.child)  # type: ignore[arg-type]
        if node.length % 2 == 0:
            return "".join(c + ("1" if c == "0" else "0") for c in u)
        return "".join(c + ("1" if c == "0" else "0") for c in u[:-1]) + u[-1]
    # "odd"
    u = node_to_string(node.child)  # type: ignore[arg-type]
    if node.length % 2 == 1:
        tail = "".join(c + ("1" if c == "0" else "0") for c in u[1:])
        return ("1" if u[0] == "0" else "0") + tail
    mid = "".join(c + ("1" if c == "0" else "0") for c in u[1:-1])
    return ("1" if u[0] == "0" else "0") + mid + u[-1]


def A_mod(index: int) -> int:
    if index == 0:
        return 0
    length = find_length_by_index(index)
    rank = index - 1 - count_start1_prefix_sum(length - 1)
    node = kth_word(length, rank, 1)
    return evals(node)[0]


def A_exact(index: int) -> int:
    if index == 0:
        return 0
    length = find_length_by_index(index)
    rank = index - 1 - count_start1_prefix_sum(length - 1)
    node = kth_word(length, rank, 1)
    return int(node_to_string(node), 2)


def main() -> None:
    assert A_exact(100) == 3251
    assert A_exact(1000) == 80852364498

    total = 0
    for k in range(1, 19):
        total = (total + A_mod(10**k)) % MOD
    print(total)


if __name__ == "__main__":
    main()
