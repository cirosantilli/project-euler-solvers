import ProjectEulerStatements.P97
namespace ProjectEulerSolutions.P97

partial def powMod (a e mod : Nat) : Nat :=
  let rec loop (base exp acc : Nat) : Nat :=
    if exp == 0 then
      acc
    else
      let acc := if exp % 2 == 1 then (acc * base) % mod else acc
      loop ((base * base) % mod) (exp / 2) acc
  if mod == 1 then 0 else loop (a % mod) e 1

partial def lastTenDigits : Nat :=
  let mod := Nat.pow 10 10
  (28433 * powMod 2 7830457 mod + 1) % mod



def sol (_n : Nat) :=
  lastTenDigits

theorem equiv (n : Nat) : ProjectEulerStatements.P97.naive = sol n := sorry
end ProjectEulerSolutions.P97
open ProjectEulerSolutions.P97

def main : IO Unit := do
  IO.println (sol 0)