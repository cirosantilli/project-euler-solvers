import ProjectEulerStatements.P73
namespace ProjectEulerSolutions.P73

partial def gcd (a b : Nat) : Nat :=
  if b == 0 then a else gcd b (a % b)

partial def countBetweenOneThirdAndOneHalf (limit : Nat) : Nat :=
  let rec loopD (d : Nat) (total : Nat) : Nat :=
    if d > limit then
      total
    else
      let nStart := d / 3 + 1
      let nEnd := (d - 1) / 2
      if nStart > nEnd then
        loopD (d + 1) total
      else
        let rec loopN (n : Nat) (cnt : Nat) : Nat :=
          if n > nEnd then
            cnt
          else
            let cnt := if gcd n d == 1 then cnt + 1 else cnt
            loopN (n + 1) cnt
        loopD (d + 1) (loopN nStart total)
  loopD 2 0


example : countBetweenOneThirdAndOneHalf 8 = 3 := by
  native_decide


def sol (_n : Nat) :=
  countBetweenOneThirdAndOneHalf 12000

theorem equiv (n : Nat) : ProjectEulerStatements.P73.naive n = sol n := sorry
end ProjectEulerSolutions.P73
open ProjectEulerSolutions.P73

def main : IO Unit := do
  IO.println (sol 0)