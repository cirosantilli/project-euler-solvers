import ProjectEulerStatements.P20
namespace ProjectEulerSolutions.P20

partial def digitSum (n : Nat) : Nat :=
  let s := toString n
  s.data.foldl (fun acc c => acc + (c.toNat - '0'.toNat)) 0

partial def solve (n : Nat) : Nat :=
  let rec loop (k acc : Nat) : Nat :=
    if k > n then
      digitSum acc
    else
      loop (k + 1) (acc * k)
  loop 2 1

example : solve 10 = 27 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P20.naive n = solve n := sorry
end ProjectEulerSolutions.P20
open ProjectEulerSolutions.P20

def main : IO Unit := do
  IO.println (solve 100)
