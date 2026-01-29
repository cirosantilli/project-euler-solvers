namespace ProjectEulerSolutions.P61

partial def polygonal (s n : Nat) : Nat :=
  match s with
  | 3 => n * (n + 1) / 2
  | 4 => n * n
  | 5 => n * (3 * n - 1) / 2
  | 6 => n * (2 * n - 1)
  | 7 => n * (5 * n - 3) / 2
  | 8 => n * (3 * n - 2)
  | _ => 0

partial def generate4DigitPolygonals (s : Nat) : List Nat :=
  let rec loop (n : Nat) (acc : List Nat) : List Nat :=
    let val := polygonal s n
    if val >= 10000 then
      acc.reverse
    else
      let acc :=
        if val >= 1000 && val <= 9999 && val % 100 >= 10 then
          val :: acc
        else
          acc
      loop (n + 1) acc
  loop 1 []

partial def buildPrefixMap (nums : List Nat) : Array (List Nat) :=
  nums.foldl (fun arr x =>
    let pref := x / 100
    let lst := arr[pref]!
    arr.set! pref (x :: lst)
  ) (Array.replicate 100 [])

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

partial def lastOr (xs : List (Nat × Nat)) (default : Nat × Nat) : Nat × Nat :=
  match xs.reverse with
  | [] => default
  | x :: _ => x

partial def findCycleSum : Nat :=
  let types : List Nat := [3,4,5,6,7,8]
  let numsByType :=
    types.foldl (fun arr t => arr.set! t (generate4DigitPolygonals t)) (Array.replicate 9 [])
  let prefMaps :=
    types.foldl (fun arr t => arr.set! t (buildPrefixMap (numsByType[t]!)))
      (Array.replicate 9 (Array.replicate 100 []))

  let rec dfs (path : List (Nat × Nat)) (usedTypes usedNums : List Nat) : Option (List (Nat × Nat)) :=
    if path.length == 6 then
      let lastNum := (lastOr path (0,0)).1
      let firstNum := (getAtPair path 0).1
      if lastNum % 100 == firstNum / 100 then some path else none
    else
      let suffix := (lastOr path (0,0)).1 % 100
      let rec loopTypes (ts : List Nat) : Option (List (Nat × Nat)) :=
        match ts with
        | [] => none
        | t :: ts =>
            if usedTypes.any (fun u => u == t) then
              loopTypes ts
            else
              let candidates := (prefMaps[t]!)[suffix]!
              let rec loopCand (cs : List Nat) : Option (List (Nat × Nat)) :=
                match cs with
                | [] => loopTypes ts
                | nxt :: cs =>
                    if usedNums.any (fun u => u == nxt) then
                      loopCand cs
                    else
                      match dfs (path ++ [(nxt, t)]) (t :: usedTypes) (nxt :: usedNums) with
                      | some res => some res
                      | none => loopCand cs
              loopCand candidates
      loopTypes types

  let starts := numsByType[8]!
  let rec loopStart (xs : List Nat) : Nat :=
    match xs with
    | [] => 0
    | s :: xs =>
        match dfs [(s, 8)] [8] [s] with
        | some res => res.foldl (fun acc p => acc + p.1) 0
        | none => loopStart xs
  loopStart starts


def sol : Nat :=
  findCycleSum

example : polygonal 3 127 = 8128 := by
  native_decide

example : polygonal 4 91 = 8281 := by
  native_decide

example : polygonal 5 44 = 2882 := by
  native_decide

end ProjectEulerSolutions.P61
open ProjectEulerSolutions.P61

def main : IO Unit := do
  IO.println sol
