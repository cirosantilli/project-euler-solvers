import ProjectEulerStatements.P19
namespace ProjectEulerSolutions.P19

partial def isLeapYear (year : Nat) : Bool :=
  if year % 400 == 0 then
    true
  else if year % 100 == 0 then
    false
  else
    year % 4 == 0

partial def daysInMonth (year month : Nat) : Nat :=
  if month == 2 then
    if isLeapYear year then 29 else 28
  else if month == 4 || month == 6 || month == 9 || month == 11 then
    30
  else
    31

partial def countSundaysOnFirst (startYear endYear : Nat) : Nat :=
  let rec loopYear (year dow count : Nat) : Nat :=
    if year > endYear then
      count
    else
      let rec loopMonth (month dow count : Nat) : Nat :=
        if month > 12 then
          loopYear (year + 1) dow count
        else
          let count' :=
            if startYear <= year && year <= endYear && dow == 6 then
              count + 1
            else
              count
          let dow' := (dow + daysInMonth year month) % 7
          loopMonth (month + 1) dow' count'
      loopMonth 1 dow count
  loopYear 1900 0 0



def sol (_n : Nat) : Nat :=
  countSundaysOnFirst 1901 2000

theorem equiv (n : Nat) : ProjectEulerStatements.P19.naive = sol n := sorry
end ProjectEulerSolutions.P19
open ProjectEulerSolutions.P19

def main : IO Unit := do
  IO.println (sol 0)
