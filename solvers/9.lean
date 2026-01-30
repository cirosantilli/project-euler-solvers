import ProjectEulerStatements.P9
namespace ProjectEulerSolutions.P9

partial def solve (total : Nat) : Nat :=
  let rec loopM (m : Nat) : Nat :=
    if 2 * m * (m + 1) > total then
      0
    else
      let rec loopN (n : Nat) : Nat :=
        if n >= m then
          0
        else
          let s := 2 * m * (m + n)
          if total % s != 0 then
            loopN (n + 1)
          else
            let k := total / s
            let a := k * (m * m - n * n)
            let b := k * (2 * m * n)
            let c := k * (m * m + n * n)
            if a > 0 && a * a + b * b == c * c && a + b + c == total then
              a * b * c
            else
              loopN (n + 1)
      let res := loopN 1
      if res != 0 then res else loopM (m + 1)
  loopM 2

example : solve 12 = 60 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P9.naive n = solve n := sorry
end ProjectEulerSolutions.P9
open ProjectEulerSolutions.P9

def main : IO Unit := do
  IO.println (solve 1000)
