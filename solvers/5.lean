import ProjectEulerStatements.P5
namespace ProjectEulerSolutions.P5

def lcm (a b : Nat) : Nat :=
  a / Nat.gcd a b * b

partial def solve (n : Nat) : Nat :=
  let rec go (x acc : Nat) : Nat :=
    if x > n then
      acc
    else
      go (x + 1) (lcm acc x)
  go 2 1

example : solve 10 = 2520 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P5.naive n = solve n := sorry
end ProjectEulerSolutions.P5
open ProjectEulerSolutions.P5

def main : IO Unit := do
  IO.println (solve 20)
