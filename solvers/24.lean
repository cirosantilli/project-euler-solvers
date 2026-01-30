import ProjectEulerStatements.P24
namespace ProjectEulerSolutions.P24

partial def factorials (k : Nat) : Array Nat :=
  let rec loop (i acc : Nat) (arr : Array Nat) : Array Nat :=
    if i > k then
      arr
    else
      let acc' := acc * i
      loop (i + 1) acc' (arr.push acc')
  loop 1 1 #[1]

partial def popAt (idx : Nat) (xs : List Nat) : Nat × List Nat :=
  match xs, idx with
  | [], _ => (0, [])
  | x :: xs, 0 => (x, xs)
  | x :: xs, n + 1 =>
      let (y, rest) := popAt n xs
      (y, x :: rest)

partial def nthLexicographicPermutation (digits : List Nat) (n : Nat) : List Nat :=
  let k := digits.length
  let fact := factorials k
  let rec loop (i : Nat) (rank : Nat) (available : List Nat) (acc : List Nat) : List Nat :=
    if i == 0 then
      acc.reverse
    else
      let block := fact[i - 1]!
      let idx := rank / block
      let rank' := rank % block
      let (d, rest) := popAt idx available
      loop (i - 1) rank' rest (d :: acc)
  loop k (n - 1) digits []

def solve (digits : List Nat) (n : Nat) : List Nat :=
  nthLexicographicPermutation digits n

def serialize (ds : List Nat) : String :=
  String.mk (ds.map (fun d => Char.ofNat (d + 48)))

theorem equiv (digits : List Nat) (n : Nat) : (ProjectEulerStatements.P24.naive digits n) = (solve digits n) := sorry
end ProjectEulerSolutions.P24
open ProjectEulerSolutions.P24

def main : IO Unit := do
  IO.println (serialize (solve (List.range 10) 1000000))
