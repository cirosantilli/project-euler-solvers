namespace ProjectEulerSolutions.P37

partial def sieve (limit : Nat) : Array Bool :=
  if limit == 0 then
    #[]
  else
    let arr0 := (Array.replicate (limit + 1) true)
      |>.set! 0 false
      |>.set! 1 false
    let rec markEven (i : Nat) (arr : Array Bool) : Array Bool :=
      if i > limit then arr else markEven (i + 2) (arr.set! i false)
    let arr := if limit >= 4 then markEven 4 arr0 else arr0
    let rec loopP (p : Nat) (arr : Array Bool) : Array Bool :=
      if p * p > limit then
        arr
      else
        if arr[p]! then
          let rec loop (x : Nat) (arr : Array Bool) : Array Bool :=
            if x > limit then
              arr
            else
              loop (x + 2 * p) (arr.set! x false)
          loopP (p + 2) (loop (p * p) arr)
        else
          loopP (p + 2) arr
    loopP 3 arr

partial def digitsCount (n : Nat) : Nat :=
  let rec loop (m c : Nat) : Nat :=
    if m < 10 then c + 1 else loop (m / 10) (c + 1)
  if n == 0 then 1 else loop n 0

partial def pow10 (k : Nat) : Nat :=
  Nat.pow 10 k

partial def isTruncatablePrime (n : Nat) (isPrime : Array Bool) : Bool :=
  if n < 10 then
    false
  else
    let len := digitsCount n
    let rec loopR (m : Nat) : Bool :=
      if m == 0 then true
      else if !isPrime[m]! then false else loopR (m / 10)
    let rec loopL (k : Nat) : Bool :=
      if k == 0 then true
      else
        let m := n % pow10 k
        if !isPrime[m]! then false else loopL (k - 1)
    loopR n && loopL (len - 1)

partial def solve : Nat :=
  let limit := 1000000
  let isPrime := sieve limit
  let rec loop (n found total : Nat) : Nat :=
    if n > limit then
      total
    else if found == 11 then
      total
    else
      if n % 2 == 1 && isPrime[n]! && isTruncatablePrime n isPrime then
        loop (n + 2) (found + 1) (total + n)
      else
        loop (n + 2) found total
  loop 11 0 0


def sol : Nat :=
  solve

example :
    let isPrime := sieve 1000000
    isPrime[3797]! = true := by
  native_decide

example :
    let isPrime := sieve 1000000
    isTruncatablePrime 3797 isPrime = true := by
  native_decide

example :
    let isPrime := sieve 1000000
    isTruncatablePrime 2 isPrime = false := by
  native_decide

example :
    let isPrime := sieve 1000000
    isTruncatablePrime 3 isPrime = false := by
  native_decide

example :
    let isPrime := sieve 1000000
    isTruncatablePrime 5 isPrime = false := by
  native_decide

example :
    let isPrime := sieve 1000000
    isTruncatablePrime 7 isPrime = false := by
  native_decide

end ProjectEulerSolutions.P37
open ProjectEulerSolutions.P37

def main : IO Unit := do
  IO.println sol
