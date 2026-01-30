import ProjectEulerStatements.P80
namespace ProjectEulerSolutions.P80

partial def sqrtFloor (n : Nat) : Nat :=
  let rec loop (lo hi : Nat) : Nat :=
    if lo > hi then
      hi
    else
      let mid := (lo + hi) / 2
      let sq := mid * mid
      if sq == n then
        mid
      else if sq < n then
        loop (mid + 1) hi
      else
        loop lo (mid - 1)
  loop 1 n

partial def isPerfectSquare (n : Nat) : Bool :=
  let r := sqrtFloor n
  r * r == n

partial def digitSumFirst100DigitsOfSqrt (n : Nat) : Nat :=
  let scale := Nat.pow 10 198
  let scaled := n * scale
  let rootScaled := sqrtFloor scaled
  let s := toString rootScaled
  s.data.foldl (fun acc c => acc + (c.toNat - '0'.toNat)) 0

partial def solve : Nat :=
  let rec loop (n : Nat) (total : Nat) : Nat :=
    if n > 100 then
      total
    else
      if isPerfectSquare n then
        loop (n + 1) total
      else
        loop (n + 1) (total + digitSumFirst100DigitsOfSqrt n)
  loop 1 0


example : digitSumFirst100DigitsOfSqrt 2 = 475 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P80.naive n n = solve := sorry
end ProjectEulerSolutions.P80
open ProjectEulerSolutions.P80

def main : IO Unit := do
  IO.println solve
