import Std
namespace ProjectEulerSolutions.P59

def parseNat (s : String) : Nat :=
  s.data.foldl (fun acc c => acc * 10 + (c.toNat - '0'.toNat)) 0

def parseCipher (s : String) : List Nat :=
  s.splitOn "," |>.filter (fun t => t != "") |>.map parseNat

partial def setChars (arr : Array Int) (chars : List Char) (val : Int) : Array Int :=
  chars.foldl (fun a ch => a.set! ch.toNat val) arr

partial def buildScoringTables : Array Bool × Array Int :=
  let printable := Array.replicate 256 false
  let rec loopPrintable (v : Nat) (arr : Array Bool) : Array Bool :=
    if v > 126 then arr else loopPrintable (v + 1) (arr.set! v true)
  let printable := loopPrintable 32 printable
  let printable := printable.set! 10 true |>.set! 13 true
  let weights := Array.replicate 256 (0 : Int)
  let weights := weights.set! (' '.toNat) 10
  let freq : List (Char × Int) :=
    [('e',6),('t',5),('a',5),('o',5),('i',4),('n',4),('s',4),('h',4),('r',4),
     ('d',3),('l',3),('u',2),('c',2),('m',2),('w',2),('f',2),('g',2),('y',2),
     ('p',2),('b',1),('v',1),('k',1),('j',0),('x',0),('q',0),('z',0)]
  let weights := freq.foldl (fun a (ch, val) =>
    let a := a.set! ch.toNat val
    a.set! (Char.toUpper ch).toNat val
  ) weights
  let weights := setChars weights ['.',',',';',':','"','!','?','(',')','-'] 1
  let rec loopDigits (v : Nat) (a : Array Int) : Array Int :=
    if v > ('9'.toNat) then a else loopDigits (v + 1) (a.set! v 0)
  let weights := loopDigits ('0'.toNat) weights
  let weights := setChars weights ['{','}','[',']','|','^','~','`'] (-3)
  (printable, weights)

partial def scoreKey (cipher : List Nat) (k0 k1 k2 : Nat)
    (printable : Array Bool) (weights : Array Int) : Option (Int × Nat) :=
  let rec loop (i : Nat) (xs : List Nat) (score : Int) (sum : Nat) : Option (Int × Nat) :=
    match xs with
    | [] => some (score, sum)
    | c :: cs =>
        let key := if i % 3 == 0 then k0 else if i % 3 == 1 then k1 else k2
        let p := Nat.xor c key
        if printable[p]! then
          let score := score + weights[p]!
          loop (i + 1) cs score (sum + p)
        else
          none
  loop 0 cipher 0 0

partial def bestKeyAndSum (cipher : List Nat) : Nat :=
  let (printable, weights) := buildScoringTables
  let rec loopK0 (k0 : Nat) (bestScore : Int) (bestSum : Nat) : Nat :=
    if k0 > ('z'.toNat) then
      bestSum
    else
      let rec loopK1 (k1 : Nat) (bestScore : Int) (bestSum : Nat) : Int × Nat :=
        if k1 > ('z'.toNat) then
          (bestScore, bestSum)
        else
          let rec loopK2 (k2 : Nat) (bestScore : Int) (bestSum : Nat) : Int × Nat :=
            if k2 > ('z'.toNat) then
              (bestScore, bestSum)
            else
              match scoreKey cipher k0 k1 k2 printable weights with
              | none => loopK2 (k2 + 1) bestScore bestSum
              | some (score, s) =>
                  if score > bestScore then
                    loopK2 (k2 + 1) score s
                  else
                    loopK2 (k2 + 1) bestScore bestSum
          let (bestScore, bestSum) := loopK2 ('a'.toNat) bestScore bestSum
          loopK1 (k1 + 1) bestScore bestSum
      let (bestScore, bestSum) := loopK1 ('a'.toNat) bestScore bestSum
      loopK0 (k0 + 1) bestScore bestSum
  loopK0 ('a'.toNat) (-1000000000000000000) 0

example : Nat.xor 65 42 = 107 := by
  native_decide

example : Nat.xor 107 42 = 65 := by
  native_decide


def solve (cipher : List Nat) : Nat :=
  bestKeyAndSum cipher

end ProjectEulerSolutions.P59
open ProjectEulerSolutions.P59

def main : IO Unit := do
  let text ← IO.FS.readFile "0059_cipher.txt"
  IO.println (solve (parseCipher text))
