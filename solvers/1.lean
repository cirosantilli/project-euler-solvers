def sumOfMultiples (m n : Nat) : Nat :=
  let k := n / m
  (m * k * (k + 1)) / 2

def sumOfMultiplesOfEither3Or5 (n : Nat) : Nat :=
  let n' := n - 1
  sumOfMultiples 3 n' + sumOfMultiples 5 n' - sumOfMultiples 15 n'

example : sumOfMultiplesOfEither3Or5 10 = 23 := rfl

def main : IO Unit := do
  IO.println (sumOfMultiplesOfEither3Or5 1000)
