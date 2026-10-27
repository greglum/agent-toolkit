#!/bin/sh
# Same checks for local work, CI and the optional repository hook. No installs or remote calls.
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

command -v python3 >/dev/null 2>&1 || { echo 'Python 3.10+ is required.' >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo 'Node.js 18+ is required.' >&2; exit 1; }

python3 "$repo_dir/scripts/check.py"
python3 -m unittest discover -q -s "$repo_dir/scripts" -p 'test_*.py'
for scripts_dir in "$repo_dir"/skills/*/scripts; do
  [ -d "$scripts_dir" ] || continue
  set -- "$scripts_dir"/test_*.py
  if [ -f "$1" ]; then
    python3 -m unittest discover -q -s "$scripts_dir" -p 'test_*.py'
  fi
  for test_file in "$scripts_dir"/test*.mjs; do
    [ -f "$test_file" ] || continue
    node --test "$test_file"
  done
done
