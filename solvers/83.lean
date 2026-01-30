import Std
import ProjectEulerStatements.P83
namespace ProjectEulerSolutions.P83

partial def parseNat (s : String) : Nat :=
  s.data.foldl (fun acc c => acc * 10 + (c.toNat - '0'.toNat)) 0

partial def parseMatrix (text : String) : List (List Nat) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  lines.map (fun ln => ln.splitOn "," |>.filter (fun t => t != "") |>.map parseNat)

partial def dijkstraMinPathSum (mat : List (List Nat)) : Nat :=
  let n := mat.length
  if n == 0 then
    0
  else
    let m := (mat.headD []).length
    let total := n * m
    let idx (r c : Nat) : Nat := r * m + c
    let inf := (Nat.pow 10 30)
    let dist0 := Array.replicate total inf
    let dist0 := dist0.set! 0 ((mat.headD []).headD 0)
    let visited0 := Array.replicate total false
    let rec loop (visited : Array Bool) (dist : Array Nat) (count : Nat) : Nat :=
      if count == total then
        dist[total - 1]!
      else
        let rec findMin (i : Nat) (bestI : Nat) (bestD : Nat) : Nat × Nat :=
          if i >= total then (bestI, bestD)
          else if visited[i]! then findMin (i + 1) bestI bestD
          else
            let d := dist[i]!
            if d < bestD then findMin (i + 1) i d else findMin (i + 1) bestI bestD
        let (u, du) := findMin 0 0 inf
        if du == inf then
          dist[total - 1]!
        else
          let visited := visited.set! u true
          let r := u / m
          let c := u % m
          let rec relax (r c : Int) (dist : Array Nat) : Array Nat :=
            if r < 0 || c < 0 || r >= (n : Int) || c >= (m : Int) then
              dist
            else
              let rr := Int.toNat r
              let cc := Int.toNat c
              let v := idx rr cc
              if visited[v]! then
                dist
              else
                let nd := du + (mat.getD rr []).getD cc 0
                if nd < dist[v]! then dist.set! v nd else dist
          let dist := relax (Int.ofNat r - 1) (Int.ofNat c) dist
          let dist := relax (Int.ofNat r + 1) (Int.ofNat c) dist
          let dist := relax (Int.ofNat r) (Int.ofNat c - 1) dist
          let dist := relax (Int.ofNat r) (Int.ofNat c + 1) dist
          loop visited dist (count + 1)
    loop visited0 dist0 0

example :
    let sample := [
      [131, 673, 234, 103, 18],
      [201, 96, 342, 965, 150],
      [630, 803, 746, 422, 111],
      [537, 699, 497, 121, 956],
      [805, 732, 524, 37, 331]
    ]
    dijkstraMinPathSum sample = 2297 := by
  native_decide



def solve (matrix : List (List Nat)) : Nat :=
  dijkstraMinPathSum matrix

theorem equiv (matrix : List (List Nat)) : ProjectEulerStatements.P83.naive matrix = solve matrix := sorry
end ProjectEulerSolutions.P83
open ProjectEulerSolutions.P83

def main : IO Unit := do
  let text ← IO.FS.readFile "0083_matrix.txt"
  IO.println (solve (parseMatrix text))
