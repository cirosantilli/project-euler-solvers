namespace ProjectEulerSolutions.P39

partial def gcd (a b : Nat) : Nat :=
  if b == 0 then a else gcd b (a % b)

partial def maxSolutionsPerimeter (limit : Nat) : Nat :=
  let counts := Array.replicate (limit + 1) 0
  let rec loopM (m : Nat) (counts : Array Nat) : Array Nat :=
    if 2 * m * (m + 1) > limit then
      counts
    else
      let rec loopN (n : Nat) (counts : Array Nat) : Array Nat :=
        if n >= m then
          counts
        else
          if (m - n) % 2 == 0 || gcd m n != 1 then
            loopN (n + 1) counts
          else
            let p0 := 2 * m * (m + n)
            if p0 > limit then
              loopN (n + 1) counts
            else
              let rec loopK (k : Nat) (counts : Array Nat) : Array Nat :=
                if k * p0 > limit then
                  counts
                else
                  loopK (k + 1) (counts.set! (k * p0) (counts[k * p0]! + 1))
              loopN (n + 1) (loopK 1 counts)
      loopM (m + 1) (loopN 1 counts)
  let counts := loopM 2 counts
  let rec loopP (p bestP bestCount : Nat) : Nat :=
    if p > limit then
      bestP
    else
      let c := counts[p]!
      if c > bestCount then
        loopP (p + 1) p c
      else
        loopP (p + 1) bestP bestCount
  loopP 1 0 0

partial def countFor (limit pTarget : Nat) : Nat :=
  let counts := Array.replicate (limit + 1) 0
  let rec loopM (m : Nat) (counts : Array Nat) : Array Nat :=
    if 2 * m * (m + 1) > limit then
      counts
    else
      let rec loopN (n : Nat) (counts : Array Nat) : Array Nat :=
        if n >= m then
          counts
        else
          if (m - n) % 2 == 0 || gcd m n != 1 then
            loopN (n + 1) counts
          else
            let p0 := 2 * m * (m + n)
            if p0 > limit then
              loopN (n + 1) counts
            else
              let rec loopK (k : Nat) (counts : Array Nat) : Array Nat :=
                if k * p0 > limit then
                  counts
                else
                  loopK (k + 1) (counts.set! (k * p0) (counts[k * p0]! + 1))
              loopN (n + 1) (loopK 1 counts)
      loopM (m + 1) (loopN 1 counts)
  let counts := loopM 2 counts
  counts[pTarget]!


def sol : Nat :=
  maxSolutionsPerimeter 1000

example : countFor 1000 120 = 3 := by
  native_decide

end ProjectEulerSolutions.P39
open ProjectEulerSolutions.P39

def main : IO Unit := do
  IO.println sol
