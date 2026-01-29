import ProjectEulerStatements.P79
namespace ProjectEulerSolutions.P79

abbrev keylogText : String :=
  String.intercalate "\n" [
    "319",
    "680",
    "180",
    "690",
    "129",
    "620",
    "762",
    "689",
    "762",
    "318",
    "368",
    "710",
    "720",
    "710",
    "629",
    "168",
    "160",
    "689",
    "716",
    "731",
    "736",
    "729",
    "316",
    "729",
    "729",
    "710",
    "769",
    "290",
    "719",
    "680",
    "318",
    "389",
    "162",
    "289",
    "162",
    "718",
    "729",
    "319",
    "790",
    "680",
    "890",
    "362",
    "319",
    "760",
    "316",
    "729",
    "380",
    "319",
    "728",
    "716"
  ]

partial def parseDigits (s : String) : List Nat :=
  s.data.map (fun c => c.toNat - '0'.toNat)

partial def getAt (xs : List Nat) (i : Nat) : Nat :=
  match xs, i with
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAt xs i

partial def addEdge (u v : Nat) (adj : Array (List Nat)) (indeg : Array Nat) : Array (List Nat) × Array Nat :=
  if adj[u]!.any (fun x => x == v) then
    (adj, indeg)
  else
    let adj := adj.set! u (v :: adj[u]!)
    let indeg := indeg.set! v (indeg[v]! + 1)
    (adj, indeg)

partial def buildGraph (attempts : List String) : Array (List Nat) × Array Nat × Array Bool :=
  let adj := Array.replicate 10 []
  let indeg := Array.replicate 10 0
  let present := Array.replicate 10 false
  let rec loop (xs : List String) (adj : Array (List Nat)) (indeg : Array Nat) (present : Array Bool)
      : Array (List Nat) × Array Nat × Array Bool :=
    match xs with
    | [] => (adj, indeg, present)
    | s :: xs =>
        let ds := parseDigits s
        let a := getAt ds 0
        let b := getAt ds 1
        let c := getAt ds 2
        let present := present.set! a true |>.set! b true |>.set! c true
        let (adj, indeg) := addEdge a b adj indeg
        let (adj, indeg) := addEdge b c adj indeg
        loop xs adj indeg present
  loop attempts adj indeg present

partial def topoSort (adj : Array (List Nat)) (indeg : Array Nat) (present : Array Bool) : List Nat :=
  let used := Array.replicate 10 false
  let total := (List.range 10).foldl (fun acc i => if present[i]! then acc + 1 else acc) 0
  let rec loop (k : Nat) (indeg : Array Nat) (used : Array Bool) (out : List Nat) : List Nat :=
    if k == total then
      out.reverse
    else
      let rec find (i : Nat) : Nat :=
        if i >= 10 then 10 else if present[i]! && used[i]! == false && indeg[i]! == 0 then i else find (i + 1)
      let v := find 0
      if v == 10 then
        out.reverse
      else
        let used := used.set! v true
        let rec decNeighbors (ns : List Nat) (indeg : Array Nat) : Array Nat :=
          match ns with
          | [] => indeg
          | x :: xs => decNeighbors xs (indeg.set! x (indeg[x]! - 1))
        let indeg := decNeighbors (adj[v]!) indeg
        loop (k + 1) indeg used (v :: out)
  loop 0 indeg used []

partial def derivePasscode : String :=
  let attempts := keylogText.splitOn "\n" |>.filter (fun ln => ln != "")
  let (adj, indeg, present) := buildGraph attempts
  let digits := topoSort adj indeg present
  digits.foldl (fun acc d => acc ++ toString d) ""


def sol (_n : Nat) :=
  derivePasscode.data

theorem equiv (n : Nat) : ProjectEulerStatements.P79.naive ([] : List String) = sol n := sorry
end ProjectEulerSolutions.P79
open ProjectEulerSolutions.P79

def main : IO Unit := do
  IO.println (String.mk (sol 0))
