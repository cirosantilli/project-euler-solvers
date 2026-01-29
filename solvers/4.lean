import ProjectEulerStatements.P4
namespace ProjectEulerSolutions.P4

def isPalindrome (n : Nat) : Bool :=
  let s := toString n
  s = String.mk s.data.reverse

partial def loopB (a b lo best bestA bestB : Nat) : Nat × Nat × Nat :=
  if b < lo then
    (best, bestA, bestB)
  else
    let prod := a * b
    if prod <= best then
      (best, bestA, bestB)
    else if isPalindrome prod then
      (prod, a, b)
    else
      loopB a (b - 1) lo best bestA bestB

partial def loopA (a lo hi best bestA bestB : Nat) : Nat × Nat × Nat :=
  if a < lo then
    (best, bestA, bestB)
  else if a * hi < best then
    (best, bestA, bestB)
  else
    let (best', bestA', bestB') := loopB a a lo best bestA bestB
    if a = 0 then
      (best', bestA', bestB')
    else
      loopA (a - 1) lo hi best' bestA' bestB'

def largestPalindromeProduct (lo hi : Nat) : Nat × Nat × Nat :=
  loopA hi lo hi 0 0 0

example : (largestPalindromeProduct 10 99).1 = 9009 := by
  native_decide


def sol (_n : Nat) : Nat :=
  (largestPalindromeProduct 100 999).1

theorem equiv (n : Nat) : ProjectEulerStatements.P4.naive n = sol n := sorry
end ProjectEulerSolutions.P4
open ProjectEulerSolutions.P4

def main : IO Unit := do
  IO.println (sol 0)
