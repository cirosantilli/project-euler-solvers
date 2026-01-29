import ProjectEulerStatements.P18
namespace ProjectEulerSolutions.P18

partial def combineRow (row dp : List Nat) : List Nat :=
  match row, dp with
  | [], _ => []
  | r :: rs, d1 :: d2 :: ds =>
      (r + (if d1 > d2 then d1 else d2)) :: combineRow rs (d2 :: ds)
  | _, _ => []

partial def maxPathSum (triangle : List (List Nat)) : Nat :=
  match triangle.reverse with
  | [] => 0
  | dp :: rows =>
      let final := rows.foldl (fun acc row => combineRow row acc) dp
      match final with
      | [x] => x
      | _ => 0

abbrev triangle : List (List Nat) := [
  [75],
  [95, 64],
  [17, 47, 82],
  [18, 35, 87, 10],
  [20, 4, 82, 47, 65],
  [19, 1, 23, 75, 3, 34],
  [88, 2, 77, 73, 7, 63, 67],
  [99, 65, 4, 28, 6, 16, 70, 92],
  [41, 41, 26, 56, 83, 40, 80, 70, 33],
  [41, 48, 72, 33, 47, 32, 37, 16, 94, 29],
  [53, 71, 44, 65, 25, 43, 91, 52, 97, 51, 14],
  [70, 11, 33, 28, 77, 73, 17, 78, 39, 68, 17, 57],
  [91, 71, 52, 38, 17, 14, 91, 43, 58, 50, 27, 29, 48],
  [63, 66, 4, 68, 89, 53, 67, 30, 73, 16, 69, 87, 40, 31],
  [4, 62, 98, 27, 23, 9, 70, 98, 73, 93, 38, 53, 60, 4, 23]
]


example : maxPathSum [[3], [7, 4], [2, 4, 6], [8, 5, 9, 3]] = 23 := by
  native_decide


def sol (_n : Nat) :=
  maxPathSum triangle

theorem equiv (n : Nat) : ProjectEulerStatements.P18.naive = sol n := sorry
end ProjectEulerSolutions.P18
open ProjectEulerSolutions.P18

def main : IO Unit := do
  IO.println (sol 0)