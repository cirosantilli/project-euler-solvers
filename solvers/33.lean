import ProjectEulerStatements.P33
namespace ProjectEulerSolutions.P33

partial def findCuriousFractions : List (Nat × Nat) :=
  let rec loopN (n : Nat) (acc : List (Nat × Nat)) : List (Nat × Nat) :=
    if n > 99 then
      acc.reverse
    else
      let rec loopD (d : Nat) (acc : List (Nat × Nat)) : List (Nat × Nat) :=
        if d > 99 then
          acc
        else
          if n % 10 == 0 && d % 10 == 0 then
            loopD (d + 1) acc
          else
            let n10 := n / 10
            let n1 := n % 10
            let d10 := d / 10
            let d1 := d % 10
            let ok :=
              (n1 == d1 && n1 != 0 && d10 != 0 && n * d10 == d * n10) ||
              (n1 == d10 && n1 != 0 && d1 != 0 && n * d1 == d * n10) ||
              (n10 == d1 && n10 != 0 && d10 != 0 && n * d10 == d * n1) ||
              (n10 == d10 && n10 != 0 && d1 != 0 && n * d1 == d * n1)
            let acc := if ok then (n, d) :: acc else acc
            loopD (d + 1) acc
      loopN (n + 1) (loopD (n + 1) acc)
  loopN 10 []

partial def gcd (a b : Nat) : Nat :=
  if b == 0 then a else gcd b (a % b)

partial def reducedProductDenominator (fracs : List (Nat × Nat)) : Nat :=
  let rec loop (fs : List (Nat × Nat)) (num den : Nat) : Nat :=
    match fs with
    | [] =>
        let g := gcd num den
        den / g
    | (n, d) :: rest =>
        loop rest (num * n) (den * d)
  loop fracs 1 1

partial def listAll (xs : List (Nat × Nat)) (pred : (Nat × Nat) -> Bool) : Bool :=
  match xs with
  | [] => true
  | x :: rest => if pred x then listAll rest pred else false


example :
    let fracs := findCuriousFractions
    fracs.length == 4 := by
  native_decide

example :
    let fracs := findCuriousFractions
    let expected := [(16, 64), (19, 95), (26, 65), (49, 98)]
    listAll expected (fun p => fracs.contains p) := by
  native_decide


def sol (_n : Nat) :=
  let fracs := findCuriousFractions
  reducedProductDenominator fracs

theorem equiv (n : Nat) : ProjectEulerStatements.P33.naive = sol n := sorry
end ProjectEulerSolutions.P33
open ProjectEulerSolutions.P33

def main : IO Unit := do
  IO.println (sol 0)