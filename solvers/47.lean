import ProjectEulerStatements.P47
namespace ProjectEulerSolutions.P47

partial def distinctPrimeFactorCounts (limit : Nat) : Array Nat :=
  let counts := Array.replicate (limit + 1) 0
  let rec loopP (p : Nat) (counts : Array Nat) : Array Nat :=
    if p > limit then
      counts
    else
      if counts[p]! == 0 then
        let rec loopM (m : Nat) (counts : Array Nat) : Array Nat :=
          if m > limit then
            counts
          else
            loopM (m + p) (counts.set! m (counts[m]! + 1))
        loopP (p + 1) (loopM p counts)
      else
        loopP (p + 1) counts
  loopP 2 counts

partial def firstConsecutiveWithKFactors (k runLen startLimit : Nat) : Nat :=
  let rec loopLimit (limit : Nat) : Nat :=
    let counts := distinctPrimeFactorCounts limit
    let rec loopN (n streak : Nat) : Nat :=
      if n > limit then
        0
      else if counts[n]! == k then
        if streak + 1 == runLen then
          n - runLen + 1
        else
          loopN (n + 1) (streak + 1)
      else
        loopN (n + 1) 0
    let found := loopN 2 0
    if found != 0 then found else loopLimit (limit * 2)
  loopLimit startLimit


example : firstConsecutiveWithKFactors 2 2 100 = 14 := by
  native_decide

example : firstConsecutiveWithKFactors 3 3 2000 = 644 := by
  native_decide


def sol (_n : Nat) :=
  firstConsecutiveWithKFactors 4 4 200000

theorem equiv (n : Nat) : ProjectEulerStatements.P47.naive n n n = sol n := sorry
end ProjectEulerSolutions.P47
open ProjectEulerSolutions.P47

def main : IO Unit := do
  IO.println (sol 0)