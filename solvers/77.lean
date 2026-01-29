import ProjectEulerStatements.P77
namespace ProjectEulerSolutions.P77

partial def sievePrimes (limit : Nat) : List Nat :=
  if limit < 2 then
    []
  else
    let arr0 := Array.replicate (limit + 1) true
      |>.set! 0 false
      |>.set! 1 false
    let rec loopP (p : Nat) (arr : Array Bool) : Array Bool :=
      if p * p > limit then
        arr
      else
        if arr[p]! then
          let rec loop (m : Nat) (arr : Array Bool) : Array Bool :=
            if m > limit then
              arr
            else
              loop (m + p) (arr.set! m false)
          loopP (p + 1) (loop (p * p) arr)
        else
          loopP (p + 1) arr
    let arr := loopP 2 arr0
    (List.range (limit + 1)).filter (fun n => arr[n]!)

partial def countPrimeSummations (n : Nat) (primes : List Nat) : Nat :=
  let ways0 := Array.replicate (n + 1) 0
  let ways0 := ways0.set! 0 1
  let rec loopPr (ps : List Nat) (ways : Array Nat) : Array Nat :=
    match ps with
    | [] => ways
    | p :: ps =>
        if p > n then
          ways
        else
          let rec loopS (s : Nat) (ways : Array Nat) : Array Nat :=
            if s > n then
              ways
            else
              let ways := ways.set! s (ways[s]! + ways[s - p]!)
              loopS (s + 1) ways
          loopPr ps (loopS p ways)
  let ways := loopPr primes ways0
  ways[n]!

partial def firstValueOver (target : Nat) : Nat :=
  let rec loop (n : Nat) : Nat :=
    let primes := sievePrimes n
    let cnt := countPrimeSummations n primes
    if cnt > target then n else loop (n + 1)
  loop 2


example : countPrimeSummations 10 (sievePrimes 10) = 5 := by
  native_decide


def sol (_n : Nat) :=
  firstValueOver 5000

theorem equiv (n : Nat) : ProjectEulerStatements.P77.naive n n = sol n := sorry
end ProjectEulerSolutions.P77
open ProjectEulerSolutions.P77

def main : IO Unit := do
  IO.println (sol 0)