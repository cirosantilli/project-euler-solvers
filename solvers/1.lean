import ProjectEulerStatements.P1

def sumOfMultiples (m n : Nat) : Nat :=
  let k := n / m
  (m * k * (k + 1)) / 2

def p1sol (n : Nat) : Nat :=
  let n' := n - 1
  sumOfMultiples 3 n' + sumOfMultiples 5 n' - sumOfMultiples 15 n'

example : p1sol 10 = 23 := rfl

theorem p1_10 : p1sol 10 = 23 := by native_decide
theorem p1 : p1sol 1000 = 233168 := by native_decide
theorem p1_equiv (n : Nat) : p1def n = p1sol n := by
  sorry

def main : IO Unit := do
  IO.println (p1sol 1000)
