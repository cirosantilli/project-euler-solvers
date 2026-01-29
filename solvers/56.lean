namespace ProjectEulerSolutions.P56

partial def digitSum (n : Nat) : Nat :=
  let s := toString n
  s.data.foldl (fun acc c => acc + (c.toNat - '0'.toNat)) 0

partial def maxDigitalSum (limit : Nat) : Nat × Nat × Nat :=
  let rec loopA (a : Nat) (best bestA bestB : Nat) : Nat × Nat × Nat :=
    if a >= limit then
      (best, bestA, bestB)
    else
      let rec loopB (b : Nat) (best bestA bestB : Nat) : Nat × Nat × Nat :=
        if b >= limit then
          loopA (a + 1) best bestA bestB
        else
          let s := digitSum (Nat.pow a b)
          if s > best then
            loopB (b + 1) s a b
          else
            loopB (b + 1) best bestA bestB
      loopB 1 best bestA bestB
  loopA 1 0 0 0


example : digitSum (Nat.pow 10 100) = 1 := by
  native_decide

example : digitSum (Nat.pow 2 15) = 26 := by
  native_decide


def sol (_n : Nat) :=
  (maxDigitalSum 100).1

end ProjectEulerSolutions.P56
open ProjectEulerSolutions.P56

def main : IO Unit := do
  IO.println (sol 0)