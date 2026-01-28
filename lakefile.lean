import Lake

open System Lake DSL
open Lean Elab Command Parser

private def exeFiles (dir : FilePath) : IO (Array FilePath) :=
  dir.readDir >>= fun entries =>
    pure <| entries.foldl (init := #[]) fun acc entry =>
      if entry.path.extension == some "lean" then
        acc.push entry.path
      else
        acc

/--
Declare a `lean_exe` for each `.lean` file in the given directory.
The executable is named `{stem}` and uses `root := {stem}`.
-/
elab "lean_exes_from " dir:str : command => do
  let dirStr := dir.getString
  liftIO (exeFiles dirStr) >>= fun paths => do
    for path in paths do
      match path.fileStem with
      | none => pure ()
      | some stem =>
        let exeName := s!"«{stem}»"
        let exeCmdStr :=
          s!"lean_exe {exeName} where\n" ++
          s!"  root := Name.mkSimple \"{stem}\"\n"
        match runParserCategory (← getEnv) `command exeCmdStr with
        | .error err => throwError err
        | .ok stx => elabCommand stx

package ProjectEulerSolvers where
  version := v!"0.1.0"
  keywords := #["math"]
  srcDir := "solvers"
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩,
    ⟨`relaxedAutoImplicit, false⟩,
    ⟨`weak.linter.mathlibStandardSet, true⟩,
    ⟨`maxSynthPendingDepth, (Lean.LeanOptionValue.ofNat 3)⟩
  ]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.24.0"

require ProjectEulerStatements from
  "data/project-euler-statements/data/lean"

lean_lib Exes

lean_exes_from "solvers"

/--
Copy built executables into `solvers/` with a `.out` suffix.
-/
@[default_target]
target copy_exes pkg : Unit := do
  let destDir := pkg.dir / "solvers"
  let exes := pkg.leanExes
  let copyJobs ← exes.mapM fun exe => do
    let exeJob ← exe.fetch
    exeJob.mapM (sync := true) fun path => do
      let name := path.fileName.getD path.toString
      let dest := destDir / s!"{name}_lean.out"
      let createDir : LogIO Unit := liftM (m := IO) <| IO.FS.createDirAll destDir
      let copyExe : LogIO Unit := liftM (m := IO) <| Lake.copyFile path dest
      let chmodExe : LogIO Unit := liftM (m := IO) <| do
        let user : IO.AccessRight := {read := true, write := true, execution := true}
        let rx : IO.AccessRight := {read := true, execution := true}
        let mode : IO.FileRight := {user := user, group := rx, other := rx}
        IO.setAccessRights dest mode
      liftM (m := LogIO) createDir
      liftM (m := LogIO) copyExe
      liftM (m := LogIO) chmodExe
      return ()
  return Job.mixArray copyJobs "copy-exes"
