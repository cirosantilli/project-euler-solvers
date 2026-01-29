import ProjectEulerStatements.P12
namespace ProjectEulerSolutions.P12

partial def stripFactor (x p exp : Nat) : Nat × Nat :=
  if x % p == 0 then
    stripFactor (x / p) p (exp + 1)
  else
    (x, exp)

partial def divisorCount (n : Nat) : Nat :=
  if n <= 1 then
    1
  else
    let rec loop (x i total : Nat) : Nat :=
      if i * i > x then
        if x > 1 then total * 2 else total
      else if x % i == 0 then
        let (x', exp) := stripFactor x i 0
        loop x' (i + 1) (total * (exp + 1))
      else
        loop x (i + 1) total
    loop n 2 1

partial def firstTriangularWithOver (k : Nat) : Nat :=
  let rec loop (n : Nat) : Nat :=
    let (a, b) :=
      if n % 2 == 0 then
        (n / 2, n + 1)
      else
        (n, (n + 1) / 2)
    let d := divisorCount a * divisorCount b
    if d > k then
      n * (n + 1) / 2
    else
      loop (n + 1)
  loop 1


def sol (k : Nat) : Nat :=
  firstTriangularWithOver k

example : sol 5 = 28 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P12.naive n n = sol n := sorry
end ProjectEulerSolutions.P12
open ProjectEulerSolutions.P12

def main : IO Unit := do
  IO.println (sol 500)