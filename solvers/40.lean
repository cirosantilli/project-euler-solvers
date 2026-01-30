import ProjectEulerStatements.P40
namespace ProjectEulerSolutions.P40

partial def digitAt (n : Nat) : Nat :=
  let rec loop (n : Nat) (length start count : Nat) : Nat :=
    let blockDigits := count * length
    if n > blockDigits then
      loop (n - blockDigits) (length + 1) (start * 10) (count * 10)
    else
      let idx := (n - 1) / length
      let pos := (n - 1) % length
      let num := start + idx
      let s := toString num
      let ch := s.data[pos]!
      ch.toNat - '0'.toNat
  loop n 1 1 9

partial def solve : Nat :=
  let positions := [1, 10, 100, 1000, 10000, 100000, 1000000]
  positions.foldl (fun acc p => acc * digitAt p) 1


example : digitAt 12 = 1 := by
  native_decide

example : digitAt 1 = 1 := by
  native_decide

example : digitAt 10 = 1 := by
  native_decide

example : digitAt 100 = 5 := by
  native_decide

example : digitAt 1000 = 3 := by
  native_decide

example : digitAt 10000 = 7 := by
  native_decide

example : digitAt 100000 = 2 := by
  native_decide

example : digitAt 1000000 = 1 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P40.naive n = solve := sorry
end ProjectEulerSolutions.P40
open ProjectEulerSolutions.P40

def main : IO Unit := do
  IO.println solve
