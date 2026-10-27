#!/usr/bin/env bash
# ui-tells.sh: grep source trees for the class-name and markup tells of AI-generated UI.
# Usage: ui-tells.sh PATH...   Exit 1 on a strong hit, 0 otherwise, 2 on scan failure.
set -euo pipefail
if [ $# -eq 0 ]; then echo "usage: ui-tells.sh PATH..." >&2; exit 2; fi
for dependency in grep find xargs sed perl; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    printf 'ui-tells: missing dependency: %s\n' "$dependency" >&2
    exit 2
  fi
done
for target in "$@"; do
  if [ ! -f "$target" ] && [ ! -d "$target" ]; then
    printf 'ui-tells: target is not a file or directory: %s\n' "$target" >&2
    exit 2
  fi
done
INCLUDE=(--include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.js' --include='*.vue' --include='*.svelte' --include='*.html' --include='*.css' --include='*.scss' --include='*.mdx')
EXCLUDE=(--exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build --exclude-dir=coverage --exclude-dir=.git --exclude='*.test.*' --exclude='*.spec.*' --exclude='*.stories.*')
strong=0
emit_hits() {
  local label="$1" strength="$2" hits="$3"
  [ -z "$hits" ] && return 0
  printf '\n== %s (%s) ==\n' "$label" "$strength"
  printf '%s\n' "$hits" | sed -n '1,200p;201{s/.*/[ui-tells: more matches omitted; narrow the target or inspect the source]/;p;}'
  [ "$strength" = strong ] && strong=1
  return 0
}
run() {
  local label="$1" pattern="$2" strength="$3"
  shift 3
  local hits status
  if hits=$(grep -rnHE "${INCLUDE[@]}" "${EXCLUDE[@]}" -- "$pattern" "$@"); then
    emit_hits "$label" "$strength" "$hits"
  else
    status=$?
    [ "$status" -eq 1 ] && return 0
    printf 'ui-tells: scan failed for %s\n' "$label" >&2
    return 2
  fi
}
run_all() {
  run "V1 decorative gradient (purple/indigo/violet/fuchsia/pink families or via-)" \
      '(from|via|to)-(purple|indigo|violet|fuchsia|pink)-[0-9]{2,3}|bg-gradient-to-[a-z]{1,2}[^"'"'"'`]*(via-|from-(purple|indigo|violet|fuchsia|pink))' strong "$@"
  run "V2 gradient text fill" 'bg-clip-text|text-transparent' strong "$@"
  run "V3 glow / blob / aurora" 'blur-(2xl|3xl)|drop-shadow-\[|shadow-\[0_0_|mix-blend-(screen|plus-lighter)|animate-(aurora|glow|blob)' strong "$@"
  run "V4 glassmorphism" 'backdrop-blur|bg-white/[0-9]{1,2}\b.*border-white/|bg-black/[0-9]{1,2}\b.*border-white/' strong "$@"
  run "V6 uniform large radius" 'rounded-(2xl|3xl|\[[0-9]{2,}px\])' weak "$@"
  run "V7 heavy shadow on content" 'shadow-(xl|2xl)\b' weak "$@"
  # shellcheck disable=SC2016 # Perl owns these variables, so keep shell expansion off.
  if emoji_hits=$(find -H "$@" \( -type d \( -name node_modules -o -name dist -o -name build -o -name coverage -o -name .git \) -prune \) -o \( -type f \( -name '*.tsx' -o -name '*.jsx' -o -name '*.ts' -o -name '*.js' -o -name '*.vue' -o -name '*.svelte' -o -name '*.html' -o -name '*.mdx' \) ! -name '*.test.*' ! -name '*.spec.*' ! -name '*.stories.*' -print0 \) | xargs -0 perl -CSD -ne 'print "$ARGV:$.:$_" if /[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B50}\x{2705}]/; close ARGV if eof' --); then
    emit_hits "V8 emoji in markup or strings" strong "$emoji_hits"
  else
    echo 'ui-tells: emoji scan failed' >&2
    return 2
  fi
  run "V9 sparkle / magic icons" 'Sparkles?Icon|WandIcon|Wand2|MagicWand|<Sparkle' strong "$@"
  run "V10 colored left-border accent" 'border-l-(2|4|8) border-(l-)?(red|orange|amber|yellow|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-' weak "$@"
  run "V11 generic status dot" '(size|h)-(1\.5|2|2\.5|3) (w-(1\.5|2|2\.5|3) )?rounded-full bg-(red|orange|amber|yellow|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|pink|rose|success|warning|destructive|info)' weak "$@"
  run "V12 decorative motion" 'hover:(scale|-translate-y|rotate)-|animate-(bounce|pulse|ping|spin)\b|group-hover:(scale|translate)' weak "$@"
  run "V13 icon stamp" '(rounded-(lg|xl|2xl)|rounded-full) [^"]*bg-(primary|accent|[a-z]+-(50|100))/?[0-9]*[^"]*(p-2|p-3|size-(8|9|10|12))' weak "$@"
  run "C2 verb slop in strings" '"[^"]*\b(Empower|Unlock|Supercharge|Elevate|Seamless(ly)?|Effortless(ly)?|Leverage|Robust|Delightful|Next-level|Game-chang)[^"]*"' strong "$@"
  run "C8 chat register" '"[^"]*(Welcome back!|Oops|Awesome|Great job|You.re all set!|Let.s get started!|Hooray|Yay)[^"]*"|>[^<]*![^<]*<' weak "$@"
  run "C1 aspirational headline" '"[^"]*\b(Work smarter|your potential|Take control|All in one place|Built for teams|Made simple|Reimagined?)\b[^"]*"' strong "$@"
}
run_all "$@"
if [ "$strong" -eq 1 ]; then echo; echo "ui-tells: strong hits found"; exit 1; fi
echo; echo "ui-tells: no strong hits"; exit 0
