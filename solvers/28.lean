import ProjectEulerStatements.P28
namespace ProjectEulerSolutions.P28

partial def spiralDiagonalsSum (n : Nat) : Nat :=
  let m := (n - 1) / 2
  let total := 1
  let sumSquares := 16 * m * (m + 1) * (2 * m + 1) / 6
  let sumLinear := 4 * m * (m + 1) / 2
  let sumOnes := 4 * m
  total + sumSquares + sumLinear + sumOnes


def sol (n : Nat) : Nat :=
  spiralDiagonalsSum n

example : sol 5 = 101 := by
  native_decide

example : sol 1 = 1 := by
  native_decide

example : sol 3 = 25 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P28.naive n = sol n := sorry
end ProjectEulerSolutions.P28
open ProjectEulerSolutions.P28

def main : IO Unit := do
  IO.println (sol 1001)