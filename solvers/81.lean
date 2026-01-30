import Std
import ProjectEulerStatements.P81
namespace ProjectEulerSolutions.P81

partial def parseNat (s : String) : Nat :=
  s.data.foldl (fun acc c => acc * 10 + (c.toNat - '0'.toNat)) 0

partial def parseMatrix (text : String) : List (List Nat) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  lines.map (fun ln => ln.splitOn "," |>.filter (fun t => t != "") |>.map parseNat)

partial def minPathSum (matrix : List (List Nat)) : Nat :=
  match matrix with
  | [] => 0
  | row0 :: rows =>
      let m := row0.length
      let dp0 := Array.replicate m 0
      let dp0 := dp0.set! 0 (row0.headD 0)
      let rec initRow (j : Nat) (dp : Array Nat) : Array Nat :=
        if j >= m then dp
        else
          let val := dp[j - 1]! + (row0.getD j 0)
          initRow (j + 1) (dp.set! j val)
      let dp0 := if m > 1 then initRow 1 dp0 else dp0
      let rec loopRows (rows : List (List Nat)) (dp : Array Nat) : Array Nat :=
        match rows with
        | [] => dp
        | r :: rs =>
            let dp := dp.set! 0 (dp[0]! + r.headD 0)
            let rec loopCols (j : Nat) (dp : Array Nat) : Array Nat :=
              if j >= m then dp
              else
                let v := r.getD j 0
                let best := Nat.min dp[j]! dp[j - 1]!
                loopCols (j + 1) (dp.set! j (v + best))
            loopRows rs (loopCols 1 dp)
      let dp := loopRows rows dp0
      dp[m - 1]!

example :
    let sample := [
      [131, 673, 234, 103, 18],
      [201, 96, 342, 965, 150],
      [630, 803, 746, 422, 111],
      [537, 699, 497, 121, 956],
      [805, 732, 524, 37, 331]
    ]
    minPathSum sample = 2427 := by
  native_decide



def solve (matrix : List (List Nat)) : Nat :=
  minPathSum matrix

theorem equiv (matrix : List (List Nat)) : ProjectEulerStatements.P81.naive matrix = solve matrix := sorry
end ProjectEulerSolutions.P81
open ProjectEulerSolutions.P81

def main : IO Unit := do
  let text ← IO.FS.readFile "0081_matrix.txt"
  IO.println (solve (parseMatrix text))
