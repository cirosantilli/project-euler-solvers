namespace ProjectEulerSolutions.P35

partial def primeSieve (n : Nat) : Array Bool :=
  if n == 0 then
    #[]
  else
    let arr0 := (Array.replicate n true)
      |>.set! 0 false
      |>.set! 1 false
    let rec loopP (p : Nat) (arr : Array Bool) : Array Bool :=
      if p * p > n - 1 then
        arr
      else
        if arr[p]! then
          let rec loop (j : Nat) (arr : Array Bool) : Array Bool :=
            if j >= n then
              arr
            else
              loop (j + p) (arr.set! j false)
          loopP (p + 1) (loop (p * p) arr)
        else
          loopP (p + 1) arr
    loopP 2 arr0

partial def digitsCount (n : Nat) : Nat :=
  let rec loop (m c : Nat) : Nat :=
    if m < 10 then c + 1 else loop (m / 10) (c + 1)
  if n == 0 then 1 else loop n 0

partial def pow10 (k : Nat) : Nat :=
  Nat.pow 10 k

partial def rotationsOf (n : Nat) : List Nat :=
  let k := digitsCount n
  if k == 1 then
    [n]
  else
    let p := pow10 (k - 1)
    let rec loop (i : Nat) (x : Nat) (acc : List Nat) : List Nat :=
      if i == k then
        acc.reverse
      else
        let acc' := x :: acc
        let x' := (x % p) * 10 + (x / p)
    loop (i + 1) x' acc'
    loop 0 n []

partial def allowedDigits (n : Nat) : Bool :=
  let rec loop (m : Nat) : Bool :=
    if m == 0 then
      true
    else
      let d := m % 10
      if d == 0 || d == 2 || d == 4 || d == 5 || d == 6 || d == 8 then
        false
      else
        loop (m / 10)
  loop n

partial def isCircularPrime (n : Nat) (isPrime : Array Bool) : Bool :=
  let rots := rotationsOf n
  rots.all (fun r => isPrime[r]!)

partial def countDistinctUnder (rots : List Nat) (limit : Nat) : Nat :=
  let rec loop (lst : List Nat) (seen : List Nat) (acc : Nat) : Nat :=
    match lst with
    | [] => acc
    | r :: rs =>
        if r < limit && !seen.contains r then
          loop rs (r :: seen) (acc + 1)
        else
          loop rs seen acc
  loop rots [] 0

partial def circularPrimeCount (limit : Nat) : Nat :=
  if limit <= 2 then
    0
  else
    let d := digitsCount (limit - 1)
    let sieveN := if limit > pow10 d then limit else pow10 d
    let isPrime := primeSieve sieveN
    let processed := Array.replicate limit false
    let rec loop (p count : Nat) (processed : Array Bool) : Nat :=
      if p >= limit then
        count
      else
        if !isPrime[p]! || processed[p]! then
          loop (p + 1) count processed
        else
          let processed := processed.set! p true
          if p < 10 then
            loop (p + 1) (count + 1) processed
          else if !allowedDigits p then
            loop (p + 1) count processed
          else
            let rots := rotationsOf p
            let processed :=
              rots.foldl (fun acc r => if r < limit then acc.set! r true else acc) processed
            if rots.all (fun r => isPrime[r]!) then
              let add := countDistinctUnder rots limit
              loop (p + 1) (count + add) processed
            else
              loop (p + 1) count processed
    loop 2 0 processed


def sol : Nat :=
  circularPrimeCount 1000000

example : circularPrimeCount 100 = 13 := by
  native_decide

example : isCircularPrime 197 (primeSieve 1000) = true := by
  native_decide

end ProjectEulerSolutions.P35
open ProjectEulerSolutions.P35

def main : IO Unit := do
  IO.println sol
