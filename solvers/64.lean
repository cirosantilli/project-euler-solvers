namespace ProjectEulerSolutions.P64

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

partial def periodLengthSqrt (n : Nat) : Nat :=
  let a0 := sqrtFloor n
  if a0 * a0 == n then
    0
  else
    let rec loop (m d a period : Nat) : Nat :=
      let m := d * a - m
      let d := (n - m * m) / d
      let a := (a0 + m) / d
      let period := period + 1
      if a == 2 * a0 then period else loop m d a period
    loop 0 1 a0 0

partial def countOddPeriods (limit : Nat) : Nat :=
  let rec loop (n : Nat) (cnt : Nat) : Nat :=
    if n > limit then
      cnt
    else
      let r := sqrtFloor n
      if r * r == n then
        loop (n + 1) cnt
      else
        let cnt := if periodLengthSqrt n % 2 == 1 then cnt + 1 else cnt
        loop (n + 1) cnt
  loop 2 0


def sol : Nat :=
  countOddPeriods 10000

example : countOddPeriods 13 = 4 := by
  native_decide

end ProjectEulerSolutions.P64
open ProjectEulerSolutions.P64

def main : IO Unit := do
  IO.println sol
