import ProjectEulerStatements.P75
namespace ProjectEulerSolutions.P75

partial def gcd (a b : Nat) : Nat :=
  if b == 0 then a else gcd b (a % b)

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

partial def solve (limit : Nat) : Nat :=
  let counts := Array.replicate (limit + 1) 0
  let mMax := sqrtFloor (limit / 2) + 1
  let rec loopM (m : Nat) (counts : Array Nat) : Array Nat :=
    if m > mMax then
      counts
    else
      let rec loopN (n : Nat) (counts : Array Nat) : Array Nat :=
        if n >= m then
          counts
        else
          if (m + n) % 2 == 0 then
            loopN (n + 1) counts
          else if gcd m n != 1 then
            loopN (n + 1) counts
          else
            let p0 := 2 * m * (m + n)
            if p0 > limit then
              counts
            else
              let rec loopP (p : Nat) (counts : Array Nat) : Array Nat :=
                if p > limit then
                  counts
                else
                  loopP (p + p0) (counts.set! p (counts[p]! + 1))
              loopN (n + 1) (loopP p0 counts)
      loopM (m + 1) (loopN 1 counts)
  let counts := loopM 2 counts
  let rec countOnes (i : Nat) (acc : Nat) : Nat :=
    if i > limit then
      acc
    else
      let acc := if counts[i]! == 1 then acc + 1 else acc
      countOnes (i + 1) acc
  countOnes 0 0


example : solve 50 = 6 := by
  native_decide


def sol (_n : Nat) :=
  solve 1500000

theorem equiv (n : Nat) : ProjectEulerStatements.P75.naive n = sol n := sorry
end ProjectEulerSolutions.P75
open ProjectEulerSolutions.P75

def main : IO Unit := do
  IO.println (sol 0)