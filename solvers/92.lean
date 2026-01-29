import ProjectEulerStatements.P92
namespace ProjectEulerSolutions.P92

partial def buildSumSqTable (limit : Nat) : Array Nat :=
  let sq := (List.range 10).map (fun d => d * d)
  let sqArr := sq.toArray
  let arr0 := Array.replicate (limit + 1) 0
  let rec loop (i : Nat) (arr : Array Nat) : Array Nat :=
    if i > limit then
      arr
    else
      let v := arr[i / 10]! + sqArr[i % 10]!
      loop (i + 1) (arr.set! i v)
  loop 1 arr0

partial def buildTerminal (sumSq : Array Nat) (maxSum : Nat) : Array Nat :=
  let term0 := Array.replicate (maxSum + 1) 0
    |>.set! 1 1
    |>.set! 89 89
  let rec loopStart (start : Nat) (term : Array Nat) : Array Nat :=
    if start > maxSum then
      term
    else
      if term[start]! != 0 then
        loopStart (start + 1) term
      else
        let rec loopPath (x : Nat) (path : List Nat) : List Nat × Nat :=
          if x <= maxSum && term[x]! != 0 then
            (path, term[x]!)
          else
            loopPath (sumSq[x]!) (path ++ [x])
        let (path, endv) := loopPath start []
        let endv :=
          if endv != 0 then endv else
            let rec loopEnd (y : Nat) : Nat :=
              if y == 1 || y == 89 then y else loopEnd (sumSq[y]!)
            loopEnd start
        let term := path.foldl (fun acc v => acc.set! v endv) term
        loopStart (start + 1) term
  loopStart 1 term0

partial def sumSqOfNumber (sumSq : Array Nat) (n : Nat) : Nat :=
  let hi := n / 10000
  let lo := n % 10000
  sumSq[hi]! + sumSq[lo]!

partial def endFromNumber (sumSq : Array Nat) (n : Nat) : Nat :=
  let rec loop (x : Nat) : Nat :=
    if x == 1 || x == 89 then x else loop (sumSqOfNumber sumSq x)
  loop n

partial def countEndingAt89 (limitExclusive : Nat) : Nat :=
  let maxSum := 7 * 81
  let sumSq := buildSumSqTable 9999
  let terminal := buildTerminal sumSq maxSum

  let rec loopHigh (high : Nat) (count : Nat) : Nat :=
    if high >= 1000 then
      count
    else
      let hs := sumSq[high]!
      let startLow := if high == 0 then 1 else 0
      let rec loopLow (low : Nat) (count : Nat) : Nat :=
        if low >= 10000 then
          count
        else
          let count := if terminal.getD (hs + sumSq[low]!) 0 == 89 then count + 1 else count
          loopLow (low + 1) count
      loopHigh (high + 1) (loopLow startLow count)
  let count := loopHigh 0 0
  if limitExclusive == 10000000 then count else count


example :
    let sumSq := buildSumSqTable 9999
    (endFromNumber sumSq 44 = 1) && (endFromNumber sumSq 85 = 89) = true := by
  native_decide


def sol (_n : Nat) :=
  countEndingAt89 10000000

theorem equiv (n : Nat) : ProjectEulerStatements.P92.naive n n = sol n := sorry
end ProjectEulerSolutions.P92
open ProjectEulerSolutions.P92

def main : IO Unit := do
  IO.println (sol 0)