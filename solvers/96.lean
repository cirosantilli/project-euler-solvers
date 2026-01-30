import ProjectEulerStatements.P96
namespace ProjectEulerSolutions.P96

abbrev sudokuText : String :=
  String.intercalate "\n" [
    "Grid 01",
    "003020600",
    "900305001",
    "001806400",
    "008102900",
    "700000008",
    "006708200",
    "002609500",
    "800203009",
    "005010300",
    "Grid 02",
    "200080300",
    "060070084",
    "030500209",
    "000105408",
    "000000000",
    "402706000",
    "301007040",
    "720040060",
    "004010003",
    "Grid 03",
    "000000907",
    "000420180",
    "000705026",
    "100904000",
    "050000040",
    "000507009",
    "920108000",
    "034059000",
    "507000000",
    "Grid 04",
    "030050040",
    "008010500",
    "460000012",
    "070502080",
    "000603000",
    "040109030",
    "250000098",
    "001020600",
    "080060020",
    "Grid 05",
    "020810740",
    "700003100",
    "090002805",
    "009040087",
    "400208003",
    "160030200",
    "302700060",
    "005600008",
    "076051090",
    "Grid 06",
    "100920000",
    "524010000",
    "000000070",
    "050008102",
    "000000000",
    "402700090",
    "060000000",
    "000030945",
    "000071006",
    "Grid 07",
    "043080250",
    "600000000",
    "000001094",
    "900004070",
    "000608000",
    "010200003",
    "820500000",
    "000000005",
    "034090710",
    "Grid 08",
    "480006902",
    "002008001",
    "900370060",
    "840010200",
    "003704100",
    "001060049",
    "020085007",
    "700900600",
    "609200018",
    "Grid 09",
    "000900002",
    "050123400",
    "030000160",
    "908000000",
    "070000090",
    "000000205",
    "091000050",
    "007439020",
    "400007000",
    "Grid 10",
    "001900003",
    "900700160",
    "030005007",
    "050000009",
    "004302600",
    "200000070",
    "600100030",
    "042007006",
    "500006800",
    "Grid 11",
    "000125400",
    "008400000",
    "420800000",
    "030000095",
    "060902010",
    "510000060",
    "000003049",
    "000007200",
    "001298000",
    "Grid 12",
    "062340750",
    "100005600",
    "570000040",
    "000094800",
    "400000006",
    "005830000",
    "030000091",
    "006400007",
    "059083260",
    "Grid 13",
    "300000000",
    "005009000",
    "200504000",
    "020000700",
    "160000058",
    "704310600",
    "000890100",
    "000067080",
    "000005437",
    "Grid 14",
    "630000000",
    "000500008",
    "005674000",
    "000020000",
    "003401020",
    "000000345",
    "000007004",
    "080300902",
    "947100080",
    "Grid 15",
    "000020040",
    "008035000",
    "000070602",
    "031046970",
    "200000000",
    "000501203",
    "049000730",
    "000000010",
    "800004000",
    "Grid 16",
    "361025900",
    "080960010",
    "400000057",
    "008000471",
    "000603000",
    "259000800",
    "740000005",
    "020018060",
    "005470329",
    "Grid 17",
    "050807020",
    "600010090",
    "702540006",
    "070020301",
    "504000908",
    "103080070",
    "900076205",
    "060090003",
    "080103040",
    "Grid 18",
    "080005000",
    "000003457",
    "000070809",
    "060400903",
    "007010500",
    "408007020",
    "901020000",
    "842300000",
    "000100080",
    "Grid 19",
    "003502900",
    "000040000",
    "106000305",
    "900251008",
    "070408030",
    "800763001",
    "308000104",
    "000020000",
    "005104800",
    "Grid 20",
    "000000000",
    "009805100",
    "051907420",
    "290401065",
    "000000000",
    "140508093",
    "026709580",
    "005103600",
    "000000000",
    "Grid 21",
    "020030090",
    "000907000",
    "900208005",
    "004806500",
    "607000208",
    "003102900",
    "800605007",
    "000309000",
    "030020050",
    "Grid 22",
    "005000006",
    "070009020",
    "000500107",
    "804150000",
    "000803000",
    "000092805",
    "907006000",
    "030400010",
    "200000600",
    "Grid 23",
    "040000050",
    "001943600",
    "009000300",
    "600050002",
    "103000506",
    "800020007",
    "005000200",
    "002436700",
    "030000040",
    "Grid 24",
    "004000000",
    "000030002",
    "390700080",
    "400009001",
    "209801307",
    "600200008",
    "010008053",
    "900040000",
    "000000800",
    "Grid 25",
    "360020089",
    "000361000",
    "000000000",
    "803000602",
    "400603007",
    "607000108",
    "000000000",
    "000418000",
    "970030014",
    "Grid 26",
    "500400060",
    "009000800",
    "640020000",
    "000001008",
    "208000501",
    "700500000",
    "000090084",
    "003000600",
    "060003002",
    "Grid 27",
    "007256400",
    "400000005",
    "010030060",
    "000508000",
    "008060200",
    "000107000",
    "030070090",
    "200000004",
    "006312700",
    "Grid 28",
    "000000000",
    "079050180",
    "800000007",
    "007306800",
    "450708096",
    "003502700",
    "700000005",
    "016030420",
    "000000000",
    "Grid 29",
    "030000080",
    "009000500",
    "007509200",
    "700105008",
    "020090030",
    "900402001",
    "004207100",
    "002000800",
    "070000090",
    "Grid 30",
    "200170603",
    "050000100",
    "000006079",
    "000040700",
    "000801000",
    "009050000",
    "310400000",
    "005000060",
    "906037002",
    "Grid 31",
    "000000080",
    "800701040",
    "040020030",
    "374000900",
    "000030000",
    "005000321",
    "010060050",
    "050802006",
    "080000000",
    "Grid 32",
    "000000085",
    "000210009",
    "960080100",
    "500800016",
    "000000000",
    "890006007",
    "009070052",
    "300054000",
    "480000000",
    "Grid 33",
    "608070502",
    "050608070",
    "002000300",
    "500090006",
    "040302050",
    "800050003",
    "005000200",
    "010704090",
    "409060701",
    "Grid 34",
    "050010040",
    "107000602",
    "000905000",
    "208030501",
    "040070020",
    "901080406",
    "000401000",
    "304000709",
    "020060010",
    "Grid 35",
    "053000790",
    "009753400",
    "100000002",
    "090080010",
    "000907000",
    "080030070",
    "500000003",
    "007641200",
    "061000940",
    "Grid 36",
    "006080300",
    "049070250",
    "000405000",
    "600317004",
    "007000800",
    "100826009",
    "000702000",
    "075040190",
    "003090600",
    "Grid 37",
    "005080700",
    "700204005",
    "320000084",
    "060105040",
    "008000500",
    "070803010",
    "450000091",
    "600508007",
    "003010600",
    "Grid 38",
    "000900800",
    "128006400",
    "070800060",
    "800430007",
    "500000009",
    "600079008",
    "090004010",
    "003600284",
    "001007000",
    "Grid 39",
    "000080000",
    "270000054",
    "095000810",
    "009806400",
    "020403060",
    "006905100",
    "017000620",
    "460000038",
    "000090000",
    "Grid 40",
    "000602000",
    "400050001",
    "085010620",
    "038206710",
    "000000000",
    "019407350",
    "026040530",
    "900020007",
    "000809000",
    "Grid 41",
    "000900002",
    "050123400",
    "030000160",
    "908000000",
    "070000090",
    "000000205",
    "091000050",
    "007439020",
    "400007000",
    "Grid 42",
    "380000000",
    "000400785",
    "009020300",
    "060090000",
    "800302009",
    "000040070",
    "001070500",
    "495006000",
    "000000092",
    "Grid 43",
    "000158000",
    "002060800",
    "030000040",
    "027030510",
    "000000000",
    "046080790",
    "050000080",
    "004070100",
    "000325000",
    "Grid 44",
    "010500200",
    "900001000",
    "002008030",
    "500030007",
    "008000500",
    "600080004",
    "040100700",
    "000700006",
    "003004050",
    "Grid 45",
    "080000040",
    "000469000",
    "400000007",
    "005904600",
    "070608030",
    "008502100",
    "900000005",
    "000781000",
    "060000010",
    "Grid 46",
    "904200007",
    "010000000",
    "000706500",
    "000800090",
    "020904060",
    "040002000",
    "001607000",
    "000000030",
    "300005702",
    "Grid 47",
    "000700800",
    "006000031",
    "040002000",
    "024070000",
    "010030080",
    "000060290",
    "000800070",
    "860000500",
    "002006000",
    "Grid 48",
    "001007090",
    "590080001",
    "030000080",
    "000005800",
    "050060020",
    "004100000",
    "080000030",
    "100020079",
    "020700400",
    "Grid 49",
    "000003017",
    "015009008",
    "060000000",
    "100007000",
    "009000200",
    "000500004",
    "000000020",
    "500600340",
    "340200000",
    "Grid 50",
    "300200000",
    "000107000",
    "706030500",
    "070009080",
    "900020004",
    "010800050",
    "009040301",
    "000702000",
    "000008006"
  ]

