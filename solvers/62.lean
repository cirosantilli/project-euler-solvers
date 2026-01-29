import ProjectEulerStatements.P62
namespace ProjectEulerSolutions.P62

partial def digitSignature (x : Nat) : Array Nat :=
  let rec loop (n : Nat) (acc : Array Nat) : Array Nat :=
    if n == 0 then
      acc
    else
      let d := n % 10
      loop (n / 10) (acc.set! d (acc[d]! + 1))
  if x == 0 then
    (Array.replicate 10 0).set! 0 1
  else
    loop x (Array.replicate 10 0)

partial def updateGroup (sig : Array Nat) (cube : Nat) (groups : List (Array Nat × Nat × Nat))
    : List (Array Nat × Nat × Nat) :=
  match groups with
  | [] => [(sig, 1, cube)]
  | (s, cnt, minc) :: rest =>
      if s == sig then
        let minc := if cube < minc then cube else minc
        (s, cnt + 1, minc) :: rest
      else
        (s, cnt, minc) :: updateGroup sig cube rest

partial def collectCandidates (k : Nat) (groups : List (Array Nat × Nat × Nat)) : List Nat :=
  match groups with
  | [] => []
  | (_, cnt, minc) :: rest =>
      if cnt == k then minc :: collectCandidates k rest else collectCandidates k rest

partial def listMin (xs : List Nat) : Nat :=
  match xs with
  | [] => 0
  | x :: xs => xs.foldl (fun acc v => if v < acc then v else acc) x

partial def smallestCubeWithKPermutations (k : Nat) : Nat :=
  let rec loop (n : Nat) (currentLen : Nat) (groups : List (Array Nat × Nat × Nat)) : Nat :=
    let cube := n * n * n
    let l := (toString cube).length
    if l > currentLen then
      let candidates := collectCandidates k groups
      if candidates != [] then
        listMin candidates
      else
        loop n l []
    else
      let sig := digitSignature cube
      let groups := updateGroup sig cube groups
      loop (n + 1) currentLen groups
  loop 1 1 []


example : smallestCubeWithKPermutations 3 = 41063625 := by
  native_decide


def sol (_n : Nat) :=
  smallestCubeWithKPermutations 5

theorem equiv (n : Nat) : ProjectEulerStatements.P62.naive n n = sol n := sorry
end ProjectEulerSolutions.P62
open ProjectEulerSolutions.P62

def main : IO Unit := do
  IO.println (sol 0)