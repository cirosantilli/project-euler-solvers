namespace ProjectEulerSolutions.P55

partial def reverseInt (n : Nat) : Nat :=
  let s := toString n
  let rs := String.mk s.data.reverse
  rs.toNat!

partial def isPalindrome (n : Nat) : Bool :=
  let s := toString n
  s == String.mk s.data.reverse

partial def isLychrelCandidate (n : Nat) (maxIters : Nat) : Bool :=
  let rec loop (x : Nat) (i : Nat) : Bool :=
    if i == maxIters then
      true
    else
      let x := x + reverseInt x
      if isPalindrome x then
        false
      else
        loop x (i + 1)
  loop n 0

partial def solve (limit : Nat) : Nat :=
  let rec loop (n : Nat) (acc : Nat) : Nat :=
    if n >= limit then
      acc
    else
      let acc := if isLychrelCandidate n 50 then acc + 1 else acc
      loop (n + 1) acc
  loop 1 0



def sol (_n : Nat) :=
  solve 10000

end ProjectEulerSolutions.P55
open ProjectEulerSolutions.P55

def main : IO Unit := do
  IO.println (sol 0)