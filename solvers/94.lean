import ProjectEulerStatements.P94
namespace ProjectEulerSolutions.P94

abbrev LIMIT : Nat := 1000000000

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

partial def triangleAreaIsosceles (a b : Nat) : Nat :=
  let d := 4 * a * a - b * b
  let k := sqrtFloor d
  if k * k != d then 0 else (b * k) / 4

partial def generatePerimeters (limit : Nat) : List Nat :=
  let rec loop (x y : Nat) (acc : List Nat) : List Nat :=
    let p :=
      if x % 3 == 2 then
        let a := (x + 1) / 3
        3 * a + 1
      else
        let a := (x - 1) / 3
        3 * a - 1
    if p > limit then
      acc.reverse
    else
      let acc := p :: acc
      let x' := 2 * x + 3 * y
      let y' := x + 2 * y
      loop x' y' acc
  loop 14 8 []

partial def sumPerimeters (limit : Nat) : Nat :=
  (generatePerimeters limit).foldl (fun acc p => acc + p) 0


example : triangleAreaIsosceles 5 6 = 12 := by
  native_decide

example : generatePerimeters 1000 = [16, 50, 196, 722] := by
  native_decide


def sol (_n : Nat) :=
  sumPerimeters LIMIT

theorem equiv (n : Nat) : ProjectEulerStatements.P94.naive n = sol n := sorry
end ProjectEulerSolutions.P94
open ProjectEulerSolutions.P94

def main : IO Unit := do
  IO.println (sol 0)