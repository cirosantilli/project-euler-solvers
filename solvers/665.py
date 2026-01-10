#!/usr/bin/env python3
"""
Project Euler 665 - Proportionate Nim

We compute f(M) = sum(n+m) over all losing positions (n,m) with n<=m and n+m<=M
for the 2-pile game with moves:
 - remove n from one pile
 - remove n from both piles
 - remove n from one and 2n from the other

This game is (1,2)-GDWN. Losing positions are generated greedily by avoiding
previously used invariants:
  d = b-a
  e = b-2a
  f = 2b-a
(and their symmetric counterparts).

Pure Python is fine for the small test cases, but for M=10^7 we compile
and run an optimized C++ implementation.
"""

import os
import sys
import hashlib
import subprocess
from array import array


# ---------------------------
# Small pure-Python validator
# ---------------------------
def f_python(M: int) -> int:
    """Pure Python version used for small M only (e.g. <= 1000)."""
    limit_a = M // 2
    maxN = 3 * limit_a + 10

    parent = array("I", range(maxN + 2))
    offD = maxN
    D = bytearray(2 * maxN + 1)

    offE = 2 * maxN
    E = bytearray(3 * maxN + 1)

    offF = maxN
    F = bytearray(3 * maxN + 1)

    # mark invariant zero used
    D[offD] = 1
    E[offE] = 1
    F[offF] = 1

    par = parent
    par[0] = 1  # mark 0 used

    def find(x: int) -> int:
        while True:
            px = par[x]
            if px == x:
                return x
            par[x] = par[px]
            x = px

    def use(x: int) -> None:
        par[x] = find(x + 1)

    use(0)

    total = 0
    a = find(1)

    while a <= limit_a:
        b = find(a + 1)
        two_a = a << 1

        while True:
            d = b - a
            if D[d + offD]:
                b = find(b + 1)
                continue
            e = b - two_a
            if E[e + offE]:
                b = find(b + 1)
                continue
            f = (b << 1) - a
            if F[f + offF]:
                b = find(b + 1)
                continue
            break

        # accept (a,b)
        use(a)
        use(b)

        D[d + offD] = 1
        D[-d + offD] = 1

        E[e + offE] = 1
        E[(a - (b << 1)) + offE] = 1

        F[f + offF] = 1
        F[(two_a - b) + offF] = 1

        s = a + b
        if s <= M:
            total += s

        a = find(a)

    return total


# ---------------------------
# C++ accelerator (embedded)
# ---------------------------
CPP_SOURCE = r"""
#include <bits/stdc++.h>
using namespace std;

static inline uint32_t dsu_find(vector<uint32_t>& p, uint32_t x){
    while(p[x] != x){
        p[x] = p[p[x]];
        x = p[x];
    }
    return x;
}

int main(int argc, char** argv){
    uint32_t M = 10000000u;
    if(argc >= 2) M = (uint32_t)strtoul(argv[1], nullptr, 10);

    uint32_t limit_a = M / 2;
    uint32_t maxN = 3 * limit_a + 10;

    vector<uint32_t> parent(maxN + 2);
    for(uint32_t i=0;i<=(uint32_t)maxN+1;i++) parent[i]=i;

    const uint32_t offD = maxN;
    vector<uint8_t> D(2*maxN + 1, 0);

    const uint32_t offE = 2*maxN;
    vector<uint8_t> E(3*maxN + 1, 0);

    const uint32_t offF = maxN;
    vector<uint8_t> F(3*maxN + 1, 0);

    // invariant zero used
    D[offD] = 1;
    E[offE] = 1;
    F[offF] = 1;

    // mark 0 used in DSU
    parent[0] = 1;
    parent[0] = dsu_find(parent, 1);

    auto dsu_use = [&](uint32_t x){
        parent[x] = dsu_find(parent, x+1);
    };

    uint64_t total = 0;

    uint32_t a = dsu_find(parent, 1);
    while(a <= limit_a){
        uint32_t b = dsu_find(parent, a+1);
        uint32_t two_a = a << 1;

        int32_t d,e;
        int32_t f;

        while(true){
            d = (int32_t)b - (int32_t)a;
            if(D[(int32_t)d + (int32_t)offD]){
                b = dsu_find(parent, b+1);
                continue;
            }
            e = (int32_t)b - (int32_t)two_a;
            if(E[(int32_t)e + (int32_t)offE]){
                b = dsu_find(parent, b+1);
                continue;
            }
            f = (int32_t)(b<<1) - (int32_t)a;
            if(F[(int32_t)f + (int32_t)offF]){
                b = dsu_find(parent, b+1);
                continue;
            }
            break;
        }

        // accept (a,b)
        dsu_use(a);
        dsu_use(b);

        D[d + (int32_t)offD] = 1;
        D[-d + (int32_t)offD] = 1;

        E[e + (int32_t)offE] = 1;
        E[(int32_t)a - (int32_t)(b<<1) + (int32_t)offE] = 1;

        F[f + (int32_t)offF] = 1;
        F[(int32_t)two_a - (int32_t)b + (int32_t)offF] = 1;

        uint32_t s = a + b;
        if(s <= M) total += s;

        a = dsu_find(parent, a);
    }

    cout << total << "\n";
    return 0;
}
"""


def compile_cpp() -> str:
    """Compile the embedded C++ code and return the executable path."""
    src_hash = hashlib.sha256(CPP_SOURCE.encode("utf-8")).hexdigest()[:16]
    exe_name = f"euler665_{src_hash}.bin"
    exe_path = os.path.join(os.path.dirname(__file__), exe_name)

    if os.path.exists(exe_path):
        return exe_path

    cpp_path = os.path.join(os.path.dirname(__file__), f"euler665_{src_hash}.cpp")
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.write(CPP_SOURCE)

    cmd = ["g++", "-O3", "-std=c++17", cpp_path, "-o", exe_path]
    subprocess.check_call(cmd)
    return exe_path


def f_fast(M: int) -> int:
    """Compute using the compiled C++ accelerator."""
    exe = compile_cpp()
    out = subprocess.check_output([exe, str(M)], text=True).strip()
    return int(out)


def main():
    # Required asserts from problem statement
    assert f_python(10) == 21
    assert f_python(100) == 1164
    assert f_python(1000) == 117002

    M = 10**7
    try:
        ans = f_fast(M)
    except Exception:
        # Fallback (will be far too slow for 1e7, but keeps correctness)
        ans = f_python(M)

    print(ans)


if __name__ == "__main__":
    main()
