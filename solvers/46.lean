namespace ProjectEulerSolutions.P46

partial def isPrimeWithList (n : Nat) (primes : List Nat) : Bool :=
  if n < 2 then
    false
  else
    let rec loop (ps : List Nat) : Bool :=
      match ps with
      | [] => true
      | p :: ps =>
          if p * p > n then
            true
          else if n % p == 0 then
            false
          else
            loop ps
    loop primes

partial def lastOr (xs : List Nat) (default : Nat) : Nat :=
  match xs.reverse with
  | [] => default
  | x :: _ => x

partial def ensurePrimesUpTo (n : Nat) (primes : List Nat) : List Nat :=
  let rec loop (candidate : Nat) (primes : List Nat) : List Nat :=
    if lastOr primes 0 >= n then
      primes
    else
      let primes := if isPrimeWithList candidate primes then primes ++ [candidate] else primes
      loop (candidate + 2) primes
  if lastOr primes 0 >= n then primes else loop (lastOr primes 0 + 2) primes

partial def sqrtIfSquare (n : Nat) : Nat :=
  let rec loop (i : Nat) : Nat :=
    if i * i > n then 0 else if i * i == n then i else loop (i + 1)
  loop 1

partial def canBeWritten (n : Nat) (primes : List Nat) : Bool :=
  let primes := ensurePrimesUpTo n primes
  let rec loop (ps : List Nat) : Bool :=
    match ps with
    | [] => false
    | p :: ps =>
        if p >= n then
          false
        else
          let rem := n - p
          if rem % 2 != 0 then
            loop ps
          else
            let t := rem / 2
            let s := sqrtIfSquare t
            if s != 0 then
              true
            else
              loop ps
  loop primes

partial def smallestCounterexample : Nat :=
  let rec loop (n : Nat) (primes : List Nat) : Nat :=
    let primes := ensurePrimesUpTo n primes
    if !isPrimeWithList n primes && !canBeWritten n primes then
      n
    else
      loop (n + 2) primes
  loop 9 [2, 3]

def sol : Nat :=
  smallestCounterexample

example :
    let primes := [2, 3]
    [9, 15, 21, 25, 27, 33].all (fun x => canBeWritten x primes) = true := by
  native_decide

end ProjectEulerSolutions.P46
open ProjectEulerSolutions.P46

def main : IO Unit := do
  IO.println sol
