import ProjectEulerStatements.P10
namespace ProjectEulerSolutions.P10

partial def isPrimeWith (n : Nat) (primes : Array Nat) : Bool :=
  let rec loop (i : Nat) : Bool :=
    if i >= primes.size then
      true
    else
      let p := primes[i]!
      if p * p > n then
        true
      else if n % p == 0 then
        false
      else
        loop (i + 1)
  loop 0

partial def solve (limit : Nat) : Nat :=
  if limit <= 2 then
    0
  else if limit <= 3 then
    2
  else
    let rec go (candidate sum : Nat) (primes : Array Nat) : Nat :=
      if candidate >= limit then
        sum
      else
        if isPrimeWith candidate primes then
          go (candidate + 2) (sum + candidate) (primes.push candidate)
        else
          go (candidate + 2) sum primes
    go 3 2 #[2]

example : solve 10 = 17 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P10.naive n = solve n := sorry
end ProjectEulerSolutions.P10
open ProjectEulerSolutions.P10

def main : IO Unit := do
  IO.println (solve 2000000)
