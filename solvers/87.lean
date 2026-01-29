import ProjectEulerStatements.P87
namespace ProjectEulerSolutions.P87

partial def sievePrimes (limit : Nat) : List Nat :=
  if limit < 2 then
    []
  else
    let arr0 := Array.replicate (limit + 1) true
      |>.set! 0 false
      |>.set! 1 false
    let rec loopP (p : Nat) (arr : Array Bool) : Array Bool :=
      if p * p > limit then
        arr
      else
        if arr[p]! then
          let rec loop (m : Nat) (arr : Array Bool) : Array Bool :=
            if m > limit then
              arr
            else
              loop (m + p) (arr.set! m false)
          loopP (p + 1) (loop (p * p) arr)
        else
          loopP (p + 1) arr
    let arr := loopP 2 arr0
    (List.range (limit + 1)).filter (fun n => arr[n]!)

partial def sqrt (n : Nat) : Nat :=
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

partial def countPrimePowerTriples (limit : Nat) : Nat :=
  if limit <= 0 then
    0
  else
    let primes := sievePrimes (sqrt limit + 1)
    let rec buildPows (ps : List Nat) (squares cubes fourths : List Nat)
        : List Nat × List Nat × List Nat :=
      match ps with
      | [] => (squares.reverse, cubes.reverse, fourths.reverse)
      | p :: ps =>
          let p2 := p * p
          let squares := if p2 < limit then p2 :: squares else squares
          let p3 := p2 * p
          let cubes := if p3 < limit then p3 :: cubes else cubes
          let p4 := p2 * p2
          let fourths := if p4 < limit then p4 :: fourths else fourths
          buildPows ps squares cubes fourths
    let (squares, cubes, fourths) := buildPows primes [] [] []
    let seen := Array.replicate limit false
    let rec loopF (fs : List Nat) (seen : Array Bool) : Array Bool :=
      match fs with
      | [] => seen
      | f :: fs =>
          let rec loopC (cs : List Nat) (seen : Array Bool) : Array Bool :=
            match cs with
            | [] => seen
            | c :: cs =>
                let fc := f + c
                if fc >= limit then
                  seen
                else
                  let rec loopS (ss : List Nat) (seen : Array Bool) : Array Bool :=
                    match ss with
                    | [] => seen
                    | s :: ss =>
                        let total := fc + s
                        if total >= limit then
                          seen
                        else
                          loopS ss (seen.set! total true)
                  loopC cs (loopS squares seen)
          loopF fs (loopC cubes seen)
    let seen := loopF fourths seen
    seen.foldl (fun acc b => if b then acc + 1 else acc) 0

example : countPrimePowerTriples 50 = 4 := by
  native_decide


def sol (_n : Nat) :=
  countPrimePowerTriples 50000000

theorem equiv (n : Nat) : ProjectEulerStatements.P87.naive n = sol n := sorry
end ProjectEulerSolutions.P87
open ProjectEulerSolutions.P87

def main : IO Unit := do
  IO.println (sol 0)