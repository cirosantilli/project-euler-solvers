import ProjectEulerStatements.P27
namespace ProjectEulerSolutions.P27

partial def sievePrimes (limit : Nat) : Array Nat :=
  if limit < 2 then
    #[]
  else
    let rec mark (p : Nat) (arr : Array Bool) : Array Bool :=
      if p * p > limit then
        arr
      else
        if arr[p]! then
          let rec loop (j : Nat) (arr : Array Bool) : Array Bool :=
            if j > limit then
              arr
            else
              loop (j + p) (arr.set! j false)
          mark (p + 1) (loop (p * p) arr)
        else
          mark (p + 1) arr
    let arr0 := (Array.replicate (limit + 1) true).set! 0 false |>.set! 1 false
    let arr := mark 2 arr0
    let rec collect (i : Nat) (acc : Array Nat) : Array Nat :=
      if i > limit then
        acc
      else
        let acc' := if arr[i]! then acc.push i else acc
        collect (i + 1) acc'
    collect 2 #[]

partial def isPrimeNat (n : Nat) (trial : Array Nat) : Bool :=
  if n < 2 then
    false
  else
    let rec loop (i : Nat) : Bool :=
      if i >= trial.size then
        true
      else
        let p := trial[i]!
        if p * p > n then
          true
        else if n % p == 0 then
          n == p
        else
          loop (i + 1)
    loop 0

partial def isPrimeInt (n : Int) (trial : Array Nat) : Bool :=
  if n < 2 then
    false
  else
    isPrimeNat n.toNat trial

partial def consecutivePrimeLength (a b : Int) (trial : Array Nat) : Nat :=
  let rec loop (n : Nat) : Nat :=
    let nI := (Int.ofNat n)
    let val := nI * nI + a * nI + b
    if isPrimeInt val trial then
      loop (n + 1)
    else
      n
  loop 0

partial def solve : Int :=
  let trial := sievePrimes 100000
  let bCandidates := (sievePrimes 1000).toList
  let rec loopB (bs : List Nat) (bestLen : Nat) (bestA bestB : Int) : Int :=
    match bs with
    | [] => bestA * bestB
    | bNat :: rest =>
        let b := Int.ofNat bNat
        let rec loopA (i : Nat) (bestLen : Nat) (bestA bestB : Int) : Nat × Int × Int :=
          if i > 1998 then
            (bestLen, bestA, bestB)
          else
            let a := (Int.ofNat i) - 999
            let parityOk :=
              if bNat != 2 then
                i % 2 == 0
              else
                i % 2 == 1
            if !parityOk then
              loopA (i + 1) bestLen bestA bestB
            else
              let quick := isPrimeInt (1 + a + b) trial
              if !quick then
                loopA (i + 1) bestLen bestA bestB
              else
                let len := consecutivePrimeLength a b trial
                if len > bestLen then
                  loopA (i + 1) len a b
                else
                  loopA (i + 1) bestLen bestA bestB
        let (bestLen', bestA', bestB') := loopA 0 bestLen bestA bestB
        loopB rest bestLen' bestA' bestB'
  loopB bCandidates 0 0 0



theorem equiv (n : Nat) : ProjectEulerStatements.P27.naive n n n = solve := sorry
end ProjectEulerSolutions.P27
open ProjectEulerSolutions.P27

def main : IO Unit := do
  IO.println solve
