import Std
import ProjectEulerStatements.P98
namespace ProjectEulerSolutions.P98

partial def insertChar (x : Char) (xs : List Char) : List Char :=
  match xs with
  | [] => [x]
  | y :: ys => if x <= y then x :: y :: ys else y :: insertChar x ys

partial def sortChars (xs : List Char) : List Char :=
  xs.foldl (fun acc x => insertChar x acc) []

partial def sortedKey (s : String) : String :=
  String.mk (sortChars s.data)

partial def stripQuotes (s : String) : String :=
  match s.data with
  | '"' :: xs =>
      match xs.reverse with
      | '"' :: ys => String.mk ys.reverse
      | _ => s
  | _ => s

partial def parseWords (text : String) : List String :=
  let parts := text.splitOn "," |>.filter (fun t => t != "")
  parts.map (fun w => stripQuotes w.trim)

partial def patternSignature (s : String) : List Nat :=
  let rec loop (xs : List Char) (mp : List (Char × Nat)) (next : Nat) (acc : List Nat)
      : List Nat :=
    match xs with
    | [] => acc.reverse
    | x :: xs =>
        let rec find (mp : List (Char × Nat)) : Option Nat :=
          match mp with
          | [] => none
          | (c, v) :: ms => if c == x then some v else find ms
        match find mp with
        | some v => loop xs mp next (v :: acc)
        | none => loop xs ((x, next) :: mp) (next + 1) (next :: acc)
  loop s.data [] 0 []

partial def insertGroup (key : String) (val : String) (groups : List (String × List String))
    : List (String × List String) :=
  match groups with
  | [] => [(key, [val])]
  | (k, vs) :: gs => if k == key then (k, val :: vs) :: gs else (k, vs) :: insertGroup key val gs

partial def groupAnagrams (words : List String) : List (List String) :=
  let groups := words.foldl (fun acc w => insertGroup (sortedKey w) w acc) []
  groups.foldl (fun acc kv => if kv.2.length >= 2 then kv.2 :: acc else acc) []

partial def concatMap {α β : Type} (f : α -> List β) (xs : List α) : List β :=
  match xs with
  | [] => []
  | x :: xs => f x ++ concatMap f xs

partial def sqrtFloor (n : Nat) : Nat :=
  let rec loop (lo hi : Nat) : Nat :=
    if lo > hi then
      hi
    else
      let mid := (lo + hi) / 2
      let sq := mid * mid
      if sq == n then mid else if sq < n then loop (mid + 1) hi else loop lo (mid - 1)
  loop 1 n

partial def pow10 (n : Nat) : Nat :=
  let rec loop (k acc : Nat) : Nat :=
    if k == 0 then acc else loop (k - 1) (acc * 10)
  loop n 1

partial def insertPattern (pat : List Nat) (s : String)
    (groups : List (List Nat × List String)) : List (List Nat × List String) :=
  match groups with
  | [] => [(pat, [s])]
  | (p, vs) :: gs => if p == pat then (p, s :: vs) :: gs else (p, vs) :: insertPattern pat s gs

partial def squaresWithLength (L : Nat) : List (List Nat × List String) × List String :=
  let lo := pow10 (L - 1)
  let hi := pow10 L - 1
  let n0 := sqrtFloor lo
  let n0 := if n0 * n0 < lo then n0 + 1 else n0
  let n1 := sqrtFloor hi
  let rec loop (n : Nat) (groups : List (List Nat × List String)) (all : List String)
      : List (List Nat × List String) × List String :=
    if n > n1 then
      (groups, all)
    else
      let sq := n * n
      let s := toString sq
      let pat := patternSignature s
      loop (n + 1) (insertPattern pat s groups) (s :: all)
  loop n0 [] []

partial def findPattern (pat : List Nat) (groups : List (List Nat × List String)) : List String :=
  match groups with
  | [] => []
  | (p, vs) :: gs => if p == pat then vs else findPattern pat gs

partial def lookupChar (c : Char) (mp : List (Char × Char)) : Option Char :=
  match mp with
  | [] => none
  | (k, v) :: ms => if k == c then some v else lookupChar c ms

partial def solve (words : List String) : Nat :=
  let groups := groupAnagrams words
  let lengths := (concatMap (fun g => g.map (fun w => w.length)) groups).eraseDups
  let squaresCache := List.foldl (fun acc L =>
    let (byPat, asSet) := squaresWithLength L
    (L, (byPat, asSet)) :: acc) [] lengths
  let rec getSquares (L : Nat) (cache : List (Nat × (List (List Nat × List String) × List String)))
      : List (List Nat × List String) × List String :=
    match cache with
    | [] => ([], [])
    | (k, v) :: cs => if k == L then v else getSquares L cs
  let rec loopGroups (gs : List (List String)) (best : Nat) : Nat :=
    match gs with
    | [] => best
    | g :: gs =>
        let L := (g.headD "").length
        let (byPat, asSet) := getSquares L squaresCache
        let rec loopW (ws : List String) (best : Nat) : Nat :=
          match ws with
          | [] => best
          | w1 :: ws =>
              let pat := patternSignature w1
              let candidates := findPattern pat byPat
              let others := g.filter (fun w => w != w1)
              let rec loopSq (cs : List String) (best : Nat) : Nat :=
                match cs with
                | [] => best
                | sqStr :: cs =>
                    let rec buildMap (w : List Char) (s : List Char)
                        (mp : List (Char × Char)) (mp2 : List (Char × Char)) : Option (List (Char × Char)) :=
                      match w, s with
                      | [], [] => some mp
                      | c :: ws, d :: ds =>
                          match lookupChar c mp, lookupChar d mp2 with
                          | some d1, some c1 => if d1 == d && c1 == c then buildMap ws ds mp mp2 else none
                          | some d1, none => if d1 == d then buildMap ws ds mp ((d, c) :: mp2) else none
                          | none, some c1 => if c1 == c then buildMap ws ds ((c, d) :: mp) mp2 else none
                          | none, none => buildMap ws ds ((c, d) :: mp) ((d, c) :: mp2)
                      | _, _ => none
                    match buildMap w1.data sqStr.data [] [] with
                    | none => loopSq cs best
                    | some mp =>
                        let rec loopOther (os : List String) (best : Nat) : Nat :=
                          match os with
                          | [] => best
                          | w2 :: os =>
                              if lookupChar (w2.data.headD '0') mp == some '0' then
                                loopOther os best
                              else
                                let num2 :=
                                  w2.data.foldl (fun acc ch =>
                                    match lookupChar ch mp with
                                    | some d => acc ++ String.mk [d]
                                    | none => acc) ""
                                if asSet.any (fun s => s == num2) then
                                  let sq1 := sqStr.toNat!
                                  let sq2 := num2.toNat!
                                  let best := Nat.max best (Nat.max sq1 sq2)
                                  loopOther os best
                                else
                                  loopOther os best
                        loopSq cs (loopOther others best)
              loopW ws (loopSq candidates best)
        loopGroups gs (loopW g best)
  loopGroups groups 0



theorem equiv (words : List String) : ProjectEulerStatements.P98.naive words = solve words := sorry
end ProjectEulerSolutions.P98
open ProjectEulerSolutions.P98

def main : IO Unit := do
  let text ← IO.FS.readFile "0098_words.txt"
  IO.println (solve (parseWords text))
