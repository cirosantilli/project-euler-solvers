import ProjectEulerStatements.P7
namespace ProjectEulerSolutions.P7

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

partial def nthPrime (n : Nat) : Nat :=
  if n == 1 then
    2
  else
    let rec go (candidate count : Nat) (primes : Array Nat) : Nat :=
      if count == n then
        primes[primes.size - 1]!
      else
        if isPrimeWith candidate primes then
          let primes' := primes.push candidate
          go (candidate + 2) (count + 1) primes'
        else
          go (candidate + 2) count primes
    go 3 1 #[2]

def sol (n : Nat) : Nat :=
  nthPrime n

example : sol 1 = 2 := by
  native_decide

example : sol 6 = 13 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P7.naive n = sol n := sorry
end ProjectEulerSolutions.P7
open ProjectEulerSolutions.P7

def main : IO Unit := do
  IO.println (sol 10001)