import Std
import ProjectEulerStatements.P82
namespace ProjectEulerSolutions.P82

partial def parseNat (s : String) : Nat :=
  s.data.foldl (fun acc c => acc * 10 + (c.toNat - '0'.toNat)) 0

partial def parseMatrix (text : String) : List (List Nat) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  lines.map (fun ln => ln.splitOn "," |>.filter (fun t => t != "") |>.map parseNat)

partial def minimalPathSumThreeWays (mat : List (List Nat)) : Nat :=
  let n := mat.length
  if n == 0 then
    0
  else
    let dp := (mat.map (fun row => row.headD 0)).toArray
    let rec loopCol (j : Nat) (dp : Array Nat) : Array Nat :=
      if j >= n then
        dp
      else
        let colVals := mat.map (fun row => row.getD j 0)
        let temp0 := (List.range n |>.map (fun i => dp[i]! + colVals.getD i 0)).toArray
        let rec relaxDown (i : Nat) (temp : Array Nat) : Array Nat :=
          if i >= n then temp
          else
            let cand := temp[i - 1]! + colVals.getD i 0
            let temp := if cand < temp[i]! then temp.set! i cand else temp
            relaxDown (i + 1) temp
        let temp1 := if n > 1 then relaxDown 1 temp0 else temp0
        let rec relaxUp (i : Nat) (temp : Array Nat) : Array Nat :=
          let cand := temp[i + 1]! + colVals.getD i 0
          let temp := if cand < temp[i]! then temp.set! i cand else temp
          if i == 0 then temp else relaxUp (i - 1) temp
        let temp2 := if n > 1 then relaxUp (n - 2) temp1 else temp1
        loopCol (j + 1) temp2
    let dp := loopCol 1 dp
    dp.foldl (fun acc v => if v < acc then v else acc) (dp[0]!)

example :
    let sample := [
      [131, 673, 234, 103, 18],
      [201, 96, 342, 965, 150],
      [630, 803, 746, 422, 111],
      [537, 699, 497, 121, 956],
      [805, 732, 524, 37, 331]
    ]
    minimalPathSumThreeWays sample = 994 := by
  native_decide



def solve (matrix : List (List Nat)) : Nat :=
  minimalPathSumThreeWays matrix

theorem equiv (matrix : List (List Nat)) : ProjectEulerStatements.P82.naive matrix = solve matrix := sorry
end ProjectEulerSolutions.P82
open ProjectEulerSolutions.P82

def main : IO Unit := do
  let text ← IO.FS.readFile "0082_matrix.txt"
  IO.println (solve (parseMatrix text))
