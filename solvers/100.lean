import ProjectEulerStatements.P100
namespace ProjectEulerSolutions.P100

partial def nextSolution (u v : Nat) : Nat × Nat :=
  (3 * u + 4 * v, 2 * u + 3 * v)

partial def blueRedForTotalLimit (limitN : Nat) : Nat × Nat × Nat :=
  let rec loop (u v : Nat) : Nat × Nat × Nat :=
    let n := (u + 1) / 2
    let b := (v + 1) / 2
    if n > limitN then
      (b, n - b, n)
    else
      let (u, v) := nextSolution u v
      loop u v
  loop 1 1


example :
    let (u1, v1) := (1, 1)
    let (u2, v2) := nextSolution u1 v1
    let (u3, v3) := nextSolution u2 v2
    let (u4, v4) := nextSolution u3 v3
    let n3 := (u3 + 1) / 2
    let b3 := (v3 + 1) / 2
    let n4 := (u4 + 1) / 2
    let b4 := (v4 + 1) / 2
    (b3, n3) = (15, 21) && (b4, n4) = (85, 120) = true := by
  native_decide


def sol (_n : Nat) :=
  (blueRedForTotalLimit (Nat.pow 10 12)).1

theorem equiv (n : Nat) : ProjectEulerStatements.P100.naive n n = sol n := sorry
end ProjectEulerSolutions.P100
open ProjectEulerSolutions.P100

def main : IO Unit := do
  IO.println (sol 0)