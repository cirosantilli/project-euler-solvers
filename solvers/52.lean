namespace ProjectEulerSolutions.P52

partial def digitSignature (n : Nat) : Array Nat :=
  let rec loop (n : Nat) (acc : Array Nat) : Array Nat :=
    if n == 0 then
      acc
    else
      let d := n % 10
      loop (n / 10) (acc.set! d (acc[d]! + 1))
  if n == 0 then
    Array.replicate 10 0
  else
    loop n (Array.replicate 10 0)

partial def smallestPermutedMultiple (limitMul : Nat) : Nat :=
  let rec loopDigits (d : Nat) : Nat :=
    let lo := Nat.pow 10 (d - 1)
    let hi := (Nat.pow 10 d - 1) / limitMul
    let rec loopX (x : Nat) : Nat :=
      if x > hi then
        loopDigits (d + 1)
      else
        let sig := digitSignature x
        let rec loopM (m : Nat) : Bool :=
          if m > limitMul then
            true
          else
            if digitSignature (m * x) == sig then
              loopM (m + 1)
            else
              false
        if loopM 2 then
          x
        else
          loopX (x + 1)
    loopX lo
  loopDigits 1



def sol (_n : Nat) :=
  smallestPermutedMultiple 6

end ProjectEulerSolutions.P52
open ProjectEulerSolutions.P52

def main : IO Unit := do
  IO.println (sol 0)