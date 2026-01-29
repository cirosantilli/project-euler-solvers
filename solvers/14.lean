import ProjectEulerStatements.P14
namespace ProjectEulerSolutions.P14

partial def collatzNext (n : Nat) : Nat :=
  if n % 2 == 1 then 3 * n + 1 else n / 2

partial def collatzLength (n : Nat) : Nat :=
  if n == 1 then
    1
  else
    1 + collatzLength (collatzNext n)

partial def collatzLengthMemo (n limit : Nat) (cache : Array Nat) : Nat × Array Nat :=
  let rec loop (m : Nat) (path : List Nat) (cache : Array Nat) : Nat × Array Nat × List Nat :=
    if m <= limit then
      let cm := cache[m]!
      if cm != 0 then
        (cm, cache, path)
      else
        loop (collatzNext m) (m :: path) cache
    else
      loop (collatzNext m) (m :: path) cache
  let (len, cache1, path) := loop n [] cache
  let rec propagate (path : List Nat) (len : Nat) (cache : Array Nat) : Nat × Array Nat :=
    match path with
    | [] => (len, cache)
    | v :: vs =>
        let len' := len + 1
        let cache' := if v <= limit then cache.set! v len' else cache
        propagate vs len' cache'
  propagate path len cache1

partial def longestCollatzUnder (limit : Nat) : Nat × Nat :=
  let cache0 := (Array.replicate (limit + 1) 0).set! 1 1
  let rec loop (n bestN bestLen : Nat) (cache : Array Nat) : Nat × Nat :=
    if n >= limit then
      (bestN, bestLen)
    else
      let (len, cache') := collatzLengthMemo n limit cache
      let (bestN', bestLen') := if len > bestLen then (n, len) else (bestN, bestLen)
      loop (n + 1) bestN' bestLen' cache'
  loop 1 1 1 cache0


def sol (limit : Nat) : Nat :=
  (longestCollatzUnder limit).1

example : collatzLength 1 = 1 := by
  native_decide

example : collatzLength 13 = 10 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P14.naive n n = sol n := sorry
end ProjectEulerSolutions.P14
open ProjectEulerSolutions.P14

def main : IO Unit := do
  IO.println (sol 1000000)