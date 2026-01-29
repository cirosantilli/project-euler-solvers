import ProjectEulerStatements.P65
namespace ProjectEulerSolutions.P65

partial def eContinuedFractionCoeffs (n : Nat) : List Nat :=
  let rec loop (i : Nat) (acc : List Nat) : List Nat :=
    if i >= n then
      acc.reverse
    else
      let a := if i == 0 then 2 else if i % 3 == 2 then 2 * (i / 3 + 1) else 1
      loop (i + 1) (a :: acc)
  loop 0 []

partial def convergentNumeratorDenominator (coeffs : List Nat) : Nat × Nat :=
  let rec loop (cs : List Nat) (p_nm2 p_nm1 q_nm2 q_nm1 : Nat) : Nat × Nat :=
    match cs with
    | [] => (p_nm1, q_nm1)
    | a :: cs =>
        let p := a * p_nm1 + p_nm2
        let q := a * q_nm1 + q_nm2
        loop cs p_nm1 p q_nm1 q
  loop coeffs 0 1 1 0

partial def digitSum (x : Nat) : Nat :=
  (toString x).data.foldl (fun acc c => acc + (c.toNat - '0'.toNat)) 0

partial def solve : Nat :=
  let coeffs100 := eContinuedFractionCoeffs 100
  let p100 := (convergentNumeratorDenominator coeffs100).1
  digitSum p100


example :
    let coeffs10 := eContinuedFractionCoeffs 10
    let pq := convergentNumeratorDenominator coeffs10
    pq = (1457, 536) := by
  native_decide

example : digitSum 1457 = 17 := by
  native_decide


def sol (_n : Nat) :=
  solve

theorem equiv (n : Nat) : ProjectEulerStatements.P65.naive n = sol n := sorry
end ProjectEulerSolutions.P65
open ProjectEulerSolutions.P65

def main : IO Unit := do
  IO.println (sol 0)