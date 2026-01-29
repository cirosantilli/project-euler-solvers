import ProjectEulerStatements.P88
namespace ProjectEulerSolutions.P88

partial def dfs (start prod summ terms kMax limit : Nat) (best : Array Nat) : Array Nat :=
  let maxF := limit / prod
  let rec loopF (f : Nat) (best : Array Nat) : Array Nat :=
    if f > maxF then
      best
    else
      let newProd := prod * f
      let newSum := summ + f
      let newTerms := terms + 1
      let k := newTerms + (newProd - newSum)
      let best :=
        if k <= kMax && newProd < best[k]! then best.set! k newProd else best
      let best := if k <= kMax then dfs f newProd newSum newTerms kMax limit best else best
      loopF (f + 1) best
  loopF start best

partial def minProductSumNumbersSum (kMax : Nat) : Nat :=
  let limit := 2 * kMax
  let inf := Nat.pow 10 18
  let best0 := Array.replicate (kMax + 1) inf
  let best := dfs 2 1 0 0 kMax limit best0
  let seen := Array.replicate (limit + 1) false
  let rec loopK (k : Nat) (seen : Array Bool) (sum : Nat) : Nat :=
    if k > kMax then
      sum
    else
      let v := best[k]!
      if v <= limit && seen[v]! == false then
        loopK (k + 1) (seen.set! v true) (sum + v)
      else
        loopK (k + 1) seen sum
  loopK 2 seen 0


example : minProductSumNumbersSum 6 = 30 := by
  native_decide

example : minProductSumNumbersSum 12 = 61 := by
  native_decide


def sol (_n : Nat) :=
  minProductSumNumbersSum 12000

theorem equiv (n : Nat) : ProjectEulerStatements.P88.naive ([] : List Nat) = sol n := sorry
end ProjectEulerSolutions.P88
open ProjectEulerSolutions.P88

def main : IO Unit := do
  IO.println (sol 0)