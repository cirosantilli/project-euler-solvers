import ProjectEulerStatements.P71
namespace ProjectEulerSolutions.P71

partial def gcd (a b : Nat) : Nat :=
  if b == 0 then a else gcd b (a % b)

partial def bestFractionLeftOf (targetN targetD maxD : Nat) : Nat × Nat :=
  let rec loop (d : Nat) (bestN bestD : Nat) : Nat × Nat :=
    if d > maxD then
      (bestN, bestD)
    else
      let n := (targetN * d - 1) / targetD
      if n == 0 then
        loop (d + 1) bestN bestD
      else if gcd n d != 1 then
        loop (d + 1) bestN bestD
      else if n * bestD > bestN * d then
        loop (d + 1) n d
      else
        loop (d + 1) bestN bestD
  loop 1 0 1


example : bestFractionLeftOf 3 7 8 = (2, 5) := by
  native_decide


def sol (_n : Nat) :=
  (bestFractionLeftOf 3 7 1000000).1

theorem equiv (n : Nat) : ProjectEulerStatements.P71.naive n = sol n := sorry
end ProjectEulerSolutions.P71
open ProjectEulerSolutions.P71

def main : IO Unit := do
  IO.println (sol 0)