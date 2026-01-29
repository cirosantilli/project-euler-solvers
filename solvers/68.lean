import ProjectEulerStatements.P68
namespace ProjectEulerSolutions.P68

partial def insertAsc (x : Nat) (xs : List Nat) : List Nat :=
  match xs with
  | [] => [x]
  | y :: ys => if x <= y then x :: y :: ys else y :: insertAsc x ys

partial def sortAsc (xs : List Nat) : List Nat :=
  xs.foldl (fun acc x => insertAsc x acc) []

partial def allDistinctSorted (xs : List Nat) : Bool :=
  match xs with
  | [] => true
  | [_] => true
  | x :: y :: ys => if x == y then false else allDistinctSorted (y :: ys)

partial def listContains (xs : List Nat) (v : Nat) : Bool :=
  xs.any (fun x => x == v)

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

partial def permutations (xs : List Nat) : List (List Nat) :=
  match xs with
  | [] => [[]]
  | _ =>
      let rec concatMap (f : List Nat -> List (List Nat)) (ls : List (List Nat)) : List (List Nat) :=
        match ls with
        | [] => []
        | x :: xs => f x ++ concatMap f xs
      let rec insertAll (x : Nat) (ys : List Nat) : List (List Nat) :=
        match ys with
        | [] => [[x]]
        | y :: ys =>
            let head := (x :: y :: ys)
            let rest := insertAll x ys
            head :: rest.map (fun tail => y :: tail)
      let rec loop (xs : List Nat) : List (List Nat) :=
        match xs with
        | [] => [[]]
        | x :: xs =>
            concatMap (insertAll x) (loop xs)
      loop xs

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def minIndex (xs : List Nat) : Nat :=
  let rec loop (xs : List Nat) (idx bestIdx bestVal : Nat) : Nat :=
    match xs with
    | [] => bestIdx
    | x :: xs =>
        if x < bestVal then
          loop xs (idx + 1) idx x
        else
          loop xs (idx + 1) bestIdx bestVal
  match xs with
  | [] => 0
  | x :: xs => loop xs 1 0 x

partial def concatStrings (xs : List String) : String :=
  xs.foldl (fun acc s => acc ++ s) ""

partial def magic5GonMax16Digit : String :=
  let nums := (List.range 10).map (fun k => k + 1)
  let innerCandidates := combinations 5 ((List.range 9).map (fun k => k + 1))
  let rec loopInner (inners : List (List Nat)) (best : String) : String :=
    match inners with
    | [] => best
    | innerSet :: rest =>
        let innerSum := innerSet.foldl (fun acc x => acc + x) 0
        if (55 + innerSum) % 5 != 0 then
          loopInner rest best
        else
          let s := (55 + innerSum) / 5
          let remainingOuter := nums.filter (fun n => !listContains innerSet n)
          if listContains remainingOuter 10 == false then
            loopInner rest best
          else
            let perms := permutations innerSet
            let rec loopPerm (ps : List (List Nat)) (best : String) : String :=
              match ps with
              | [] => loopInner rest best
              | inner :: ps =>
                  let rec loopK (k : Nat) (outer : List Nat) : Option (List Nat) :=
                    if k == 5 then
                      some outer.reverse
                    else
                      let a := getAt inner k
                      let b := getAt inner ((k + 1) % 5)
                      if s < a + b then
                        none
                      else
                        let o := s - a - b
                        if o == 0 || o > 10 then
                          none
                        else
                          loopK (k + 1) (o :: outer)
                  match loopK 0 [] with
                  | none => loopPerm ps best
                  | some outer =>
                      let outerSorted := sortAsc outer
                      let remSorted := sortAsc remainingOuter
                      if outerSorted != remSorted || allDistinctSorted outerSorted == false then
                        loopPerm ps best
                      else
                        let start := minIndex outer
                        let parts := (List.range 5).map (fun t =>
                          let idx := (start + t) % 5
                          let a := getAt outer idx
                          let b := getAt inner idx
                          let c := getAt inner ((idx + 1) % 5)
                          toString a ++ toString b ++ toString c)
                        let str := concatStrings parts
                        if str.length == 16 && str > best then
                          loopPerm ps str
                        else
                          loopPerm ps best
            loopPerm perms best
  loopInner innerCandidates ""



def sol (_n : Nat) :=
  magic5GonMax16Digit.toNat!

theorem equiv (n : Nat) : ProjectEulerStatements.P68.naive = sol n := sorry
end ProjectEulerSolutions.P68
open ProjectEulerSolutions.P68

def main : IO Unit := do
  IO.println (sol 0)
