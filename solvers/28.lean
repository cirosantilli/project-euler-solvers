import ProjectEulerStatements.P28
namespace ProjectEulerSolutions.P28

partial def solve (n : Nat) : Nat :=
  let m := (n - 1) / 2
  let total := 1
  let sumSquares := 16 * m * (m + 1) * (2 * m + 1) / 6
  let sumLinear := 4 * m * (m + 1) / 2
  let sumOnes := 4 * m
  total + sumSquares + sumLinear + sumOnes

example : solve 5 = 101 := by
  native_decide

example : solve 1 = 1 := by
  native_decide

example : solve 3 = 25 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P28.naive n = solve n := sorry
end ProjectEulerSolutions.P28
open ProjectEulerSolutions.P28

def main : IO Unit := do
  IO.println (solve 1001)
