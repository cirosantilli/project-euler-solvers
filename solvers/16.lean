import ProjectEulerStatements.P16
namespace ProjectEulerSolutions.P16

partial def digitSum (n : Nat) : Nat :=
  let s := toString n
  s.data.foldl (fun acc c => acc + (c.toNat - '0'.toNat)) 0


example : digitSum (Nat.pow 2 15) = 26 := by
  native_decide


def sol (_n : Nat) :=
  digitSum (Nat.pow 2 1000)

theorem equiv (n : Nat) : ProjectEulerStatements.P16.naive n = sol n := sorry
end ProjectEulerSolutions.P16
open ProjectEulerSolutions.P16

def main : IO Unit := do
  IO.println (sol 0)