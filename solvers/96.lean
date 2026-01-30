import Std
import ProjectEulerStatements.P96
namespace ProjectEulerSolutions.P96

partial def bit (d : Nat) : Nat :=
  Nat.pow 2 d

abbrev ALL : Nat := Nat.pow 2 9 - 1

partial def bitCount (n : Nat) : Nat :=
  if n == 0 then 0 else (n % 2) + bitCount (n / 2)

partial def bitToDigit (mask : Nat) : Nat :=
  let rec loop (d : Nat) : Nat :=
    if d >= 9 then 0
    else if mask == bit d then d + 1 else loop (d + 1)
  loop 0

partial def iterBits (mask : Nat) : List Nat :=
  let rec loop (d : Nat) (acc : List Nat) : List Nat :=
    if d >= 9 then acc.reverse
    else
      let acc := if (mask &&& bit d) != 0 then (bit d) :: acc else acc
      loop (d + 1) acc
  loop 0 []

partial def concatMap {α β : Type} (f : α -> List β) (xs : List α) : List β :=
  match xs with
  | [] => []
  | x :: xs => f x ++ concatMap f xs

partial def buildUnits : List (List Nat) :=
  let rows := (List.range 9).map (fun r => (List.range 9).map (fun c => r * 9 + c))
  let cols := (List.range 9).map (fun c => (List.range 9).map (fun r => r * 9 + c))
  let boxes :=
    concatMap (fun br =>
      (List.range 3).map (fun bc =>
        concatMap (fun r =>
          (List.range 3).map (fun c => (br * 3 + r) * 9 + (bc * 3 + c))) (List.range 3))) (List.range 3)
  rows ++ cols ++ boxes

partial def buildPeers : Array (List Nat) :=
  let units := buildUnits
  let rec loopCell (i : Nat) (acc : Array (List Nat)) : Array (List Nat) :=
    if i >= 81 then
      acc
    else
      let mask0 := Array.replicate 81 false
      let mask := units.foldl (fun m u =>
        if u.any (fun x => x == i) then
          u.foldl (fun m x => if x == i then m else m.set! x true) m
        else
          m) mask0
      let peers := (List.range 81).filter (fun j => mask[j]!)
      loopCell (i + 1) (acc.set! i peers)
  loopCell 0 (Array.replicate 81 [])

partial def reduceCands (cands : Array Nat) (peers : Array (List Nat)) (units : List (List Nat))
    : Option (Array Nat) :=
  let rec loopChanged (cands : Array Nat) : Option (Array Nat) :=
    let rec propagateSingles (queue : List Nat) (cands : Array Nat) : Option (Array Nat) :=
      match queue with
      | [] => some cands
      | i :: qs =>
          let val := cands[i]!
          let rec loopPeers (ps : List Nat) (cands : Array Nat) (queue : List Nat)
              : Option (Array Nat × List Nat) :=
            match ps with
            | [] => some (cands, queue)
            | p :: ps =>
                if (cands[p]! &&& val) != 0 then
                  let newMask := cands[p]! &&& (ALL - val)
                  if newMask == 0 then
                    none
                  else
                    let queue := if bitCount newMask == 1 then p :: queue else queue
                    loopPeers ps (cands.set! p newMask) queue
                else
                  loopPeers ps cands queue
          match loopPeers (peers[i]!) cands qs with
          | none => none
          | some (cands, queue) => propagateSingles queue cands

    let singles := (List.range 81).filter (fun i => bitCount (cands[i]!) == 1)
    match propagateSingles singles cands with
    | none => none
    | some cands =>
        let rec loopUnits (us : List (List Nat)) (cands : Array Nat) (changed : Bool)
            : Option (Array Nat × Bool) :=
          match us with
          | [] => some (cands, changed)
          | u :: us =>
              let rec loopBit (d : Nat) (cands : Array Nat) (changed : Bool)
                  : Option (Array Nat × Bool) :=
                if d >= 9 then
                  loopUnits us cands changed
                else
                  let b := bit d
                  let places := u.filter (fun i => (cands[i]! &&& b) != 0)
                  if places.isEmpty then
                    none
                  else if places.length == 1 then
                    let i := places.headD 0
                    if cands[i]! != b then
                      loopBit (d + 1) (cands.set! i b) true
                    else
                      loopBit (d + 1) cands changed
                  else
                    loopBit (d + 1) cands changed
              loopBit 0 cands changed
        match loopUnits units cands false with
        | none => none
        | some (cands, changed2) =>
            if changed2 then loopChanged cands else some cands
  loopChanged cands

