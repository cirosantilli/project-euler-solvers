import Std
import ProjectEulerStatements.P67
namespace ProjectEulerSolutions.P67

def parseNat (s : String) : Nat :=
  s.data.foldl (fun acc c => acc * 10 + (c.toNat - '0'.toNat)) 0

def parseTriangle (text : String) : List (List Nat) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  lines.map (fun ln => ln.splitOn " " |>.filter (fun t => t != "") |>.map parseNat)

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def maxPathSum (triangle : List (List Nat)) : Nat :=
  match triangle.reverse with
  | [] => 0
  | row :: rest =>
      let rec loopRows (rows : List (List Nat)) (dp : List Nat) : List Nat :=
        match rows with
        | [] => dp
        | r :: rs =>
            let rec loopRow (r : List Nat) (j : Nat) (acc : List Nat) : List Nat :=
              match r with
              | [] => acc.reverse
              | v :: vs =>
                  let best := Nat.max (getAt dp j) (getAt dp (j + 1))
                  loopRow vs (j + 1) ((v + best) :: acc)
            let dp := loopRow r 0 []
            loopRows rs dp
      let dp := loopRows rest row
      getAt dp 0

example :
    let sample := "3\n7 4\n2 4 6\n8 5 9 3"
    maxPathSum (parseTriangle sample) = 23 := by
  native_decide


def solve (triangle : List (List Nat)) : Nat :=
  maxPathSum triangle

theorem equiv (triangle : List (List Nat)) : ProjectEulerStatements.P67.naive triangle = solve triangle := sorry
end ProjectEulerSolutions.P67
open ProjectEulerSolutions.P67

def main : IO Unit := do
  let text ← IO.FS.readFile "0067_triangle.txt"
  IO.println (solve (parseTriangle text))
