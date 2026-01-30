import ProjectEulerStatements.P21
namespace ProjectEulerSolutions.P21

partial def properDivisorSumsSieve (nMax : Nat) : Array Nat :=
  let rec loopI (i : Nat) (arr : Array Nat) : Array Nat :=
    if i > nMax / 2 then
      arr
    else
      let rec loopJ (j : Nat) (arr : Array Nat) : Array Nat :=
        if j > nMax then
          arr
        else
          loopJ (j + i) (arr.set! j (arr[j]! + i))
      loopI (i + 1) (loopJ (i * 2) arr)
  loopI 1 (Array.replicate (nMax + 1) 0)

partial def stripFactor (x p exp : Nat) : Nat × Nat :=
  if x % p == 0 then
    stripFactor (x / p) p (exp + 1)
  else
    (x, exp)

partial def properDivisorSumFactorization (n : Nat) : Nat :=
  if n <= 1 then
    0
  else
    let rec loop (x p sigma : Nat) : Nat :=
      if p * p > x then
        let sigma' := if x > 1 then sigma * (1 + x) else sigma
        sigma' - n
      else if x % p == 0 then
        let (x', exp) := stripFactor x p 0
        let term := (List.range (exp + 1)).foldl (fun acc k => acc + p ^ k) 0
        loop x' (p + 2) (sigma * term)
      else
        loop x (p + 2) sigma
    let (x2, exp2) := stripFactor n 2 0
    let sigma2 :=
      if exp2 == 0 then 1 else (List.range (exp2 + 1)).foldl (fun acc k => acc + 2 ^ k) 0
    loop x2 3 sigma2

partial def solve (limit : Nat) : Nat :=
  let divsum := properDivisorSumsSieve (limit - 1)
  let d := fun x => if x < divsum.size then divsum[x]! else properDivisorSumFactorization x
  let rec loop (a total : Nat) : Nat :=
    if a >= limit then
      total
    else
      let b := d a
      let total' := if b != a && d b == a then total + a else total
      loop (a + 1) total'
  loop 2 0

example : properDivisorSumFactorization 220 = 284 := by
  native_decide

example : properDivisorSumFactorization 284 = 220 := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P21.naive n = solve n := sorry
end ProjectEulerSolutions.P21
open ProjectEulerSolutions.P21

def main : IO Unit := do
  IO.println (solve 10000)