partial def solveCands (cands : Array Nat) (peers : Array (List Nat)) (units : List (List Nat))
    : Option (Array Nat) :=
  match reduceCands cands peers units with
  | none => none
  | some cands =>
      if (List.range 81).all (fun i => bitCount (cands[i]!) == 1) then
        some cands
      else
        let rec findBest (i : Nat) (bestI bestC : Nat) : Nat × Nat :=
          if i >= 81 then (bestI, bestC)
          else
            let bc := bitCount (cands[i]!)
            if bc > 1 && bc < bestC then
              findBest (i + 1) i bc
            else
              findBest (i + 1) bestI bestC
        let (idx, _) := findBest 0 0 10
        let bits := iterBits (cands[idx]!)
        let rec tryBits (bs : List Nat) : Option (Array Nat) :=
          match bs with
          | [] => none
          | b :: bs =>
              let next := cands.set! idx b
              match solveCands next peers units with
              | some res => some res
              | none => tryBits bs
        tryBits bits

partial def getAtNat (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAtNat xs i

partial def gridToCands (grid : List (List Nat)) : Array Nat :=
  let rec loopR (r : Nat) (acc : Array Nat) : Array Nat :=
    if r >= 9 then
      acc
    else
      let row := (grid.getD r [])
      let rec loopC (c : Nat) (acc : Array Nat) : Array Nat :=
        if c >= 9 then
          acc
        else
          let val := getAtNat row c
          let idx := r * 9 + c
          let acc :=
            if val == 0 then acc.set! idx ALL
            else acc.set! idx (bit (val - 1))
          loopC (c + 1) acc
      loopR (r + 1) (loopC 0 acc)
  loopR 0 (Array.replicate 81 ALL)

partial def topLeftNumber (solve : Array Nat) : Nat :=
  let a := bitToDigit (solve[0]!)
  let b := bitToDigit (solve[1]!)
  let c := bitToDigit (solve[2]!)
  100 * a + 10 * b + c

partial def parseDigit (c : Char) : Nat :=
  if c >= '0' && c <= '9' then c.toNat - '0'.toNat else 0

partial def parseRow (row : String) : List Nat :=
  row.data.map parseDigit

partial def parsePuzzles (text : String) : List (List (List Nat)) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  let rec loop (ls : List String) (acc : List (List (List Nat))) : List (List (List Nat)) :=
    match ls with
    | [] => acc.reverse
    | l :: ls =>
        if l.startsWith "Grid" then
          let gridLines := ls.take 9
          let grid := gridLines.map parseRow
          loop (ls.drop 9) (grid :: acc)
        else
          loop ls acc
  loop lines []

partial def solve (puzzles : List (List (List Nat))) : Nat :=
  let peers := buildPeers
  let units := buildUnits
  let rec loop (ps : List (List (List Nat))) (acc : Nat) : Nat :=
    match ps with
    | [] => acc
    | g :: gs =>
        let cands := gridToCands g
        match solveCands cands peers units with
        | some solve => loop gs (acc + topLeftNumber solve)
        | none => loop gs acc
  loop puzzles 0



theorem equiv (grids : List (List (List Nat))) : ProjectEulerStatements.P96.naive grids = solve grids := sorry
end ProjectEulerSolutions.P96
open ProjectEulerSolutions.P96

def main : IO Unit := do
  let text ← IO.FS.readFile "0096_sudoku.txt"
  let puzzles := parsePuzzles text
  IO.println (solve puzzles)
