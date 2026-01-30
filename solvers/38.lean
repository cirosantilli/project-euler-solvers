import ProjectEulerStatements.P38
namespace ProjectEulerSolutions.P38

abbrev targetMask : Nat := 1022

partial def concatenatedProduct (x : Nat) : String × Nat :=
  let rec loop (n totalLen : Nat) (acc : String) : String × Nat :=
    if totalLen >= 9 then
      (acc, n)
    else
      let n' := n + 1
      let s := toString (x * n')
      loop n' (totalLen + s.length) (acc ++ s)
  loop 0 0 ""

partial def isPandigital (s : String) : Bool :=
  if s.length != 9 then
    false
  else
    let rec loop (chars : List Char) (mask : Nat) : Bool :=
      match chars with
      | [] => mask == targetMask
      | c :: cs =>
          let d := c.toNat - '0'.toNat
          if d == 0 then false else
          let bit := 1 <<< d
          if (mask &&& bit) != 0 then false else loop cs (mask ||| bit)
    loop s.data 0

partial def solve : Nat :=
  let rec loop (x best : Nat) : Nat :=
    if x >= 10000 then
      best
    else
      let (s, n) := concatenatedProduct x
      if n > 1 && isPandigital s then
        let val := s.toNat!
        loop (x + 1) (if val > best then val else best)
      else
        loop (x + 1) best
  loop 1 0

partial def concatUpTo (x n : Nat) : String :=
  let rec loop (k : Nat) (acc : String) : String :=
    if k > n then acc else loop (k + 1) (acc ++ toString (x * k))
  loop 1 ""

example : concatUpTo 192 3 = "192384576" := by
  native_decide

example : isPandigital "192384576" = true := by
  native_decide

example : concatUpTo 9 5 = "918273645" := by
  native_decide

example : isPandigital "918273645" = true := by
  native_decide

theorem equiv (n : Nat) : ProjectEulerStatements.P38.naive n = solve := sorry
end ProjectEulerSolutions.P38
open ProjectEulerSolutions.P38

def main : IO Unit := do
  IO.println solve
