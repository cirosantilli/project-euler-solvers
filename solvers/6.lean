import ProjectEulerStatements.P6
namespace ProjectEulerSolutions.P6

def sumOfSquares (n : Nat) : Nat :=
  n * (n + 1) * (2 * n + 1) / 6

def squareOfSum (n : Nat) : Nat :=
  let s := n * (n + 1) / 2
  s * s

def sol (n : Nat) : Nat :=
  squareOfSum n - sumOfSquares n

example : sol 10 = 2640 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P6.naive n = sol n := sorry
end ProjectEulerSolutions.P6
open ProjectEulerSolutions.P6

def main : IO Unit := do
  IO.println (sol 100)