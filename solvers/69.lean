namespace ProjectEulerSolutions.P69

partial def primesUpToNeeded : List Nat :=
  let rec loop (candidate : Nat) (primes : List Nat) : List Nat :=
    if primes.length >= 1000 then
      primes
    else
      let rec isPrimeWith (ps : List Nat) : Bool :=
        match ps with
        | [] => true
        | p :: ps =>
            if p * p > candidate then
              true
            else if candidate % p == 0 then
              false
            else
              isPrimeWith ps
      let isP := isPrimeWith primes
      let primes := if isP then primes ++ [candidate] else primes
      let next := if candidate == 2 then 3 else candidate + 2
      loop next primes
  loop 2 []

partial def totientMaxN (limit : Nat) : Nat :=
  let rec loop (ps : List Nat) (n : Nat) : Nat :=
    match ps with
    | [] => n
    | p :: ps =>
        if n * p > limit then
          n
        else
          loop ps (n * p)
  loop (primesUpToNeeded) 1


def sol : Nat :=
  totientMaxN 1000000

example : totientMaxN 10 = 6 := by
  native_decide

end ProjectEulerSolutions.P69
open ProjectEulerSolutions.P69

def main : IO Unit := do
  IO.println sol
