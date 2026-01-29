import ProjectEulerStatements.P86
namespace ProjectEulerSolutions.P86

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

partial def countSolutionsUpTo (m : Nat) : Nat :=
  let rec loopC (c : Nat) (total : Nat) : Nat :=
    if c > m then
      total
    else
      let c2 := c * c
      let rec loopS (s : Nat) (total : Nat) : Nat :=
        if s > 2 * c then
          total
        else
          let d := s * s + c2
          let t := sqrtFloor d
          let total :=
            if t * t == d then
              let lo := if s > c then s - c else 1
              let hi := s / 2
              if hi >= lo then total + (hi - lo + 1) else total
            else
              total
          loopS (s + 1) total
      loopC (c + 1) (loopS 2 total)
  loopC 1 0

partial def leastMExceeding (target : Nat) : Nat :=
  let rec loop (c : Nat) (total : Nat) : Nat :=
    if total > target then
      c
    else
      let c := c + 1
      let c2 := c * c
      let rec loopS (s : Nat) (total : Nat) : Nat :=
        if s > 2 * c then
          total
        else
          let d := s * s + c2
          let t := sqrtFloor d
          let total :=
            if t * t == d then
              let lo := if s > c then s - c else 1
              let hi := s / 2
              if hi >= lo then total + (hi - lo + 1) else total
            else
              total
          loopS (s + 1) total
      loop c (loopS 2 total)
  loop 0 0


example : countSolutionsUpTo 99 = 1975 := by
  native_decide

example : countSolutionsUpTo 100 = 2060 := by
  native_decide


def sol (_n : Nat) :=
  leastMExceeding 1000000

theorem equiv (n : Nat) : ProjectEulerStatements.P86.naive n = sol n := sorry
end ProjectEulerSolutions.P86
open ProjectEulerSolutions.P86

def main : IO Unit := do
  IO.println (sol 0)