import ProjectEulerStatements.P85
namespace ProjectEulerSolutions.P85

abbrev TARGET : Nat := 2000000

partial def rectangleCount (m n : Nat) : Nat :=
  (m * (m + 1) * n * (n + 1)) / 4

partial def absDiff (a b : Nat) : Nat :=
  if a >= b then a - b else b - a

partial def bestGridAreaNear (target : Nat) : Nat :=
  let rec loopM (m : Nat) (bestDiff bestArea : Nat) : Nat :=
    if m >= 3000 then
      bestArea
    else
      let a := m * (m + 1) / 2
      let rec loopN (n : Nat) (bestDiff bestArea : Nat) : Nat × Nat :=
        if n >= 3000 then
          (bestDiff, bestArea)
        else
          let b := n * (n + 1) / 2
          let cnt := a * b
          let diff := absDiff cnt target
          let (bestDiff, bestArea) :=
            if diff < bestDiff then (diff, m * n) else (bestDiff, bestArea)
          loopN (n + 1) bestDiff bestArea
      let (bestDiff, bestArea) := loopN m bestDiff bestArea
      loopM (m + 1) bestDiff bestArea
  loopM 1 (Nat.pow 10 30) 0


example : rectangleCount 3 2 = 18 := by
  native_decide


def sol (_n : Nat) :=
  bestGridAreaNear TARGET

theorem equiv (n : Nat) : ProjectEulerStatements.P85.naive n n = sol n := sorry
end ProjectEulerSolutions.P85
open ProjectEulerSolutions.P85

def main : IO Unit := do
  IO.println (sol 0)