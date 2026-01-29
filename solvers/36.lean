namespace ProjectEulerSolutions.P36

partial def dropLastList (xs : List Char) : List Char :=
  match xs with
  | [] => []
  | [_] => []
  | x :: rest => x :: dropLastList rest

partial def generateDecimalPalindromes (limit : Nat) : List Nat :=
  let rec loop (i : Nat) (acc : List Nat) : List Nat :=
    if i >= 1000 then
      acc.reverse
    else
      let s := toString i
      let rev := String.mk s.data.reverse
      let oddStr := s ++ String.mk (dropLastList s.data |>.reverse)
      let evenStr := s ++ rev
      let odd := oddStr.toNat!
      let even := evenStr.toNat!
      let acc := if odd < limit then odd :: acc else acc
      let acc := if even < limit then even :: acc else acc
      loop (i + 1) acc
  loop 1 []

partial def isPalindromeBase2 (n : Nat) : Bool :=
  let rec bits (m : Nat) (acc : List Nat) : List Nat :=
    if m == 0 then acc else bits (m / 2) ((m % 2) :: acc)
  let b := bits n []
  b == b.reverse

partial def solve (limit : Nat) : Nat :=
  let pals := generateDecimalPalindromes limit
  let rec loop (lst : List Nat) (total : Nat) : Nat :=
    match lst with
    | [] => total
    | n :: ns =>
        if n % 2 == 0 then
          loop ns total
        else if isPalindromeBase2 n then
          loop ns (total + n)
        else
          loop ns total
  loop pals 0


def sol : Nat :=
  solve 1000000

example : isPalindromeBase2 585 = true := by
  native_decide

end ProjectEulerSolutions.P36
open ProjectEulerSolutions.P36

def main : IO Unit := do
  IO.println sol
