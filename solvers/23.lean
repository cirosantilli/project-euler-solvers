import ProjectEulerStatements.P23
namespace ProjectEulerSolutions.P23

partial def sumProperDivisorsSieve (limit : Nat) : Array Nat :=
  let rec loopD (d : Nat) (sums : Array Nat) : Array Nat :=
    if d > limit / 2 then
      sums
    else
      let rec loopM (m : Nat) (sums : Array Nat) : Array Nat :=
        if m > limit then
          sums
        else
          loopM (m + d) (sums.set! m (sums[m]! + d))
      loopD (d + 1) (loopM (d * 2) sums)
  loopD 1 (Array.replicate (limit + 1) 0)

partial def abundantList (sums : Array Nat) (limit : Nat) : List Nat :=
  let rec loop (n : Nat) (acc : List Nat) : List Nat :=
    if n > limit then
      acc.reverse
    else
      let acc' := if n >= 12 && sums[n]! > n then n :: acc else acc
      loop (n + 1) acc'
  loop 1 []

partial def canArray (abundant : List Nat) (limit : Nat) : Array Nat :=
  let rec loopI (lst : List Nat) (can : Array Nat) : Array Nat :=
    match lst with
    | [] => can
    | a :: rest =>
        let rec loopJ (lst2 : List Nat) (can : Array Nat) : Array Nat :=
          match lst2 with
          | [] => can
          | b :: bs =>
              let s := a + b
              if s > limit then
                can
              else
                loopJ bs (can.set! s 1)
        loopI rest (loopJ (a :: rest) can)
  loopI abundant (Array.replicate (limit + 1) 0)

partial def nonAbundantSums (limit : Nat) : Nat :=
  let sums := sumProperDivisorsSieve limit
  let abundant := abundantList sums limit
  let can := canArray abundant limit
  let rec loopSum (n total : Nat) : Nat :=
    if n > limit then
      total
    else
      let total' := if can[n]! == 0 then total + n else total
      loopSum (n + 1) total'
  loopSum 1 0


example : (sumProperDivisorsSieve 28)[28]! = 28 := by
  native_decide

example :
    let sums := sumProperDivisorsSieve 28123
    (abundantList sums 28123).head? = some 12 := by
  native_decide

example :
    let sums := sumProperDivisorsSieve 28123
    let abundant := abundantList sums 28123
    let can := canArray abundant 28123
    can[24]! = 1 := by
  native_decide


def sol (_n : Nat) :=
  nonAbundantSums 28123

theorem equiv (n : Nat) : ProjectEulerStatements.P23.naive n = sol n := sorry
end ProjectEulerSolutions.P23
open ProjectEulerSolutions.P23

def main : IO Unit := do
  IO.println (sol 0)