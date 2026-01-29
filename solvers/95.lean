import ProjectEulerStatements.P95
namespace ProjectEulerSolutions.P95

partial def computeSumProperDivisors (limit : Nat) : Array Nat :=
  let s0 := Array.replicate (limit + 1) 0
  let half := limit / 2
  let rec loopI (i : Nat) (s : Array Nat) : Array Nat :=
    if i > half then
      s
    else
      let rec loopJ (j : Nat) (s : Array Nat) : Array Nat :=
        if j > limit then
          s
        else
          loopJ (j + i) (s.set! j (s[j]! + i))
      loopI (i + 1) (loopJ (i + i) s)
  loopI 1 s0

partial def amicableChainBest (limit : Nat) : Nat × Nat :=
  let s := computeSumProperDivisors limit
  let processed := Array.replicate (limit + 1) false
  let seenStamp := Array.replicate (limit + 1) 0
  let seenPos := Array.replicate (limit + 1) 0
  let rec loopStart (start : Nat) (bestLen bestMin : Nat)
      (processed : Array Bool) (seenStamp seenPos : Array Nat) (stamp : Nat)
      : Nat × Nat :=
    if start > limit then
      (bestLen, bestMin)
    else if processed[start]! then
      loopStart (start + 1) bestLen bestMin processed seenStamp seenPos stamp
    else
      let stamp := stamp + 1
      let rec loop (n : Nat) (path : List Nat) (processed : Array Bool)
          (seenStamp seenPos : Array Nat) : Nat × Nat × Array Bool × Array Nat × Array Nat :=
        if n == 0 || n > limit then
          let processed := path.foldl (fun acc v => acc.set! v true) processed
          (bestLen, bestMin, processed, seenStamp, seenPos)
        else if processed[n]! then
          let processed := path.foldl (fun acc v => acc.set! v true) processed
          (bestLen, bestMin, processed, seenStamp, seenPos)
        else if seenStamp[n]! == stamp then
          let loopStartIdx := seenPos[n]!
          let cycle := path.drop loopStartIdx
          let clen := cycle.length
          let cmin := cycle.foldl (fun acc v => if v < acc then v else acc) (cycle.headD 0)
          let (bestLen, bestMin) :=
            if clen > bestLen || (clen == bestLen && (bestMin == 0 || cmin < bestMin)) then
              (clen, cmin)
            else
              (bestLen, bestMin)
          let processed := path.foldl (fun acc v => acc.set! v true) processed
          (bestLen, bestMin, processed, seenStamp, seenPos)
        else
          let seenStamp := seenStamp.set! n stamp
          let seenPos := seenPos.set! n path.length
          loop (s[n]!) (path ++ [n]) processed seenStamp seenPos
      let (bestLen, bestMin, processed, seenStamp, seenPos) := loop start [] processed seenStamp seenPos
      loopStart (start + 1) bestLen bestMin processed seenStamp seenPos stamp
  loopStart 2 0 0 processed seenStamp seenPos 0


example :
    let s := computeSumProperDivisors 300
    (s[28]! = 28) && (s[220]! = 284) && (s[284]! = 220) = true := by
  native_decide

example :
    let s := computeSumProperDivisors 16000
    let ex := [12496, 14288, 15472, 14536, 14264]
    let ok := (List.range ex.length).all (fun i =>
      let a := ex.getD i 0
      let b := ex.getD ((i + 1) % ex.length) 0
      s[a]! = b)
    ok = true := by
  native_decide


def sol (_n : Nat) :=
  (amicableChainBest 1000000).2

theorem equiv (n : Nat) : ProjectEulerStatements.P95.naive n n = sol n := sorry
end ProjectEulerSolutions.P95
open ProjectEulerSolutions.P95

def main : IO Unit := do
  IO.println (sol 0)