partial def bit (d : Nat) : Nat :=
  Nat.pow 2 d

abbrev ALL : Nat := Nat.pow 2 9 - 1

partial def bitCount (n : Nat) : Nat :=
  if n == 0 then 0 else (n % 2) + bitCount (n / 2)

partial def bitToDigit (mask : Nat) : Nat :=
  let rec loop (d : Nat) : Nat :=
    if d >= 9 then 0
    else if mask == bit d then d + 1 else loop (d + 1)
  loop 0

partial def iterBits (mask : Nat) : List Nat :=
  let rec loop (d : Nat) (acc : List Nat) : List Nat :=
    if d >= 9 then acc.reverse
    else
      let acc := if (mask &&& bit d) != 0 then (bit d) :: acc else acc
      loop (d + 1) acc
  loop 0 []

partial def concatMap {α β : Type} (f : α -> List β) (xs : List α) : List β :=
  match xs with
  | [] => []
  | x :: xs => f x ++ concatMap f xs

partial def buildUnits : List (List Nat) :=
  let rows := (List.range 9).map (fun r => (List.range 9).map (fun c => r * 9 + c))
  let cols := (List.range 9).map (fun c => (List.range 9).map (fun r => r * 9 + c))
  let boxes :=
    concatMap (fun br =>
      (List.range 3).map (fun bc =>
        concatMap (fun r =>
          (List.range 3).map (fun c => (br * 3 + r) * 9 + (bc * 3 + c))) (List.range 3))) (List.range 3)
  rows ++ cols ++ boxes

