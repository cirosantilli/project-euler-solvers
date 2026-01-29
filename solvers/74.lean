import ProjectEulerStatements.P74
namespace ProjectEulerSolutions.P74

abbrev FACT9 : Nat := 362880
abbrev LIMIT : Nat := 7 * FACT9

partial def buildFact : Array Nat :=
  let arr0 := Array.replicate 10 1
  let rec loop (i : Nat) (arr : Array Nat) : Array Nat :=
    if i >= 10 then
      arr
    else
      loop (i + 1) (arr.set! i (arr[i - 1]! * i))
  loop 2 arr0

partial def buildNext (limit : Nat) (fact : Array Nat) : Array Nat :=
  let arr0 := Array.replicate (limit + 1) 0
  let rec loop (i : Nat) (arr : Array Nat) : Array Nat :=
    if i > limit then
      arr
    else
      let val := arr[i / 10]! + fact[i % 10]!
      loop (i + 1) (arr.set! i val)
  loop 1 arr0

partial def chainLen (start : Nat)
    (nxt lens seenStamp seenPos : Array Nat) (stamp : Nat)
    : Nat × Array Nat × Array Nat × Array Nat × Nat :=
  if lens[start]! != 0 then
    (lens[start]!, lens, seenStamp, seenPos, stamp)
  else
    let stamp := stamp + 1
    let rec setLensFromEnd (seq : List Nat) (known : Nat) (lens : Array Nat) : Array Nat :=
      match seq.reverse with
      | [] => lens
      | xs =>
          let rec loop (xs : List Nat) (known : Nat) (lens : Array Nat) : Array Nat :=
            match xs with
            | [] => lens
            | v :: vs =>
                let known := known + 1
                let lens := lens.set! v known
                loop vs known lens
          loop xs known lens
    let rec setLensLoop (seq : List Nat) (loopStart loopLen len : Nat) (lens : Array Nat) : Array Nat :=
      let rec loop (xs : List Nat) (i : Nat) (lens : Array Nat) : Array Nat :=
        match xs with
        | [] => lens
        | v :: vs =>
            let lens :=
              if i >= loopStart then
                lens.set! v loopLen
              else
                lens.set! v (len - i)
            loop vs (i + 1) lens
      loop seq 0 lens
    let rec loop (cur : Nat) (seq : List Nat) (len : Nat)
        (lens seenStamp seenPos : Array Nat) : Nat × Array Nat × Array Nat × Array Nat :=
      if lens[cur]! != 0 then
        let known := lens[cur]!
        let lens := setLensFromEnd seq known lens
        (lens[start]!, lens, seenStamp, seenPos)
      else if seenStamp[cur]! == stamp then
        let loopStart := seenPos[cur]!
        let loopLen := len - loopStart
        let lens := setLensLoop seq loopStart loopLen len lens
        (lens[start]!, lens, seenStamp, seenPos)
      else
        let seenStamp := seenStamp.set! cur stamp
        let seenPos := seenPos.set! cur len
        loop (nxt[cur]!) (seq ++ [cur]) (len + 1) lens seenStamp seenPos
    let (len, lens, seenStamp, seenPos) := loop start [] 0 lens seenStamp seenPos
    (len, lens, seenStamp, seenPos, stamp)

partial def solve : Nat :=
  let fact := buildFact
  let nxt := buildNext LIMIT fact
  let lens := Array.replicate (LIMIT + 1) 0
  let seenStamp := Array.replicate (LIMIT + 1) 0
  let seenPos := Array.replicate (LIMIT + 1) 0
  let rec loopN (n : Nat) (count : Nat) (lens seenStamp seenPos : Array Nat) (stamp : Nat)
      : Nat :=
    if n >= 1000000 then
      count
    else
      let (len, lens, seenStamp, seenPos, stamp) :=
        if lens[n]! != 0 then
          (lens[n]!, lens, seenStamp, seenPos, stamp)
        else
          chainLen n nxt lens seenStamp seenPos stamp
      let count := if len == 60 then count + 1 else count
      loopN (n + 1) count lens seenStamp seenPos stamp
  loopN 1 0 lens seenStamp seenPos 0


partial def nextDigitFact (n : Nat) : Nat :=
  let fact := buildFact
  let rec loop (n : Nat) (acc : Nat) : Nat :=
    if n == 0 then acc else loop (n / 10) (acc + fact[n % 10]!)
  if n == 0 then fact[0]! else loop n 0

partial def chainLenSimple (start : Nat) : Nat :=
  let rec loop (cur : Nat) (seq : List Nat) : Nat :=
    if seq.any (fun x => x == cur) then
      seq.length
    else
      loop (nextDigitFact cur) (seq ++ [cur])
  loop start []

example : chainLenSimple 69 = 5 := by
  native_decide

example : chainLenSimple 78 = 4 := by
  native_decide

example : chainLenSimple 540 = 2 := by
  native_decide

example : chainLenSimple 169 = 3 := by
  native_decide


def sol (_n : Nat) :=
  solve

theorem equiv (n : Nat) : ProjectEulerStatements.P74.naive n n n = sol n := sorry
end ProjectEulerSolutions.P74
open ProjectEulerSolutions.P74

def main : IO Unit := do
  IO.println (sol 0)