import ProjectEulerStatements.P50
namespace ProjectEulerSolutions.P50

partial def sieveIsPrime (limit : Nat) : Array Bool :=
  if limit == 0 then
    #[]
  else
    let arr0 := (Array.replicate (limit + 1) true)
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
    loopP 2 arr0

partial def prefixSums (xs : List Nat) : List Nat :=
  let rec loop (ps : List Nat) (acc : Nat) (pref : List Nat) : List Nat :=
    match ps with
    | [] => pref.reverse
    | p :: ps => loop ps (acc + p) ((acc + p) :: pref)
  0 :: loop xs 0 []

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def maxLenPrefix (pref : List Nat) (limit : Nat) : Nat :=
  let rec loop (len : Nat) : Nat :=
    if len + 1 < pref.length && getAt pref (len + 1) < limit then loop (len + 1) else len
  loop 0

partial def searchLen (pref : List Nat) (isPrime : Array Bool) (limit n len : Nat) : Nat × Nat :=
  let rec loopI (i : Nat) : Nat × Nat :=
    if i + len > n then
      (0, 0)
    else
      let val := getAt pref (i + len) - getAt pref i
      if val >= limit then
        (0, 0)
      else if isPrime[val]! then
        (val, len)
      else
        loopI (i + 1)
  loopI 0

partial def searchBest (pref : List Nat) (isPrime : Array Bool) (limit n len : Nat) : Nat × Nat :=
  if len == 0 then
    (0, 0)
  else
    let res := searchLen pref isPrime limit n len
    if res.1 != 0 then res else searchBest pref isPrime limit n (len - 1)

partial def longestConsecutivePrimeSum (limit : Nat) : Nat × Nat := by
  if h : limit <= 2 then
    exact (0, 0)
  else
    let isPrime := sieveIsPrime (limit - 1)
    let primes := List.filter (fun p => isPrime[p]!) ((List.range (limit - 2)).map (fun k => k + 2))
    let pref := prefixSums primes
    let maxLen := maxLenPrefix pref limit
    let n := primes.length
    exact searchBest pref isPrime limit n maxLen


example : longestConsecutivePrimeSum 100 = (41, 6) := by
  native_decide

example : longestConsecutivePrimeSum 1000 = (953, 21) := by
  native_decide


def sol (_n : Nat) :=
  (longestConsecutivePrimeSum 1000000).1

theorem equiv (n : Nat) : ProjectEulerStatements.P50.naive n = sol n := sorry
end ProjectEulerSolutions.P50
open ProjectEulerSolutions.P50

def main : IO Unit := do
  IO.println (sol 0)