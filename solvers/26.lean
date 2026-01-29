import ProjectEulerStatements.P26
namespace ProjectEulerSolutions.P26

partial def stripFactor (d p : Nat) : Nat :=
  if d % p == 0 then
    stripFactor (d / p) p
  else
    d

partial def recurringCycleLength (d0 : Nat) : Nat :=
  let d := stripFactor (stripFactor d0 2) 5
  if d == 1 then
    0
  else
    let rec loop (r k : Nat) : Nat :=
      if r == 1 then k else loop ((r * 10) % d) (k + 1)
    loop (10 % d) 1

partial def solve (limit : Nat) : Nat :=
  let rec loop (d bestD bestLen : Nat) : Nat :=
    if d >= limit then
      bestD
    else
      let len := recurringCycleLength d
      let (bestD', bestLen') := if len > bestLen then (d, len) else (bestD, bestLen)
      loop (d + 1) bestD' bestLen'
  loop 2 0 0


def sol (limit : Nat) : Nat :=
  solve limit

example : recurringCycleLength 2 = 0 := by native_decide
example : recurringCycleLength 3 = 1 := by native_decide
example : recurringCycleLength 4 = 0 := by native_decide
example : recurringCycleLength 5 = 0 := by native_decide
example : recurringCycleLength 6 = 1 := by native_decide
example : recurringCycleLength 7 = 6 := by native_decide
example : recurringCycleLength 8 = 0 := by native_decide
example : recurringCycleLength 9 = 1 := by native_decide
example : recurringCycleLength 10 = 0 := by native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P26.naive n = sol n := sorry
end ProjectEulerSolutions.P26
open ProjectEulerSolutions.P26

def main : IO Unit := do
  IO.println (sol 1000)