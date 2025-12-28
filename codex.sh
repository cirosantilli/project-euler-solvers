#!/usr/bin/env bash
# This correctly solved 14 problems but then ran out of credits
# on my Plus plan, so it is not very practical.
set -eux
md="$(realpath "$1")"
num="$(basename ${1%.*})"
indir="$PWD"
cd "$(mktemp -d)"
pwd
(
  cat "$indir/codex.txt"
  cat "$md"
) | time codex exec --skip-git-repo-check -C . -s workspace-write
mv main.py "$indir/solvers/$num.py"
mv README.md "$indir/solvers/$num.md"
