namespace ProjectEulerSolutions.P43

abbrev primes : List Nat := [2, 3, 5, 7, 11, 13, 17]

partial def distinct3 (a b c : Nat) : Bool :=
  a != b && a != c && b != c

partial def buildMap (p : Nat) : Array (List Nat) :=
  let arr0 := Array.replicate 100 ([] : List Nat)
  let rec loop (x : Nat) (arr : Array (List Nat)) : Array (List Nat) :=
    if x >= 1000 then
      arr
    else
      let a := x / 100
      let b := (x / 10) % 10
      let c := x % 10
      if distinct3 a b c then
        let idx := b * 10 + c
        loop (x + p) (arr.set! idx (a :: arr[idx]!))
      else
        loop (x + p) arr
  loop 0 arr0

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def isPandigitalSubstringProperty (n : Nat) : Bool :=
  let s := toString n
  if s.length != 10 then
    false
  else
    let digits := s.data.map (fun c => c.toNat - '0'.toNat)
    if digits.eraseDups.length != 10 then
      false
    else
      let rec loop (i : Nat) (ps : List Nat) : Bool :=
        match ps with
        | [] => true
        | p :: rest =>
            let a := getAt digits (i + 1)
            let b := getAt digits (i + 2)
            let c := getAt digits (i + 3)
            let v := 100 * a + 10 * b + c
            if v % p == 0 then loop (i + 1) rest else false
      loop 0 primes

partial def solve : Nat :=
  let rec initStates (x : Nat) (states : List (List Nat × Nat)) : List (List Nat × Nat) :=
    if x >= 1000 then
      states
    else
      let a := x / 100
      let b := (x / 10) % 10
      let c := x % 10
      if distinct3 a b c && x % 17 == 0 then
        let used := (1 <<< a) ||| (1 <<< b) ||| (1 <<< c)
        initStates (x + 17) ((([a, b, c], used)) :: states)
      else
        initStates (x + 17) states
  let states := initStates 0 []
  let rec extend (ps : List Nat) (states : List (List Nat × Nat)) : List (List Nat × Nat) :=
    match ps with
    | [] => states
    | p :: rest =>
        let mp := buildMap p
        let rec loopStates (ss : List (List Nat × Nat)) (acc : List (List Nat × Nat)) : List (List Nat × Nat) :=
          match ss with
          | [] => acc
          | (digits, used) :: ss =>
              match digits with
              | b :: c :: _ =>
                  let idx := b * 10 + c
                  let candidates := mp[idx]!
                  let rec loopCand (cs : List Nat) (acc : List (List Nat × Nat)) : List (List Nat × Nat) :=
                    match cs with
                    | [] => acc
                    | a :: cs =>
                        if (used &&& (1 <<< a)) != 0 then
                          loopCand cs acc
                        else
                          loopCand cs ((a :: digits, used ||| (1 <<< a)) :: acc)
                  loopStates ss (loopCand candidates acc)
              | _ =>
                  loopStates ss acc
        extend rest (loopStates states [])
  let states := extend [13, 11, 7, 5, 3, 2] states
  let allDigits := List.range 10
  let rec sumStates (ss : List (List Nat × Nat)) (total : Nat) : Nat :=
    match ss with
    | [] => total
    | (suffix, used) :: ss =>
        let remaining := allDigits.filter (fun d => (used &&& (1 <<< d)) == 0)
        let total :=
          if remaining.length == 1 then
            let d1 := remaining.head!
            if d1 == 0 then
              total
            else
              let num := suffix.foldl (fun acc d => acc * 10 + d) d1
              total + num
          else
            total
        sumStates ss total
  sumStates states 0


def sol : Nat :=
  solve

example : isPandigitalSubstringProperty 1406357289 = true := by
  native_decide

end ProjectEulerSolutions.P43
open ProjectEulerSolutions.P43

def main : IO Unit := do
  IO.println sol
