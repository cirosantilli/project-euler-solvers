namespace ProjectEulerSolutions.P32

abbrev fullMask : Nat := (1 <<< 9) - 1

partial def digitMask (n : Nat) : Bool × Nat × Nat :=
  let rec loop (m mask len : Nat) : Bool × Nat × Nat :=
    if m == 0 then
      (true, mask, len)
    else
      let d := m % 10
      if d == 0 then
        (false, 0, 0)
      else
        let bit := (1 <<< (d - 1))
        if (mask &&& bit) != 0 then
          (false, 0, 0)
        else
          loop (m / 10) (mask ||| bit) (len + 1)
  loop n 0 0

partial def case1 (products : Array Bool) : Array Bool :=
  let rec loopA1 (a : Nat) (products : Array Bool) : Array Bool :=
    if a > 9 then
      products
    else
      let (okA, ma, la) := digitMask a
      if !okA then
        loopA1 (a + 1) products
      else
        let bMin :=
          let t := (1000 + a - 1) / a
          if t < 1000 then 1000 else t
        let bMax :=
          let t := 9999 / a
          if t > 9999 then 9999 else t
        let rec loopB1 (b : Nat) (products : Array Bool) : Array Bool :=
          if b > bMax then
            products
          else
            let (okB, mb, lb) := digitMask b
            if !okB || (ma &&& mb) != 0 then
              loopB1 (b + 1) products
            else
              let p := a * b
              if p < 1000 || p > 9999 then
                loopB1 (b + 1) products
              else
                let (okP, mp, lp) := digitMask p
                if !okP || ((ma ||| mb) &&& mp) != 0 then
                  loopB1 (b + 1) products
                else if la + lb + lp == 9 && (ma ||| mb ||| mp) == fullMask then
                  loopB1 (b + 1) (products.set! p true)
                else
                  loopB1 (b + 1) products
        loopA1 (a + 1) (loopB1 bMin products)
  loopA1 1 products

partial def case2 (products : Array Bool) : Array Bool :=
  let rec loopA2 (a : Nat) (products : Array Bool) : Array Bool :=
    if a > 99 then
      products
    else
      let (okA, ma, la) := digitMask a
      if !okA then
        loopA2 (a + 1) products
      else
        let bMin :=
          let t := (1000 + a - 1) / a
          if t < 100 then 100 else t
        let bMax :=
          let t := 9999 / a
          if t > 999 then 999 else t
        let rec loopB2 (b : Nat) (products : Array Bool) : Array Bool :=
          if b > bMax then
            products
          else
            let (okB, mb, lb) := digitMask b
            if !okB || (ma &&& mb) != 0 then
              loopB2 (b + 1) products
            else
              let p := a * b
              if p < 1000 || p > 9999 then
                loopB2 (b + 1) products
              else
                let (okP, mp, lp) := digitMask p
                if !okP || ((ma ||| mb) &&& mp) != 0 then
                  loopB2 (b + 1) products
                else if la + lb + lp == 9 && (ma ||| mb ||| mp) == fullMask then
                  loopB2 (b + 1) (products.set! p true)
                else
                  loopB2 (b + 1) products
        loopA2 (a + 1) (loopB2 bMin products)
  loopA2 10 products

partial def solve : Nat :=
  let products := Array.replicate 10000 false
  let products := case1 products
  let products := case2 products
  let rec sum (i acc : Nat) : Nat :=
    if i >= products.size then
      acc
    else
      let acc' := if products[i]! then acc + i else acc
      sum (i + 1) acc'
  sum 0 0


def sol : Nat :=
  solve

end ProjectEulerSolutions.P32
open ProjectEulerSolutions.P32

def main : IO Unit := do
  IO.println sol
