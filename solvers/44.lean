import ProjectEulerStatements.P44
namespace ProjectEulerSolutions.P44

def pentagonal (n : Nat) : Nat :=
  n * (3 * n - 1) / 2

partial def sqrtFloor (n : Nat) : Nat :=
  let rec loop (lo hi : Nat) : Nat :=
    if lo > hi then
      hi
    else
      let mid := (lo + hi) / 2
      let sq := mid * mid
      if sq == n then
        mid
      else if sq < n then
        loop (mid + 1) hi
      else
        loop lo (mid - 1)
  loop 1 n

def isPentagonal (x : Nat) : Bool :=
  if x == 0 then
    false
  else
    let t := 24 * x + 1
    let s := sqrtFloor t
    s * s == t && (1 + s) % 6 == 0

def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def findMinDifference (limit : Nat) : Nat :=
  let pent := (List.range (limit + 1)).map pentagonal
  let rec loopK (k : Nat) (best : Nat) : Nat :=
    if k > limit then
      best
    else
      let pk := getAt pent k
      let rec loopJ (j : Nat) (best : Nat) : Nat :=
        if j == 0 then
          best
        else
          let pj := getAt pent j
          let diff := pk - pj
          if diff >= best then
            best
          else if isPentagonal diff && isPentagonal (pk + pj) then
            diff
          else
            loopJ (j - 1) best
      loopK (k + 1) (loopJ (k - 1) best)
  loopK 2 (Nat.pow 10 30)


example :
    let first10 := [1,5,12,22,35,51,70,92,117,145]
    let ok := (List.range 10).all (fun i =>
      let v := getAt first10 i
      pentagonal (i + 1) == v && isPentagonal v)
    ok = true := by
  native_decide

example : pentagonal 4 + pentagonal 7 = pentagonal 8 := by
  native_decide

example : isPentagonal (pentagonal 7 - pentagonal 4) = false := by
  native_decide


def sol (_n : Nat) :=
  findMinDifference 10000

theorem equiv (n : Nat) : ProjectEulerStatements.P44.naive n = sol n := sorry
end ProjectEulerSolutions.P44
open ProjectEulerSolutions.P44

def main : IO Unit := do
  let ans := sol 0
  IO.println ans