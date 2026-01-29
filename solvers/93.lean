import ProjectEulerStatements.P93
namespace ProjectEulerSolutions.P93

partial def insertRat (x : Rat) (xs : List Rat) : List Rat :=
  match xs with
  | [] => [x]
  | y :: ys => if x < y then x :: y :: ys else y :: insertRat x ys

partial def sortRat (xs : List Rat) : List Rat :=
  xs.foldl (fun acc x => insertRat x acc) []

partial def removeAt (xs : List Rat) (i : Nat) : List Rat :=
  match xs, i with
  | [], _ => []
  | _ :: ys, 0 => ys
  | x :: ys, i + 1 => x :: removeAt ys i

partial def getAt (xs : List Rat) (i : Nat) : Rat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def findMemo (key : List Rat) (memo : List (List Rat × List Rat)) : Option (List Rat) :=
  match memo with
  | [] => none
  | (k, v) :: rest => if k == key then some v else findMemo key rest

partial def allResults (digits : List Nat) : List Rat :=
  let start := sortRat (digits.map (fun d => Rat.ofInt (Int.ofNat d)))
  let rec recEval (state : List Rat) (memo : List (List Rat × List Rat)) : List Rat × List (List Rat × List Rat) :=
    match findMemo state memo with
    | some vals => (vals, memo)
    | none =>
        if state.length == 1 then
          let vals := state
          (vals, (state, vals) :: memo)
        else
          let m := state.length
          let rec loopI (i : Nat) (vals : List Rat) (memo : List (List Rat × List Rat)) : List Rat × List (List Rat × List Rat) :=
            if i >= m then
              let vals := vals.eraseDups
              (vals, (state, vals) :: memo)
            else
              let rec loopJ (j : Nat) (vals : List Rat) (memo : List (List Rat × List Rat)) : List Rat × List (List Rat × List Rat) :=
                if j >= m then
                  loopI (i + 1) vals memo
                else
                  let a := getAt state i
                  let b := getAt state j
                  let rest := removeAt (removeAt state j) i
                  let candidates := [a + b, a - b, b - a, a * b]
                  let candidates := if b != 0 then (a / b) :: candidates else candidates
                  let candidates := if a != 0 then (b / a) :: candidates else candidates
                  let rec loopC (cs : List Rat) (vals : List Rat) (memo : List (List Rat × List Rat))
                      : List Rat × List (List Rat × List Rat) :=
                    match cs with
                    | [] => (vals, memo)
                    | c :: cs =>
                        let newState := sortRat (c :: rest)
                        let (vals2, memo) := recEval newState memo
                        loopC cs (vals ++ vals2) memo
                  let (vals, memo) := loopC candidates vals memo
                  loopJ (j + 1) vals memo
              loopJ (i + 1) vals memo
          loopI 0 [] memo
  (recEval start []).1

partial def ratToNat? (r : Rat) : Option Nat :=
  if r.den == 1 && r.num >= 0 then
    some (Int.toNat r.num)
  else
    none

partial def consecutiveLength (digits : List Nat) : Nat × List Nat :=
  let vals := allResults digits
  let ints :=
    (vals.foldl (fun acc r =>
      match ratToNat? r with
      | some n => if n > 0 then n :: acc else acc
      | none => acc) []).eraseDups
  let rec loop (n : Nat) : Nat :=
    if ints.any (fun x => x == n) then loop (n + 1) else n - 1
  (loop 1, ints)

partial def listMax (xs : List Nat) : Nat :=
  match xs with
  | [] => 0
  | x :: xs => xs.foldl (fun acc v => if v > acc then v else acc) x

partial def combinations (k : Nat) (xs : List Nat) : List (List Nat) :=
  if k == 0 then
    [[]]
  else
    match xs with
    | [] => []
    | x :: xs =>
        let withX := (combinations (k - 1) xs).map (fun ys => x :: ys)
        let withoutX := combinations k xs
        withX ++ withoutX

partial def solve : String × Nat :=
  let rec loop (combs : List (List Nat)) (bestLen : Nat) (bestDigits : List Nat) : String × Nat :=
    match combs with
    | [] => ((bestDigits.map toString).foldl (fun acc s => acc ++ s) "", bestLen)
    | c :: cs =>
        let (len, _) := consecutiveLength c
        if len > bestLen then
          loop cs len c
        else
          loop cs bestLen bestDigits
  loop (combinations 4 (List.range 10)) 0 []


example :
    let (len, ints) := consecutiveLength [1,2,3,4]
    (len = 28) && (listMax ints = 36) = true := by
  native_decide


def sol (_n : Nat) :=
  (solve).1.toNat!

theorem equiv (n : Nat) : ProjectEulerStatements.P93.naive ([] : List Nat) = sol n := sorry
end ProjectEulerSolutions.P93
open ProjectEulerSolutions.P93

def main : IO Unit := do
  IO.println (sol 0)
