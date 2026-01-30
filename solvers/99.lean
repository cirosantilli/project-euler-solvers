import Std
import ProjectEulerStatements.P99
namespace ProjectEulerSolutions.P99

partial def parseNat (s : String) : Nat :=
  s.data.foldl (fun acc c => acc * 10 + (c.toNat - '0'.toNat)) 0

partial def parsePairs (text : String) : List (Nat × Nat) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  lines.map (fun ln =>
    let parts := ln.splitOn ","
    let b := parseNat (parts.getD 0 "0")
    let e := parseNat (parts.getD 1 "0")
    (b, e))

partial def bestLineNumber (pairs : List (Nat × Nat)) : Nat :=
  let rec loop (ps : List (Nat × Nat)) (idx bestIdx : Nat) (bestScore : Float) : Nat :=
    match ps with
    | [] => bestIdx
    | (b, e) :: ps =>
        let score := (Float.ofNat e) * (Float.log (Float.ofNat b))
        if score > bestScore then
          loop ps (idx + 1) idx score
        else
          loop ps (idx + 1) bestIdx bestScore
  loop pairs 1 0 (-1.0)


def solve (pairs : List (Nat × Nat)) : Nat :=
  bestLineNumber pairs

theorem equiv (pairs : List (Nat × Nat)) : ProjectEulerStatements.P99.naive pairs = solve pairs := sorry
end ProjectEulerSolutions.P99
open ProjectEulerSolutions.P99

def main : IO Unit := do
  let text ← IO.FS.readFile "0099_base_exp.txt"
  IO.println (solve (parsePairs text))
