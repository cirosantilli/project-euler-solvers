namespace ProjectEulerSolutions.P49

partial def sievePrimesUpto (n : Nat) : Array Bool :=
  let arr0 := (Array.replicate (n + 1) true)
    |>.set! 0 false
    |>.set! 1 false
  let rec loopP (p : Nat) (arr : Array Bool) : Array Bool :=
    if p * p > n then
      arr
    else
      if arr[p]! then
        let rec loop (x : Nat) (arr : Array Bool) : Array Bool :=
          if x > n then
            arr
          else
            loop (x + p) (arr.set! x false)
        loopP (p + 1) (loop (p * p) arr)
      else
        loopP (p + 1) arr
  loopP 2 arr0

partial def signature (n : Nat) : Nat :=
  let counts := Array.replicate 10 0
  let rec loop (m : Nat) (counts : Array Nat) : Array Nat :=
    if m == 0 then
      counts
    else
      let d := m % 10
      loop (m / 10) (counts.set! d (counts[d]! + 1))
  let counts := loop n counts
  counts.foldl (fun acc c => acc * 5 + c) 0

partial def insertGroup (sig p : Nat) (groups : List (Nat × List Nat)) : List (Nat × List Nat) :=
  match groups with
  | [] => [(sig, [p])]
  | (s, ps) :: rest =>
      if s == sig then (s, p :: ps) :: rest else (s, ps) :: insertGroup sig p rest

partial def groupPrimes (primes : List Nat) : List (Nat × List Nat) :=
  primes.foldl (fun acc p => insertGroup (signature p) p acc) []

partial def insertSorted (x : Nat) (xs : List Nat) : List Nat :=
  match xs with
  | [] => [x]
  | y :: ys => if x <= y then x :: xs else y :: insertSorted x ys

partial def sortList (xs : List Nat) : List Nat :=
  xs.foldl (fun acc x => insertSorted x acc) []

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def findSequence : Nat × Nat × Nat :=
  let isPrime := sievePrimesUpto 9999
  let primes := (List.range 9000).map (fun k => k + 1000) |>.filter (fun p => isPrime[p]!)
  let groups := groupPrimes primes
  let targetKnown : Nat × Nat × Nat := (1487, 4817, 8147)
  let rec loopGroups (gs : List (Nat × List Nat)) : Nat × Nat × Nat :=
    match gs with
    | [] => (0, 0, 0)
    | (_, arr) :: rest =>
        let arr := sortList arr
        let s := arr
        let rec loopI (i : Nat) : Nat × Nat × Nat :=
          if i >= arr.length then (0, 0, 0) else
            let a := getAt arr i
            let rec loopJ (j : Nat) : Nat × Nat × Nat :=
              if j >= arr.length then (0, 0, 0) else
                let b := getAt arr j
                let d := b - a
                let c := b + d
                if s.contains c then
                  let seq := (a, b, c)
                  if seq != targetKnown then seq else loopJ (j + 1)
                else
                  loopJ (j + 1)
            let res := loopJ (i + 1)
            if res != (0, 0, 0) then res else loopI (i + 1)
        let res := loopI 0
        if res != (0, 0, 0) then res else loopGroups rest
  loopGroups groups


def sol : Nat :=
  let (a, b, c) := findSequence
  (toString a ++ toString b ++ toString c).toNat!

end ProjectEulerSolutions.P49
open ProjectEulerSolutions.P49

def main : IO Unit := do
  IO.println sol
