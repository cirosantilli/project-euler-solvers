namespace ProjectEulerSolutions.P58

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

partial def sideLengthWhenRatioBelow : Nat :=
  let rec loop (k primeCount totalDiag : Nat) : Nat :=
    let side := 2 * k + 1
    let step := side - 1
    let sq := side * side
    let corners := [sq - step, sq - 2 * step, sq - 3 * step]
    let primeCount := primeCount + corners.foldl (fun acc x => if isPrime x then acc + 1 else acc) 0
    let totalDiag := totalDiag + 4
    if primeCount * 10 < totalDiag then
      side
    else
      loop (k + 1) primeCount totalDiag
  loop 1 0 1

partial def primeRatioCountsForSide (side : Nat) : Nat × Nat :=
  let rec loop (k : Nat) (primeCount totalDiag : Nat) : Nat × Nat :=
    if k > (side - 1) / 2 then
      (primeCount, totalDiag)
    else
      let s := 2 * k + 1
      let step := s - 1
      let sq := s * s
      let corners := [sq - step, sq - 2 * step, sq - 3 * step]
      let primeCount := primeCount + corners.foldl (fun acc x => if isPrime x then acc + 1 else acc) 0
      let totalDiag := totalDiag + 4
      loop (k + 1) primeCount totalDiag
  if side % 2 == 0 || side == 0 then
    (0, 0)
  else
    loop 1 0 1


def sol : Nat :=
  sideLengthWhenRatioBelow

example : primeRatioCountsForSide 7 = (8, 13) := by
  native_decide

example : primeRatioCountsForSide 3 = (3, 5) := by
  native_decide

end ProjectEulerSolutions.P58
open ProjectEulerSolutions.P58

def main : IO Unit := do
  IO.println sol
