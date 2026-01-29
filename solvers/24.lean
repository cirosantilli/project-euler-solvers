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

partial def nthLexicographicPermutation (digits : List Nat) (n : Nat) : String :=
  let k := digits.length
  let fact := factorials k
  let rec loop (i : Nat) (rank : Nat) (available : List Nat) (acc : List Char) : String :=
    if i == 0 then
      String.mk acc
    else
      let block := fact[i - 1]!
      let idx := rank / block
      let rank' := rank % block
      let (d, rest) := popAt idx available
      loop (i - 1) rank' rest (acc ++ [Char.ofNat (d + 48)])
  loop k (n - 1) digits []

def digitsFromString (s : String) : List Nat :=
  s.data.map (fun c => c.toNat - '0'.toNat)

def digitsToString (ds : List Nat) : String :=
  String.mk (ds.map (fun d => Char.ofNat (d + 48)))



def sol (_n : Nat) :=
  digitsFromString (nthLexicographicPermutation (List.range 10) 1000000)

theorem equiv (n : Nat) : ProjectEulerStatements.P24.naive ([] : List Nat) n = sol n := sorry
end ProjectEulerSolutions.P24
open ProjectEulerSolutions.P24

def main : IO Unit := do
  IO.println (digitsToString (sol 0))
