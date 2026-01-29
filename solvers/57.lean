namespace ProjectEulerSolutions.P57

partial def countSqrt2Convergents (limit : Nat) : Nat :=
  let rec loop (i : Nat) (p q : Nat) (cnt : Nat) : Nat :=
    if i > limit then
      cnt
    else
      let cnt := if (toString p).length > (toString q).length then cnt + 1 else cnt
      loop (i + 1) (p + 2 * q) (p + q) cnt
  loop 1 3 2 0


def sol : Nat :=
  countSqrt2Convergents 1000

example : countSqrt2Convergents 7 = 0 := by
  native_decide

example : countSqrt2Convergents 8 = 1 := by
  native_decide

end ProjectEulerSolutions.P57
open ProjectEulerSolutions.P57

def main : IO Unit := do
  IO.println sol
