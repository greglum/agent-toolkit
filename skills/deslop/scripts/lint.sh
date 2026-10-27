#!/bin/sh
# Run Vale on prose files with the deslop configuration (write-good, proselint,
# Readability; E-Prime and spelling off). Styles are synced once into a cache
# directory, so no repository is touched. Exit 0 clean, 1 alerts, 2 setup failure.
#
# Usage: lint.sh [--all] FILE.md...
#   --all   report suggestions as well as warnings and errors
#
# Vale handles Markdown, MDX, reStructuredText, AsciiDoc, HTML, and plain text.
# Point tells.sh at source files instead; Vale cannot parse JSX or JSON.

command -v vale >/dev/null 2>&1 || {
  echo "vale is not installed. macOS: brew install vale. Other: https://vale.sh/docs/install" >&2
  exit 2
}

level=warning
if [ "$1" = "--all" ]; then level=suggestion; shift; fi
[ "$#" -ge 1 ] || { echo "usage: lint.sh [--all] FILE..." >&2; exit 2; }

here=$(cd "$(dirname "$0")" && pwd)
cache="${XDG_CACHE_HOME:-$HOME/.cache}/deslop/vale"
mkdir -p "$cache" || exit 2
cp "$here/../vale/.vale.ini" "$cache/.vale.ini" || exit 2
if ! { [ -d "$cache/styles/write-good" ] && [ -d "$cache/styles/proselint" ] && [ -d "$cache/styles/Readability" ]; }; then
  vale --config "$cache/.vale.ini" sync >/dev/null || {
    echo "Vale style sync failed; prose check did not run." >&2
    echo "Cold setup needs access to Vale's package registry and downloads; network failures can appear as invalid package URLs." >&2
    exit 2
  }
fi

vale --config "$cache/.vale.ini" --no-wrap --minAlertLevel="$level" "$@"
