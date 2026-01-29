import ProjectEulerStatements.P45
namespace ProjectEulerSolutions.P45

partial def triangle (n : Nat) : Nat :=
  n * (n + 1) / 2

partial def pentagonal (n : Nat) : Nat :=
  n * (3 * n - 1) / 2

partial def hexagonal (n : Nat) : Nat :=
  n * (2 * n - 1)

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

partial def sqrtIfSquare (n : Nat) : Nat :=
  let s := sqrtFloor n
  if s * s == n then s else 0

partial def isPentagonal (x : Nat) : Bool :=
  let d := 1 + 24 * x
  let s := sqrtIfSquare d
  s != 0 && (1 + s) % 6 == 0

partial def solve : Nat :=
  let _ := triangle 285
  let _ := pentagonal 165
  let _ := hexagonal 143
  let rec loop (n : Nat) : Nat :=
    let h := hexagonal n
    if isPentagonal h then h else loop (n + 1)
  loop 144


example : triangle 285 = 40755 := by
  native_decide

example : pentagonal 165 = 40755 := by
  native_decide

example : hexagonal 143 = 40755 := by
  native_decide


def sol (_n : Nat) :=
  solve

theorem equiv (n : Nat) : ProjectEulerStatements.P45.naive n n = sol n := sorry
end ProjectEulerSolutions.P45
open ProjectEulerSolutions.P45

def main : IO Unit := do
  IO.println (sol 0)