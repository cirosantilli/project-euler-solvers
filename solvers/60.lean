namespace ProjectEulerSolutions.P60

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

partial def primesUpTo (limit : Nat) : List Nat :=
  let isPrime := sieveIsPrime limit
  (List.range (limit + 1)).filter (fun n => isPrime[n]!)

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def powMod (a d n : Nat) : Nat :=
  let rec loop (base exp acc : Nat) : Nat :=
    if exp == 0 then
      acc
    else
      let acc := if exp % 2 == 1 then (acc * base) % n else acc
      loop ((base * base) % n) (exp / 2) acc
  if n == 1 then 0 else loop (a % n) d 1

partial def decompose (n : Nat) : Nat × Nat :=
  let rec loop (d s : Nat) : Nat × Nat :=
    if d % 2 == 1 then
      (d, s)
    else
      loop (d / 2) (s + 1)
  loop n 0

partial def millerCheck (a n d s : Nat) : Bool :=
  if a % n == 0 then
    true
  else
    let x := powMod a d n
    if x == 1 || x == n - 1 then
      true
    else
      let rec loop (r : Nat) (x : Nat) : Bool :=
        if r == 0 then
          false
        else
          let x := (x * x) % n
          if x == n - 1 then true else loop (r - 1) x
      loop (s - 1) x

partial def isPrime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let smallPrimes : List Nat := [2,3,5,7,11,13,17,19,23,29,31,37]
    let rec checkSmall (ps : List Nat) : Bool :=
      match ps with
      | [] => true
      | p :: ps => if n == p then true else if n % p == 0 then false else checkSmall ps
    if checkSmall smallPrimes == false then
      false
    else
      let (d, s) := decompose (n - 1)
      let bases : List Nat := [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
      let rec loop (bs : List Nat) : Bool :=
        match bs with
        | [] => true
        | a :: bs => if millerCheck a n d s then loop bs else false
      loop bases

partial def pow10For (n : Nat) : Nat :=
  let rec loop (p : Nat) : Nat :=
    if p > n then p else loop (p * 10)
  loop 1

partial def pairOk (p q : Nat) : Bool :=
  if (p + q) % 3 == 0 then
    false
  else
    let c1 := p * pow10For q + q
    if isPrime c1 == false then
      false
    else
      let c2 := q * pow10For p + p
      isPrime c2

partial def insertAsc (x : Nat) (xs : List Nat) : List Nat :=
  match xs with
  | [] => [x]
  | y :: ys => if x <= y then x :: y :: ys else y :: insertAsc x ys

partial def sortAsc (xs : List Nat) : List Nat :=
  xs.foldl (fun acc x => insertAsc x acc) []

partial def solve (limit : Nat) : Nat × List Nat :=
  let primes := (primesUpTo limit).filter (fun p => p != 2 && p != 5)
  let rec dfs (clique candidates : List Nat) (currSum bestSum : Nat) (bestSet : List Nat) : Nat × List Nat :=
    let k := clique.length
    if k == 5 then
      if currSum < bestSum then (currSum, clique) else (bestSum, bestSet)
    else
      let need := 5 - k
      if candidates.length < need then
        (bestSum, bestSet)
      else
        let rec loopIdx (cand : List Nat) (bestSum : Nat) (bestSet : List Nat) : Nat × List Nat :=
          match cand with
          | [] => (bestSum, bestSet)
          | q :: qs =>
              if currSum + q * need >= bestSum then
                (bestSum, bestSet)
              else
                let rec build (rest : List Nat) (acc : List Nat) : List Nat :=
                  match rest with
                  | [] => acc.reverse
                  | r :: rs =>
                      if currSum + q + r * (need - 1) >= bestSum then
                        acc.reverse
                      else
                        if pairOk q r then
                          build rs (r :: acc)
                        else
                          build rs acc
                let newCandidates := build qs []
                let (bestSum, bestSet) :=
                  if newCandidates.length >= (need - 1) then
                    dfs (clique ++ [q]) newCandidates (currSum + q) bestSum bestSet
                  else
                    (bestSum, bestSet)
                loopIdx qs bestSum bestSet
        loopIdx candidates bestSum bestSet
  let rec loopP (ps : List Nat) (bestSum : Nat) (bestSet : List Nat) : Nat × List Nat :=
    match ps with
    | [] => (bestSum, bestSet)
    | p :: ps =>
        if p * 5 >= bestSum then
          (bestSum, bestSet)
        else
          let rec build (rest : List Nat) (acc : List Nat) : List Nat :=
            match rest with
            | [] => acc.reverse
            | q :: qs =>
                if p + q * 4 >= bestSum then
                  acc.reverse
                else
                  if pairOk p q then
                    build qs (q :: acc)
                  else
                    build qs acc
          let candidates := build ps []
          let (bestSum, bestSet) :=
            if candidates.length >= 4 then
              dfs [p] candidates p bestSum bestSet
            else
              (bestSum, bestSet)
          loopP ps bestSum bestSet
  loopP primes (Nat.pow 10 30) []


def sol : Nat :=
  (solve 10000).1

example :
    let ex := [3, 7, 109, 673]
    let ok := (List.range ex.length).all (fun i =>
      (List.range ex.length).all (fun j =>
        if i < j then pairOk (getAt ex i) (getAt ex j) else true))
    ok = true := by
  native_decide

example :
    let res := solve 10000
    let s := sortAsc res.2
    s = [13, 5197, 5701, 6733, 8389] := by
  native_decide

end ProjectEulerSolutions.P60
open ProjectEulerSolutions.P60

def main : IO Unit := do
  IO.println sol
