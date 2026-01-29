import ProjectEulerStatements.P90
namespace ProjectEulerSolutions.P90

abbrev squarePairs : List (Nat × Nat) :=
  [(0,1),(0,4),(0,9),(1,6),(2,5),(3,6),(4,9),(6,4),(8,1)]

partial def combinations (k : Nat) (xs : List Nat) : List (List Nat) :=
  if k == 0 then
    [[]]
  else
    match xs with
    | [] => []
    | x :: xs =>
        let withX := (combinations (k - 1) xs).map (fun ys => x :: ys)
        let withoutX := combinations k xs
        withX ++ withoutX

partial def expand6_9 (mask : Nat) : Nat :=
  let has6 := (mask / (Nat.pow 2 6)) % 2
  let has9 := (mask / (Nat.pow 2 9)) % 2
  if has6 == 1 || has9 == 1 then
    mask ||| (Nat.pow 2 6) ||| (Nat.pow 2 9)
  else
    mask

partial def canDisplayAllSquares (maskA maskB : Nat) : Bool :=
  let rec loop (ps : List (Nat × Nat)) : Bool :=
    match ps with
    | [] => true
    | (x, y) :: ps =>
        let bx := Nat.pow 2 x
        let bitY := Nat.pow 2 y
        if ((maskA &&& bx) != 0 && (maskB &&& bitY) != 0) || ((maskA &&& bitY) != 0 && (maskB &&& bx) != 0) then
          loop ps
        else
          false
  loop squarePairs

partial def solve : Nat :=
  let masks :=
    (combinations 6 (List.range 10)).map (fun comb =>
      comb.foldl (fun acc d => acc ||| Nat.pow 2 d) 0)
  let expanded := masks.map expand6_9
  let rec loopI (i : Nat) (count : Nat) : Nat :=
    if i >= masks.length then
      count
    else
      let rec loopJ (j : Nat) (count : Nat) : Nat :=
        if j >= masks.length then
          count
        else
          let count := if canDisplayAllSquares (expanded.getD i 0) (expanded.getD j 0) then count + 1 else count
          loopJ (j + 1) count
      loopI (i + 1) (loopJ i count)
  loopI 0 0



def sol (_n : Nat) :=
  solve

theorem equiv (n : Nat) : ProjectEulerStatements.P90.naive = sol n := sorry
end ProjectEulerSolutions.P90
open ProjectEulerSolutions.P90

def main : IO Unit := do
  IO.println (sol 0)