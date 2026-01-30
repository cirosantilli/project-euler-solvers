import Std
namespace ProjectEulerSolutions.P54

def valueOf (c : Char) : Nat :=
  match c with
  | '2' => 2
  | '3' => 3
  | '4' => 4
  | '5' => 5
  | '6' => 6
  | '7' => 7
  | '8' => 8
  | '9' => 9
  | 'T' => 10
  | 'J' => 11
  | 'Q' => 12
  | 'K' => 13
  | 'A' => 14
  | _ => 0

def parseCard (token : String) : Nat × Char :=
  let rec getAtChar (xs : List Char) (i : Nat) : Char :=
    match xs, i with
    | [], _ => ' '
    | x :: _, 0 => x
    | _ :: xs, i + 1 => getAtChar xs i
  let cs := token.data
  let v := valueOf (getAtChar cs 0)
  let s := getAtChar cs 1
  (v, s)

partial def insertDesc (x : Nat) (xs : List Nat) : List Nat :=
  match xs with
  | [] => [x]
  | y :: ys => if x >= y then x :: y :: ys else y :: insertDesc x ys

partial def sortDesc (xs : List Nat) : List Nat :=
  xs.foldl (fun acc x => insertDesc x acc) []

partial def insertGroup (x : Nat × Nat) (xs : List (Nat × Nat)) : List (Nat × Nat) :=
  match xs with
  | [] => [x]
  | y :: ys =>
      let (c1,v1) := x
      let (c2,v2) := y
      if c1 > c2 || (c1 == c2 && v1 >= v2) then x :: y :: ys else y :: insertGroup x ys

partial def sortGroups (xs : List (Nat × Nat)) : List (Nat × Nat) :=
  xs.foldl (fun acc x => insertGroup x acc) []

partial def allEq (xs : List Char) : Bool :=
  match xs with
  | [] => true
  | x :: xs => xs.all (fun y => y == x)

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def getAtPair (xs : List (Nat × Nat)) (i : Nat) : Nat × Nat :=
  match xs, i with
  | [], _ => (0, 0)
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAtPair xs i

partial def dedupSortedAsc (xs : List Nat) : List Nat :=
  match xs with
  | [] => []
  | x :: xs =>
      let rec loop (prev : Nat) (rest : List Nat) (acc : List Nat) : List Nat :=
        match rest with
        | [] => (prev :: acc).reverse
        | y :: ys => if y == prev then loop prev ys acc else loop y ys (prev :: acc)
      loop x xs []

partial def handRank (cards : List String) : List Nat :=
  let valsSuits := cards.map parseCard
  let values := sortDesc (valsSuits.map Prod.fst)
  let suits := valsSuits.map Prod.snd
  let isFlush := allEq suits
  let valuesAsc := values.reverse
  let uniq := dedupSortedAsc valuesAsc
  let isStraight :=
    if uniq.length == 5 then
      let lo := getAt uniq 0
      let hi := getAt uniq 4
      if hi - lo == 4 then true else uniq == [2,3,4,5,14]
    else false
  let straightHigh := if uniq == [2,3,4,5,14] then 5 else (if uniq.length == 5 then getAt uniq 4 else 0)
  if isStraight && isFlush then
    [8, straightHigh]
  else
    let cntArr := values.foldl (fun acc v => acc.set! v (acc[v]! + 1)) (Array.replicate 15 0)
    let groups := sortGroups ((List.range 15).foldl (fun acc v => if cntArr[v]! > 0 then (cntArr[v]!, v) :: acc else acc) [])
    let g0 := getAtPair groups 0
    let g1 := getAtPair groups 1
    if g0.1 == 4 then
      let fourVal := g0.2
      let kicker := (values.filter (fun v => v != fourVal)).headD 0
      [7, fourVal, kicker]
    else if g0.1 == 3 && g1.1 == 2 then
      [6, g0.2, g1.2]
    else if isFlush then
      5 :: values
    else if isStraight then
      [4, straightHigh]
    else if g0.1 == 3 then
      let tripVal := g0.2
      let kickers := sortDesc (values.filter (fun v => v != tripVal))
      3 :: tripVal :: kickers
    else if g0.1 == 2 && g1.1 == 2 then
      let pairHigh := Nat.max g0.2 g1.2
      let pairLow := Nat.min g0.2 g1.2
      let kicker := (values.filter (fun v => v != pairHigh && v != pairLow)).headD 0
      [2, pairHigh, pairLow, kicker]
    else if g0.1 == 2 then
      let pairVal := g0.2
      let kickers := sortDesc (values.filter (fun v => v != pairVal))
      1 :: pairVal :: kickers
    else
      0 :: values

partial def lexGreater (a b : List Nat) : Bool :=
  match a, b with
  | [], [] => false
  | [], _ => false
  | _, [] => true
  | x :: xs, y :: ys => if x == y then lexGreater xs ys else x > y

def player1Wins (line : String) : Bool :=
  let parts := line.splitOn " " |>.filter (fun s => s != "")
  if parts.length != 10 then
    false
  else
    let h1 := parts.take 5
    let h2 := parts.drop 5
    lexGreater (handRank h1) (handRank h2)

def parseLines (s : String) : List String :=
  s.splitOn "\n" |>.filter (fun ln => ln != "")

def countWins (lines : List String) : Nat :=
  lines.foldl (fun acc ln => if player1Wins ln then acc + 1 else acc) 0

example : player1Wins "5H 5C 6S 7S KD 2C 3S 8S 8D TD" = false := by
  native_decide

example : player1Wins "5D 8C 9S JS AC 2C 5C 7D 8S QH" = true := by
  native_decide

example : player1Wins "2D 9C AS AH AC 3D 6D 7D TD QD" = false := by
  native_decide

example : player1Wins "4D 6S 9H QH QC 3D 6D 7H QD QS" = true := by
  native_decide

example : player1Wins "2H 2D 4C 4D 4S 3C 3D 3S 9S 9D" = true := by
  native_decide

example : lexGreater (handRank ["AS","2D","3H","4C","5S"]) (handRank ["KS","QD","9H","4C","3S"]) = true := by
  native_decide


def solve (lines : List String) : Nat :=
  countWins lines

end ProjectEulerSolutions.P54
open ProjectEulerSolutions.P54

def main : IO Unit := do
  let text ← IO.FS.readFile "0054_poker.txt"
  IO.println (solve (parseLines text))
