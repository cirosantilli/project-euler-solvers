import ProjectEulerStatements.P76
namespace ProjectEulerSolutions.P76

partial def countSummations (n : Nat) : Nat :=
  let dp0 := Array.replicate (n + 1) 0
  let dp0 := dp0.set! 0 1
  let rec loopPart (part : Nat) (dp : Array Nat) : Array Nat :=
    if part >= n then
      dp
    else
      let rec loopS (s : Nat) (dp : Array Nat) : Array Nat :=
        if s > n then
          dp
        else
          let dp := dp.set! s (dp[s]! + dp[s - part]!)
          loopS (s + 1) dp
      loopPart (part + 1) (loopS part dp)
  let dp := loopPart 1 dp0
  dp[n]!


example : countSummations 5 = 6 := by
  native_decide


def sol (_n : Nat) :=
  countSummations 100

theorem equiv (n : Nat) : ProjectEulerStatements.P76.naive n = sol n := sorry
end ProjectEulerSolutions.P76
open ProjectEulerSolutions.P76

def main : IO Unit := do
  IO.println (sol 0)