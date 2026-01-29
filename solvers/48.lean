namespace ProjectEulerSolutions.P48

partial def powMod (a b mod : Nat) : Nat :=
  let rec loop (base exp acc : Nat) : Nat :=
    if exp == 0 then
      acc
    else
      let acc' := if exp % 2 == 1 then (acc * base) % mod else acc
      loop ((base * base) % mod) (exp / 2) acc'
  loop (a % mod) b 1

partial def lastKDigitsSelfPowers (n k : Nat) : String :=
  let mod := Nat.pow 10 k
  let rec loop (i s : Nat) : Nat :=
    if i > n then
      s
    else
      loop (i + 1) ((s + powMod i i mod) % mod)
  let s := loop 1 0
  let str := toString s
  let padLen := if str.length >= k then 0 else k - str.length
  let pad := String.mk (List.replicate padLen '0')
  pad ++ str

partial def exactSelfPowersSum (n : Nat) : Nat :=
  (List.range n).foldl (fun acc i => acc + Nat.pow (i + 1) (i + 1)) 0


def sol : String :=
  lastKDigitsSelfPowers 1000 10

example : exactSelfPowersSum 10 = 10405071317 := by
  native_decide

example : lastKDigitsSelfPowers 10 10 = "0405071317" := by
  native_decide

end ProjectEulerSolutions.P48
open ProjectEulerSolutions.P48

def main : IO Unit := do
  IO.println sol
