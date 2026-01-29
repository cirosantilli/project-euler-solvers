import ProjectEulerStatements.P17
namespace ProjectEulerSolutions.P17

abbrev ones : Array Nat := #[0, 3, 3, 5, 4, 4, 3, 5, 5, 4]
abbrev teens : Array Nat := #[3, 6, 6, 8, 8, 7, 7, 9, 8, 8]
abbrev tens : Array Nat := #[6, 6, 5, 5, 5, 7, 6, 6]

partial def letters1To99 (n : Nat) : Nat :=
  if n < 10 then
    ones[n]!
  else if n < 20 then
    teens[n - 10]!
  else
    let t := n / 10
    let u := n % 10
    tens[t - 2]! + ones[u]!

partial def lettersInNumber (n : Nat) : Nat :=
  if n == 1000 then
    3 + 8
  else if n < 100 then
    letters1To99 n
  else
    let h := n / 100
    let r := n % 100
    let base := ones[h]! + 7
    if r == 0 then base else base + 3 + letters1To99 r


example : (List.range 5).foldl (fun acc i => acc + lettersInNumber (i + 1)) 0 = 19 := by
  native_decide

example : lettersInNumber 342 = 23 := by
  native_decide

example : lettersInNumber 115 = 20 := by
  native_decide


def sol (_n : Nat) :=
  (List.range 1000).foldl (fun acc i => acc + lettersInNumber (i + 1)) 0

theorem equiv (n : Nat) : ProjectEulerStatements.P17.naive n = sol n := sorry
end ProjectEulerSolutions.P17
open ProjectEulerSolutions.P17

def main : IO Unit := do
  IO.println (sol 0)