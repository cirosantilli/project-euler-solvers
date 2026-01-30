import Std
import ProjectEulerStatements.P22
namespace ProjectEulerSolutions.P22

def stripQuotes (s : String) : String :=
  match s.data with
  | '"' :: xs =>
      match xs.reverse with
      | '"' :: ys => String.mk ys.reverse
      | _ => s
  | _ => s

def parseNames (s : String) : List String :=
  s.splitOn "," |>.filter (fun t => t != "") |>.map (fun t => stripQuotes t.trim)

def nameValue (name : String) : Nat :=
  name.data.foldl (fun acc c => acc + (c.toNat - 'A'.toNat + 1)) 0

def merge (cmp : String -> String -> Bool) : List String -> List String -> List String
  | [], ys => ys
  | xs, [] => xs
  | x :: xs, y :: ys =>
      if cmp x y then x :: merge cmp xs (y :: ys) else y :: merge cmp (x :: xs) ys

def split (xs : List String) : List String × List String :=
  let rec loop (xs : List String) (a b : List String) : List String × List String :=
    match xs with
    | [] => (a.reverse, b.reverse)
    | [x] => ((x :: a).reverse, b.reverse)
    | x :: y :: rest => loop rest (x :: a) (y :: b)
  loop xs [] []

partial def mergeSort (cmp : String -> String -> Bool) (xs : List String) : List String :=
  match xs with
  | [] => []
  | [x] => [x]
  | _ =>
      let (a, b) := split xs
      merge cmp (mergeSort cmp a) (mergeSort cmp b)

def solve (names : List String) : Nat :=
  let namesSorted := mergeSort (fun a b => a < b) names
  let rec loop (lst : List String) (idx acc : Nat) : Nat :=
    match lst with
    | [] => acc
    | n :: ns => loop ns (idx + 1) (acc + idx * nameValue n)
  loop namesSorted 1 0

def colinPosScore (names : List String) : Nat × Nat :=
  let namesSorted := mergeSort (fun a b => a < b) names
  let rec find (lst : List String) (idx : Nat) : Nat :=
    match lst with
    | [] => 0
    | n :: ns => if n == "COLIN" then idx else find ns (idx + 1)
  let pos := find namesSorted 1
  (pos, pos * nameValue "COLIN")

example : colinPosScore (parseNames "\"COLIN\"") = (1, 53) := by
  native_decide

theorem equiv (names : List String) : ProjectEulerStatements.P22.naive names = solve names := sorry
end ProjectEulerSolutions.P22
open ProjectEulerSolutions.P22

def main : IO Unit := do
  let text ← IO.FS.readFile "0022_names.txt"
  IO.println (solve (parseNames text))
