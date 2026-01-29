namespace ProjectEulerSolutions.P51

partial def sieveIsPrime (limit : Nat) : Array Bool :=
  if limit == 0 then
    #[]
  else
    let arr0 := (Array.replicate (limit + 1) true)
      |>.set! 0 false
      |>.set! 1 false
    let rec loopP (p : Nat) (arr : Array Bool) : Array Bool :=
      if p * p > limit then
        arr
      else
        if arr[p]! then
          let rec loop (m : Nat) (arr : Array Bool) : Array Bool :=
            if m > limit then
              arr
            else
              loop (m + p) (arr.set! m false)
          loopP (p + 1) (loop (p * p) arr)
        else
          loopP (p + 1) arr
    loopP 2 arr0

partial def primesUpTo (limit : Nat) : List Nat :=
  let isPrime := sieveIsPrime limit
  (List.range (limit + 1)).filter (fun n => isPrime[n]!)

partial def digits (n : Nat) : List Nat :=
  let s := toString n
  s.data.map (fun c => c.toNat - '0'.toNat)

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def pow10At (n i : Nat) : Nat :=
  Nat.pow 10 (n - 1 - i)

partial def bitCount (n : Nat) : Nat :=
  if n == 0 then 0 else (n % 2) + bitCount (n / 2)

partial def countPrimeFamilyForPositions (p : Nat) (idxs : List Nat) : Nat :=
  match idxs with
  | [] => 0
  | i0 :: _ =>
      let ds := digits p
      let n := ds.length
      let upper := Nat.pow 10 n - 1
      let isPrime := sieveIsPrime upper
      let d0 := getAt ds i0
      let ok := idxs.all (fun i => getAt ds i == d0)
      if ok == false then
        0
      else
        let shift := idxs.foldl (fun acc i => acc + pow10At n i) 0
        let lead := idxs.any (fun i => i == 0)
        let rec loopR (r cnt : Nat) : Nat :=
          if r > 9 then
            cnt
          else
            if lead && r == 0 then
              loopR (r + 1) cnt
            else
              let numInt : Int := (p : Int) + ((r : Int) - (d0 : Int)) * (shift : Int)
              if numInt < 0 then
                loopR (r + 1) cnt
              else
                let num := Int.toNat numInt
                if num <= upper && isPrime[num]! then
                  loopR (r + 1) (cnt + 1)
                else
                  loopR (r + 1) cnt
        loopR 0 0

partial def findSmallestPrimeInFamily (target : Nat) : Nat :=
  let rec loopDigits (ndigits : Nat) : Nat :=
    if ndigits >= 10 then
      0
    else
      let upper := Nat.pow 10 ndigits - 1
      let lower := Nat.pow 10 (ndigits - 1)
      let isPrime := sieveIsPrime upper
      let primes := (List.range (upper + 1)).filter (fun n => n >= 2 && isPrime[n]!)
      let pow10 := (List.range ndigits).map (fun i => pow10At ndigits i)
      let rec loopP (ps : List Nat) : Nat :=
        match ps with
        | [] => loopDigits (ndigits + 1)
        | p :: ps =>
            if p < lower then
              loopP ps
            else
              let ds := digits p
              let idxs := List.range (ndigits - 1)
              let posLists := idxs.foldl (fun arr i =>
                let d := getAt ds i
                let lst := arr[d]!
                arr.set! d (i :: lst)
              ) (Array.replicate 10 ([] : List Nat))
              let rec loopDigit (d : Nat) : Nat :=
                if d >= 10 then
                  loopP ps
                else
                  let pos := posLists[d]!
                  let m := pos.length
                  if m == 0 then
                    loopDigit (d + 1)
                  else if target >= 8 && m < 3 then
                    loopDigit (d + 1)
                  else
                    let rec loopMask (mask : Nat) : Nat :=
                      if mask >= Nat.pow 2 m then
                        loopDigit (d + 1)
                      else
                        let k := bitCount mask
                        if k % 3 != 0 then
                          loopMask (mask + 1)
                        else
                          let rec loopJ (j : Nat) (shift : Nat) (lead : Bool) : Nat × Bool :=
                            if j >= m then
                              (shift, lead)
                            else
                              if (mask / (Nat.pow 2 j)) % 2 == 1 then
                                let idx := getAt pos j
                                loopJ (j + 1) (shift + getAt pow10 idx) (lead || idx == 0)
                              else
                                loopJ (j + 1) shift lead
                          let (shift, lead) := loopJ 0 0 false
                          let rec loopR (r cnt : Nat) : Nat :=
                            if r > 9 then
                              cnt
                            else
                              if lead && r == 0 then
                                loopR (r + 1) cnt
                              else
                                let numInt : Int := (p : Int) + ((r : Int) - (d : Int)) * (shift : Int)
                                if numInt < 0 then
                                  loopR (r + 1) cnt
                                else
                                  let num := Int.toNat numInt
                                  if num <= upper && isPrime[num]! then
                                    loopR (r + 1) (cnt + 1)
                                  else
                                    loopR (r + 1) cnt
                          let cnt := loopR 0 0
                          if cnt >= target then
                            p
                          else
                            loopMask (mask + 1)
                    loopMask 1
              loopDigit 0
      loopP primes
  loopDigits 2


example : countPrimeFamilyForPositions 13 [0] = 6 := by
  native_decide

example : countPrimeFamilyForPositions 56003 [2, 3] = 7 := by
  native_decide


def sol (_n : Nat) :=
  findSmallestPrimeInFamily 8

end ProjectEulerSolutions.P51
open ProjectEulerSolutions.P51

def main : IO Unit := do
  IO.println (sol 0)