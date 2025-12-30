partial def sumEvenFibonacci (limit : Nat) : Nat :=
  let rec go (a b total : Nat) : Nat :=
    if a ≤ limit then
      let total' := if a % 2 = 0 then total + a else total
      go b (a + b) total'
    else
      total
  go 1 2 0

def main : IO Unit := do
  IO.println (sumEvenFibonacci 4000000)
