import ProjectEulerStatements.P8
namespace ProjectEulerSolutions.P8

abbrev numberStr : String :=
  "73167176531330624919225119674426574742355349194934" ++
  "96983520312774506326239578318016984801869478851843" ++
  "85861560789112949495459501737958331952853208805511" ++
  "12540698747158523863050715693290963295227443043557" ++
  "66896648950445244523161731856403098711121722383113" ++
  "62229893423380308135336276614282806444486645238749" ++
  "30358907296290491560440772390713810515859307960866" ++
  "70172427121883998797908792274921901699720888093776" ++
  "65727333001053367881220235421809751254540594752243" ++
  "52584907711670556013604839586446706324415722155397" ++
  "53697817977846174064955149290862569321978468622482" ++
  "83972241375657056057490261407972968652414535100474" ++
  "82166370484403199890008895243450658541227588666881" ++
  "16427171479924442928230863465674813919123162824586" ++
  "17866458359124566529476545682848912883142607690042" ++
  "24219022671055626321111109370544217506941658960408" ++
  "07198403850962455444362981230987879927244284909188" ++
  "84580156166097919133875499200524063689912560717606" ++
  "05886116467109405077541002256983155200055935729725" ++
  "71636269561882670428252483600823257530420752963450"


def digitsArray (s : String) : Array Nat :=
  s.data.foldl (fun acc c => acc.push (c.toNat - '0'.toNat)) #[]

partial def prodRange (digits : Array Nat) (i len : Nat) : Nat :=
  if len == 0 then
    1
  else
    digits[i]! * prodRange digits (i + 1) (len - 1)

partial def maxAdjacentProduct (num : String) (k : Nat) : Nat :=
  let digits := digitsArray num
  let n := digits.size
  let rec findNextNonZero (i : Nat) : Nat :=
    if i < n && digits[i]! == 0 then
      findNextNonZero (i + 1)
    else
      i
  let rec findNextZero (i : Nat) : Nat :=
    if i < n && digits[i]! != 0 then
      findNextZero (i + 1)
    else
      i
  let rec slide (t j k : Nat) (prod best : Nat) : Nat :=
    if t >= j then
      best
    else
      let prod' := (prod / digits[t - k]!) * digits[t]!
      let best' := if prod' > best then prod' else best
      slide (t + 1) j k prod' best'
  let rec loop (i best : Nat) : Nat :=
    let i' := findNextNonZero i
    if i' >= n then
      best
    else
      let j := findNextZero i'
      let segLen := j - i'
      let best' :=
        if segLen >= k then
          let prod := prodRange digits i' k
          let best1 := if prod > best then prod else best
          slide (i' + k) j k prod best1
        else
          best
      loop j best'
  loop 0 0


def sol (k : Nat) : Nat :=
  maxAdjacentProduct numberStr k

example : sol 4 = 5832 := by
  native_decide


theorem equiv (n : Nat) : ProjectEulerStatements.P8.naive n = sol n := sorry
end ProjectEulerSolutions.P8
open ProjectEulerSolutions.P8

def main : IO Unit := do
  IO.println (sol 13)