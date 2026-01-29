import ProjectEulerStatements.P29
namespace ProjectEulerSolutions.P29

partial def countDistinctPowers (maxA maxB : Nat) : Nat :=
  let rec loopA (a : Nat) (vals : List Nat) : List Nat :=
    if a > maxA then
      vals
    else
      let rec loopB (b : Nat) (vals : List Nat) : List Nat :=
        if b > maxB then
          vals
        else
          let v := a ^ b
          let vals' := if vals.contains v then vals else v :: vals
          loopB (b + 1) vals'
      loopA (a + 1) (loopB 2 vals)
  (loopA 2 []).length


example : countDistinctPowers 5 5 = 15 := by
  native_decide


def sol (_n : Nat) : Nat :=
  countDistinctPowers 100 100

theorem equiv (n : Nat) : ProjectEulerStatements.P29.naive n n = sol n := sorry
end ProjectEulerSolutions.P29
open ProjectEulerSolutions.P29

def main : IO Unit := do
  IO.println (sol 0)
