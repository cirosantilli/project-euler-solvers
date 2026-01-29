import ProjectEulerStatements.P30
namespace ProjectEulerSolutions.P30

abbrev fifth : Array Nat := #[0, 1, 32, 243, 1024, 3125, 7776, 16807, 32768, 59049]

partial def digitFifthPowerSum (n : Nat) : Nat :=
  let rec loop (m acc : Nat) : Nat :=
    if m == 0 then
      acc
    else
      let d := m % 10
      loop (m / 10) (acc + fifth[d]!)
  loop n 0

partial def matchesList : List Nat :=
  let upper := 6 * fifth[9]!
  let rec loop (n : Nat) (acc : List Nat) : List Nat :=
    if n > upper then
      acc.reverse
    else
      let acc' := if n == digitFifthPowerSum n then n :: acc else acc
      loop (n + 1) acc'
  loop 2 []


example : matchesList = [4150, 4151, 54748, 92727, 93084, 194979] := by
  native_decide


def sol (_n : Nat) :=
  matchesList.foldl (fun acc n => acc + n) 0

theorem equiv (n : Nat) : ProjectEulerStatements.P30.naive n n = sol n := sorry
end ProjectEulerSolutions.P30
open ProjectEulerSolutions.P30

def main : IO Unit := do
  IO.println (sol 0)