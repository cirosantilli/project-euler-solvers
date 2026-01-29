namespace ProjectEulerSolutions.P34

partial def precomputeFactorials : Array Nat :=
  let rec loop (d f : Nat) (arr : Array Nat) : Array Nat :=
    if d > 9 then
      arr
    else
      let f' := f * d
      loop (d + 1) f' (arr.set! d f')
  loop 1 1 (Array.replicate 10 1)

partial def digitFactorialSum (n : Nat) (facts : Array Nat) : Nat :=
  let rec loop (m acc : Nat) : Nat :=
    if m == 0 then
      acc
    else
      let d := m % 10
      loop (m / 10) (acc + facts[d]!)
  loop n 0

partial def solve : Nat :=
  let facts := precomputeFactorials
  let nineFact := facts[9]!
  let rec findN (n : Nat) : Nat :=
    if n * nineFact >= Nat.pow 10 (n - 1) then
      findN (n + 1)
    else
      n
  let n := findN 1
  let upper := (n - 1) * nineFact
  let rec loop (x total : Nat) : Nat :=
    if x > upper then
      total
    else
      let total' := if x == digitFactorialSum x facts then total + x else total
      loop (x + 1) total'
  loop 3 0


def sol : Nat :=
  solve

end ProjectEulerSolutions.P34
open ProjectEulerSolutions.P34

def main : IO Unit := do
  IO.println sol
