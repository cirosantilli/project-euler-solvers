import ProjectEulerStatements.P84
namespace ProjectEulerSolutions.P84

abbrev CC_SQUARES : List Nat := [2, 17, 33]
abbrev CH_SQUARES : List Nat := [7, 22, 36]

abbrev G2J : Nat := 30
abbrev JAIL : Nat := 10

abbrev RAILWAYS : List Nat := [5, 15, 25, 35]
abbrev UTILITIES : List Nat := [12, 28]

partial def contains (xs : List Nat) (v : Nat) : Bool :=
  xs.any (fun x => x == v)

partial def nextRailway (pos : Nat) : Nat :=
  let rec loop (rs : List Nat) : Nat :=
    match rs with
    | [] => (RAILWAYS.headD 0)
    | r :: rs => if r > pos then r else loop rs
  loop RAILWAYS

partial def nextUtility (pos : Nat) : Nat :=
  let rec loop (rs : List Nat) : Nat :=
    match rs with
    | [] => (UTILITIES.headD 0)
    | r :: rs => if r > pos then r else loop rs
  loop UTILITIES

partial def diceOutcomes (sides : Nat) : List (Nat × Bool × Float) :=
  let p := 1.0 / (Float.ofNat (sides * sides))
  let rec loopD1 (d1 : Nat) (acc : List (Nat × Bool × Float)) : List (Nat × Bool × Float) :=
    if d1 > sides then
      acc.reverse
    else
      let rec loopD2 (d2 : Nat) (acc : List (Nat × Bool × Float)) : List (Nat × Bool × Float) :=
        if d2 > sides then
          acc
        else
          loopD2 (d2 + 1) ((d1 + d2, d1 == d2, p) :: acc)
      loopD1 (d1 + 1) (loopD2 1 acc)
  loopD1 1 []

partial def idxDist (sq : Nat) (sent : Bool) : Nat :=
  sq * 2 + (if sent then 1 else 0)

partial def addProb (arr : Array Float) (sq : Nat) (sent : Bool) (p : Float) : Array Float :=
  let i := idxDist sq sent
  arr.set! i (arr[i]! + p)

partial def mergeScaled (arr : Array Float) (other : Array Float) (scale : Float) : Array Float :=
  let rec loop (i : Nat) (arr : Array Float) : Array Float :=
    if i >= other.size then
      arr
    else
      let arr := arr.set! i (arr[i]! + other[i]! * scale)
      loop (i + 1) arr
  loop 0 arr

partial def resolveLanding (square : Nat) : Array Float :=
  if square == G2J then
    addProb (Array.replicate 80 0.0) JAIL true 1.0
  else if contains CC_SQUARES square then
    let dist := Array.replicate 80 0.0
    let dist := addProb dist square false (14.0 / 16.0)
    let dist := addProb dist 0 false (1.0 / 16.0)
    let dist := addProb dist JAIL true (1.0 / 16.0)
    dist
  else if contains CH_SQUARES square then
    let dist := Array.replicate 80 0.0
    let dist := addProb dist square false (6.0 / 16.0)
    let p := 1.0 / 16.0
    let rec addMove (dest : Nat) (dist : Array Float) : Array Float :=
      if contains CC_SQUARES dest || contains CH_SQUARES dest || dest == G2J then
        let sub := resolveLanding dest
        mergeScaled dist sub p
      else
        addProb dist dest false p
    let dist := addMove 0 dist
    let dist := addProb dist JAIL true p
    let dist := addMove 11 dist
    let dist := addMove 24 dist
    let dist := addMove 39 dist
    let dist := addMove 5 dist
    let dist := addMove (nextRailway square) dist
    let dist := addMove (nextRailway square) dist
    let dist := addMove (nextUtility square) dist
    let dist := addMove ((square + 40 - 3) % 40) dist
    dist
  else
    addProb (Array.replicate 80 0.0) square false 1.0

