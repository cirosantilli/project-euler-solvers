namespace ProjectEulerSolutions.P53

partial def countCombinatoricSelections (limitN threshold : Nat) : Nat :=
  let rec loopN (n : Nat) (total : Nat) : Nat :=
    if n > limitN then
      total
    else
      let rec loopR (r : Nat) (c : Nat) (total : Nat) : Nat :=
        if r > n / 2 then
          loopN (n + 1) total
        else
          let c := c * (n - r + 1) / r
          if c > threshold then
            let total := total + (n - 2 * r + 1)
            loopN (n + 1) total
          else
            loopR (r + 1) c total
      loopR 1 1 total
  loopN 1 0



def sol (_n : Nat) :=
  countCombinatoricSelections 100 1000000

end ProjectEulerSolutions.P53
open ProjectEulerSolutions.P53

def main : IO Unit := do
  IO.println (sol 0)