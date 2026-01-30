import Std
import ProjectEulerStatements.P42
namespace ProjectEulerSolutions.P42

partial def triangleNumbers (n : Nat) : List Nat :=
  (List.range n).map (fun k => (k + 1) * (k + 2) / 2)

partial def sqrtIfSquare (n : Nat) : Nat :=
  let rec loop (i : Nat) : Nat :=
    if i * i > n then 0 else if i * i == n then i else loop (i + 1)
  loop 1

partial def isTriangle (x : Nat) : Bool :=
  if x == 0 then
    false
  else
    let d := 1 + 8 * x
    let s := sqrtIfSquare d
    s != 0 && (s - 1) % 2 == 0

partial def wordValue (w : String) : Nat :=
  w.data.foldl (fun acc c => if c >= 'A' && c <= 'Z' then acc + (c.toNat - 'A'.toNat + 1) else acc) 0

partial def stripQuotes (s : String) : String :=
  match s.data with
  | '"' :: xs =>
      match xs.reverse with
      | '"' :: ys => String.mk ys.reverse
      | _ => s
  | _ => s

partial def parseWords (s : String) : List String :=
  s.splitOn "," |>.filter (fun t => t != "") |>.map (fun t => stripQuotes t.trim)

partial def countTriangleWords (words : List String) : Nat :=
  words.foldl (fun acc w => if isTriangle (wordValue w) then acc + 1 else acc) 0

example : triangleNumbers 10 = [1,3,6,10,15,21,28,36,45,55] := by
  native_decide

example : wordValue "SKY" = 55 := by
  native_decide

example : isTriangle 55 = true := by
  native_decide


def solve (words : List String) : Nat :=
  countTriangleWords words

theorem equiv (words : List String) : ProjectEulerStatements.P42.naive words = solve words := sorry
end ProjectEulerSolutions.P42
open ProjectEulerSolutions.P42

def main : IO Unit := do
  let text ← IO.FS.readFile "0042_words.txt"
  IO.println (solve (parseWords text))