partial def buildPeers : Array (List Nat) :=
  let units := buildUnits
  let rec loopCell (i : Nat) (acc : Array (List Nat)) : Array (List Nat) :=
    if i >= 81 then
      acc
    else
      let mask0 := Array.replicate 81 false
      let mask := units.foldl (fun m u =>
        if u.any (fun x => x == i) then
          u.foldl (fun m x => if x == i then m else m.set! x true) m
        else
          m) mask0
      let peers := (List.range 81).filter (fun j => mask[j]!)
      loopCell (i + 1) (acc.set! i peers)
  loopCell 0 (Array.replicate 81 [])

partial def reduceCands (cands : Array Nat) (peers : Array (List Nat)) (units : List (List Nat))
    : Option (Array Nat) :=
  let rec loopChanged (cands : Array Nat) : Option (Array Nat) :=
    let rec propagateSingles (queue : List Nat) (cands : Array Nat) : Option (Array Nat) :=
      match queue with
      | [] => some cands
      | i :: qs =>
          let val := cands[i]!
          let rec loopPeers (ps : List Nat) (cands : Array Nat) (queue : List Nat)
              : Option (Array Nat × List Nat) :=
            match ps with
            | [] => some (cands, queue)
            | p :: ps =>
                if (cands[p]! &&& val) != 0 then
                  let newMask := cands[p]! &&& (ALL - val)
                  if newMask == 0 then
                    none
                  else
                    let queue := if bitCount newMask == 1 then p :: queue else queue
                    loopPeers ps (cands.set! p newMask) queue
                else
                  loopPeers ps cands queue
          match loopPeers (peers[i]!) cands qs with
          | none => none
          | some (cands, queue) => propagateSingles queue cands

    let singles := (List.range 81).filter (fun i => bitCount (cands[i]!) == 1)
    match propagateSingles singles cands with
    | none => none
    | some cands =>
        let rec loopUnits (us : List (List Nat)) (cands : Array Nat) (changed : Bool)
            : Option (Array Nat × Bool) :=
          match us with
          | [] => some (cands, changed)
          | u :: us =>
              let rec loopBit (d : Nat) (cands : Array Nat) (changed : Bool)
                  : Option (Array Nat × Bool) :=
                if d >= 9 then
                  loopUnits us cands changed
                else
                  let b := bit d
                  let places := u.filter (fun i => (cands[i]! &&& b) != 0)
                  if places.isEmpty then
                    none
                  else if places.length == 1 then
                    let i := places.headD 0
                    if cands[i]! != b then
                      loopBit (d + 1) (cands.set! i b) true
                    else
                      loopBit (d + 1) cands changed
                  else
                    loopBit (d + 1) cands changed
              loopBit 0 cands changed
        match loopUnits units cands false with
        | none => none
        | some (cands, changed2) =>
            if changed2 then loopChanged cands else some cands
  loopChanged cands

