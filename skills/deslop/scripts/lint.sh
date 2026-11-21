#!/bin/sh

command -v vale >/dev/null 2>&1 || {
  echo "vale is not installed. See https://vale.sh/docs/install" >&2
  exit 2
}

level=warning
sync=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --all) level=suggestion; shift ;;
    --sync) sync=1; shift ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) break ;;
  esac
done
[ "$#" -ge 1 ] || { echo "usage: lint.sh [--all] [--sync] FILE..." >&2; exit 2; }

here=$(cd "$(dirname "$0")" && pwd)
cache="${XDG_CACHE_HOME:-$HOME/.cache}/deslop/vale"
mkdir -p "$cache" || exit 2
cp "$here/../vale/.vale.ini" "$cache/.vale.ini" || exit 2
if ! { [ -d "$cache/styles/write-good" ] && [ -d "$cache/styles/proselint" ] && [ -d "$cache/styles/Readability" ]; }; then
  if [ "$sync" -ne 1 ]; then
    echo "Vale styles are not cached in $cache; confirm network download authority and re-run with --sync." >&2
    exit 2
  fi
  vale --config "$cache/.vale.ini" sync >/dev/null || {
    echo "Vale style sync failed; prose check did not run." >&2
    echo "Cold setup needs access to Vale's package registry and downloads; network failures can appear as invalid package URLs." >&2
    exit 2
  }
fi

vale --config "$cache/.vale.ini" --no-wrap --minAlertLevel="$level" -- "$@"
