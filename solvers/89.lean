import Std
import ProjectEulerStatements.P89
namespace ProjectEulerSolutions.P89

def valueOf (c : Char) : Nat :=
  match c with
  | 'I' => 1
  | 'V' => 5
  | 'X' => 10
  | 'L' => 50
  | 'C' => 100
  | 'D' => 500
  | 'M' => 1000
  | _ => 0

partial def romanToInt (s : String) : Nat :=
  let rec loop (xs : List Char) (total : Nat) : Nat :=
    match xs with
    | [] => total
    | [x] => total + valueOf x
    | x :: y :: ys =>
        let v := valueOf x
        let v2 := valueOf y
        if v < v2 then
          loop ys (total + (v2 - v))
        else
          loop (y :: ys) (total + v)
  loop s.data 0

abbrev minimalTable : List (Nat × String) := [
  (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
  (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
]

partial def intToMinRoman (x : Nat) : String :=
  let rec loop (x : Nat) (tbl : List (Nat × String)) (acc : String) : String :=
    match tbl with
    | [] => acc
    | (val, sym) :: ts =>
        if x == 0 then acc
        else
          let k := x / val
          let x := x % val
          let rec rep (n : Nat) (acc : String) : String :=
            if n == 0 then acc else rep (n - 1) (acc ++ sym)
          loop x ts (rep k acc)
  loop x minimalTable ""

partial def totalCharactersSaved (lines : List String) : Nat :=
  lines.foldl (fun acc s =>
    let val := romanToInt s
    let minimal := intToMinRoman val
    acc + (s.length - minimal.length)
  ) 0

example : romanToInt "XVI" = 16 := by
  native_decide

example : intToMinRoman 16 = "XVI" := by
  native_decide

example : romanToInt "VIIII" = 9 := by
  native_decide

example : intToMinRoman 9 = "IX" := by
  native_decide

example : romanToInt "IIII" = 4 := by
  native_decide

example : intToMinRoman 4 = "IV" := by
  native_decide

example : romanToInt "MCMXC" = 1990 := by
  native_decide

example : intToMinRoman 1990 = "MCMXC" := by
  native_decide

example : romanToInt "MMMMCMXCIX" = 4999 := by
  native_decide

example : intToMinRoman 4999 = "MMMMCMXCIX" := by
  native_decide


def solve (lines : List String) : Nat :=
  totalCharactersSaved lines

theorem equiv (lines : List String) : ProjectEulerStatements.P89.naive lines = solve lines := sorry
end ProjectEulerSolutions.P89
open ProjectEulerSolutions.P89

def main : IO Unit := do
  let text ← IO.FS.readFile "0089_roman.txt"
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  IO.println (solve lines)