partial def buildTransition (sides : Nat) : List (List (Nat × Float)) :=
  let outcomes := diceOutcomes sides
  let nStates := 40 * 3
  let rec loopPos (pos : Nat) (acc : List (List (Nat × Float))) : List (List (Nat × Float)) :=
    if pos >= 40 then
      acc.reverse
    else
      let rec loopD (dc : Nat) (acc : List (List (Nat × Float))) : List (List (Nat × Float)) :=
        if dc >= 3 then
          acc
        else
          let row0 := Array.replicate nStates 0.0
          let rec loopOut (outs : List (Nat × Bool × Float)) (row : Array Float) : Array Float :=
            match outs with
            | [] => row
            | (move, isDouble, pr) :: outs =>
                if isDouble && dc == 2 then
                  let toState := JAIL * 3
                  let row := row.set! toState (row[toState]! + pr)
                  loopOut outs row
                else
                  let newDc := if isDouble then dc + 1 else 0
                  let nxt := (pos + move) % 40
                  let dist := resolveLanding nxt
                  let rec loopDist (i : Nat) (row : Array Float) : Array Float :=
                    if i >= dist.size then
                      row
                    else
                      let prob2 := dist[i]!
                      if prob2 == 0.0 then
                        loopDist (i + 1) row
                      else
                        let sq := i / 2
                        let sent := (i % 2 == 1)
                        let toState := if sent then JAIL * 3 else sq * 3 + newDc
                        let row := row.set! toState (row[toState]! + pr * prob2)
                        loopDist (i + 1) row
                  loopOut outs (loopDist 0 row)
          let row := loopOut outcomes row0
          let rec toList (i : Nat) (acc2 : List (Nat × Float)) : List (Nat × Float) :=
            if i >= nStates then
              acc2.reverse
            else
              let v := row[i]!
              if v == 0.0 then
                toList (i + 1) acc2
              else
                toList (i + 1) ((i, v) :: acc2)
          loopD (dc + 1) (toList 0 [] :: acc)
      loopPos (pos + 1) (loopD 0 acc)
  loopPos 0 []

partial def stationaryDistribution (P : List (List (Nat × Float))) : Array Float :=
  let n := P.length
  let v0 := Array.replicate n (1.0 / Float.ofNat n)
  let maxFloat (a b : Float) : Float := if a > b then a else b
  let rec loop (iter : Nat) (v : Array Float) : Array Float :=
    if iter > 5000 then
      v
    else
      let v2 := Array.replicate n 0.0
      let rec loopRows (i : Nat) (rows : List (List (Nat × Float))) (v2 : Array Float) : Array Float :=
        match rows with
        | [] => v2
        | row :: rows =>
            let vi := v[i]!
            let rec loopRow (r : List (Nat × Float)) (v2 : Array Float) : Array Float :=
              match r with
              | [] => v2
              | (j, p) :: rs => loopRow rs (v2.set! j (v2[j]! + vi * p))
            loopRows (i + 1) rows (loopRow row v2)
      let v2 := loopRows 0 P v2
      let rec maxDiff (i : Nat) (diff : Float) : Float :=
        if i >= n then diff else maxDiff (i + 1) (maxFloat diff (Float.abs (v2[i]! - v[i]!)))
      let diff := maxDiff 0 0.0
      if iter > 50 && diff < 1e-15 then
        v2
      else
        loop (iter + 1) v2
  let v := loop 1 v0
  let sum := v.foldl (fun acc x => acc + x) 0.0
  if sum == 0.0 then v else v.map (fun x => x / sum)

partial def sortByProb (xs : List (Nat × Float)) : List (Nat × Float) :=
  let rec insert (x : Nat × Float) (ys : List (Nat × Float)) : List (Nat × Float) :=
    match ys with
    | [] => [x]
    | y :: ys =>
        let (xi, xp) := x
        let (yi, yp) := y
        if xp > yp || (xp == yp && xi < yi) then
          x :: y :: ys
        else
          y :: insert x ys
  xs.foldl (fun acc x => insert x acc) []

partial def pad2 (n : Nat) : String :=
  if n < 10 then "0" ++ toString n else toString n

partial def modalString (sides : Nat) : String :=
  let P := buildTransition sides
  let v := stationaryDistribution P
  let sqProb := (List.range 40).map (fun pos =>
    let base := pos * 3
    let p := v[base]! + v[base + 1]! + v[base + 2]!
    (pos, p))
  let sorted := sortByProb sqProb
  let top3 := sorted.take 3
  top3.foldl (fun acc p => acc ++ pad2 p.1) ""


example : modalString 6 = "102400" := by
  native_decide


def sol (_n : Nat) :=
  (modalString 4).toNat!

theorem equiv (n : Nat) : ProjectEulerStatements.P84.naive n = sol n := sorry
end ProjectEulerSolutions.P84
open ProjectEulerSolutions.P84

def main : IO Unit := do
  IO.println (sol 0)
