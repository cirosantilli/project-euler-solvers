import ProjectEulerStatements.P25
namespace ProjectEulerSolutions.P25

partial def fibPair (n : Nat) : Nat × Nat :=
  if n == 0 then
    (0, 1)
  else
    let (a, b) := fibPair (n / 2)
    let c := a * (2 * b - a)
    let d := a * a + b * b
    if n % 2 == 0 then
      (c, d)
    else
      (d, c + d)

partial def fib (n : Nat) : Nat :=
  (fibPair n).1

partial def firstFibIndexWithDigits (digits : Nat) : Nat :=
  if digits <= 1 then
    1
  else
    let threshold := Nat.pow 10 (digits - 1)
    let rec findUpper (hi : Nat) : Nat :=
      if fib hi >= threshold then hi else findUpper (hi * 2)
    let rec binary (lo hi : Nat) : Nat :=
      if lo >= hi then
        lo
      else
        let mid := (lo + hi) / 2
        if fib mid >= threshold then
          binary lo mid
        else
          binary (mid + 1) hi
    let hi := findUpper 1
    binary 1 hi


def sol (digits : Nat) : Nat :=
  firstFibIndexWithDigits digits

example : sol 1 = 1 := by
  native_decide

example : sol 2 = 7 := by
  native_decide

example : sol 3 = 12 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P25.naive n n = sol n := sorry
end ProjectEulerSolutions.P25
open ProjectEulerSolutions.P25

def main : IO Unit := do
  IO.println (sol 1000)