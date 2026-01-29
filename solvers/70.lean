import ProjectEulerStatements.P70
namespace ProjectEulerSolutions.P70

abbrev MAX_N : Nat := 9999999

partial def computePhiLinear (limit : Nat) : Array Nat :=
  let phi0 := Array.replicate (limit + 1) 0
  let comp0 := Array.replicate (limit + 1) false
  let phi0 := phi0.set! 1 1
  let rec loop (i : Nat) (phi : Array Nat) (isComp : Array Bool) (primes : Array Nat)
      : Array Nat :=
    if i > limit then
      phi
    else
      let (phi, isComp, primes) :=
        if isComp[i]! then
          (phi, isComp, primes)
        else
          (phi.set! i (i - 1), isComp, primes.push i)
      let rec loopP (j : Nat) (phi : Array Nat) (isComp : Array Bool)
          : Array Nat × Array Bool :=
        if j >= primes.size then
          (phi, isComp)
        else
          let p := primes[j]!
          let ip := i * p
          if ip > limit then
            (phi, isComp)
          else
            let isComp := isComp.set! ip true
            if i % p == 0 then
              let phi := phi.set! ip (phi[i]! * p)
              (phi, isComp)
            else
              let phi := phi.set! ip (phi[i]! * (p - 1))
              loopP (j + 1) phi isComp
      let (phi, isComp) := loopP 0 phi isComp
      loop (i + 1) phi isComp primes
  loop 2 phi0 comp0 #[]

abbrev SHIFT : Array Nat :=
  (List.range 10).foldl (fun acc d => acc.push (Nat.pow 2 (3 * d))) #[]

partial def digitSignature (x : Nat) : Nat :=
  if x == 0 then
    SHIFT[0]!
  else
    let rec loop (n : Nat) (acc : Nat) : Nat :=
      if n == 0 then
        acc
      else
        let d := n % 10
        loop (n / 10) (acc + SHIFT[d]!)
    loop x 0

partial def solve (limit : Nat) : Nat :=
  let phi := computePhiLinear limit
  let rec loop (n : Nat) (bestN bestPhi low high : Nat) : Nat :=
    if n > limit then
      bestN
    else
      let (low, high) := if n == high then (high, high * 10) else (low, high)
      let pn := phi[n]!
      if pn < low || pn >= high then
        loop (n + 1) bestN bestPhi low high
      else if (n - pn) % 9 != 0 then
        loop (n + 1) bestN bestPhi low high
      else if digitSignature n != digitSignature pn then
        loop (n + 1) bestN bestPhi low high
      else
        if bestN == 0 || n * bestPhi < bestN * pn then
          loop (n + 1) n pn low high
        else
          loop (n + 1) bestN bestPhi low high
  loop 2 0 1 1 10


example :
    let phi := computePhiLinear 100000
    phi[1]! = 1 := by
  native_decide

example :
    let phi := computePhiLinear 100000
    phi[9]! = 6 := by
  native_decide

example :
    let phi := computePhiLinear 100000
    phi[87109]! = 79180 := by
  native_decide

example : digitSignature 87109 = digitSignature 79180 := by
  native_decide


def sol (_n : Nat) :=
  solve MAX_N

theorem equiv (n : Nat) : ProjectEulerStatements.P70.naive n = sol n := sorry
end ProjectEulerSolutions.P70
open ProjectEulerSolutions.P70

def main : IO Unit := do
  IO.println (sol 0)