import ProjectEulerStatements.P3
namespace ProjectEulerStatements.P3

partial def stripTwos (n : Nat) (largest : Nat) : Nat × Nat :=
  if n % 2 == 0 then
    stripTwos (n / 2) 2
  else
    (n, largest)

partial def oddLoop (n f largest : Nat) : Nat :=
  if f * f <= n then
    if n % f == 0 then
      oddLoop (n / f) f f
    else
      oddLoop n (f + 2) largest
  else
    if n > 1 then n else largest

def largestPrimeFactor (n : Nat) : Nat :=
  let (n', largest') := stripTwos n 1
  oddLoop n' 3 largest'

def sol (n : Nat) : Nat :=
  largestPrimeFactor n

example : sol 13195 = 29 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P3.naive ⟨2, by decide⟩ = sol n := sorry

end ProjectEulerStatements.P3
open ProjectEulerStatements.P3

def main : IO Unit := do
  IO.println (sol 600851475143)