partial def solveCands (cands : Array Nat) (peers : Array (List Nat)) (units : List (List Nat))
    : Option (Array Nat) :=
  match reduceCands cands peers units with
  | none => none
  | some cands =>
      if (List.range 81).all (fun i => bitCount (cands[i]!) == 1) then
        some cands
      else
        let rec findBest (i : Nat) (bestI bestC : Nat) : Nat × Nat :=
          if i >= 81 then (bestI, bestC)
          else
            let bc := bitCount (cands[i]!)
            if bc > 1 && bc < bestC then
              findBest (i + 1) i bc
            else
              findBest (i + 1) bestI bestC
        let (idx, _) := findBest 0 0 10
        let bits := iterBits (cands[idx]!)
        let rec tryBits (bs : List Nat) : Option (Array Nat) :=
          match bs with
          | [] => none
          | b :: bs =>
              let next := cands.set! idx b
              match solveCands next peers units with
              | some res => some res
              | none => tryBits bs
        tryBits bits

partial def getAtChar (xs : List Char) (i : Nat) : Char :=
  match xs, i with
  | [], _ => '0'
  | x :: _, 0 => x
  | _ :: xs, i + 1 => getAtChar xs i

partial def gridToCands (grid : List String) : Array Nat :=
  let rec loopR (r : Nat) (acc : Array Nat) : Array Nat :=
    if r >= 9 then
      acc
    else
      let row := (grid.getD r "")
      let chars := row.data
      let rec loopC (c : Nat) (acc : Array Nat) : Array Nat :=
        if c >= 9 then
          acc
        else
          let ch := getAtChar chars c
          let idx := r * 9 + c
          let acc :=
            if ch == '0' then acc.set! idx ALL
            else acc.set! idx (bit (ch.toNat - '1'.toNat))
          loopC (c + 1) acc
      loopR (r + 1) (loopC 0 acc)
  loopR 0 (Array.replicate 81 ALL)

partial def topLeftNumber (solve : Array Nat) : Nat :=
  let a := bitToDigit (solve[0]!)
  let b := bitToDigit (solve[1]!)
  let c := bitToDigit (solve[2]!)
  100 * a + 10 * b + c

partial def parsePuzzles (text : String) : List (List String) :=
  let lines := text.splitOn "\n" |>.filter (fun ln => ln != "")
  let rec loop (ls : List String) (acc : List (List String)) : List (List String) :=
    match ls with
    | [] => acc.reverse
    | l :: ls =>
        if l.startsWith "Grid" then
          let grid := ls.take 9
          loop (ls.drop 9) (grid :: acc)
        else
          loop ls acc
  loop lines []

partial def solve : Nat :=
  let puzzles := parsePuzzles sudokuText
  let peers := buildPeers
  let units := buildUnits
  let rec loop (ps : List (List String)) (acc : Nat) : Nat :=
    match ps with
    | [] => acc
    | g :: gs =>
        let cands := gridToCands g
        match solveCands cands peers units with
        | some solve => loop gs (acc + topLeftNumber solve)
        | none => loop gs acc
  loop puzzles 0



theorem equiv (n : Nat) : ProjectEulerStatements.P96.naive ([] : List (List (List Nat))) = solve := sorry
end ProjectEulerSolutions.P96
open ProjectEulerSolutions.P96

def main : IO Unit := do
  IO.println solve
