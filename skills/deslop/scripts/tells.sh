#!/bin/sh

[ "$#" -ge 1 ] || { echo "usage: tells.sh FILE..." >&2; exit 2; }
for file do
  [ -f "$file" ] && [ -r "$file" ] || {
    printf 'cannot read file: %s\n' "$file" >&2
    exit 2
  }
done

strong=0
weak=0

scan() {
  level=$1; name=$2; flags=$3; pattern=$4; shift 4
  # shellcheck disable=SC2086
  hits=$(grep -nH $flags -E -- "$pattern" "$@")
  status=$?
  [ "$status" -le 1 ] || exit 2
  [ -n "$hits" ] || return 0
  count=$(printf '%s\n' "$hits" | wc -l | tr -d ' ')
  printf '\n[%s] %s (%s)\n' "$level" "$name" "$count"
  printf '%s\n' "$hits" | awk -v pfx="$PWD/" '{ if (index($0, pfx) == 1) print substr($0, length(pfx) + 1); else print }' | cut -c1-220
  if [ "$level" = strong ]; then strong=$((strong + count)); else weak=$((weak + count)); fi
}

WB='(^|[^[:alnum:]_])'
WE='($|[^[:alnum:]_])'

scan strong "dashes as connector" -i "—|–|[[:space:]]--[[:space:]]" "$@"
# shellcheck disable=SC1111
scan strong "curly quotes" "" "“|”|‘|’" "$@"
scan strong "not X but Y" -i "${WB}(not (just|only|merely|simply) [^.]*[^[:alnum:]_]but|it'?s not [^.]*, it'?s|this (is not|isn'?t) (about|to say))${WE}" "$@"
scan strong "staged run-up" -i "${WB}(let'?s (dive|explore|break (this|it) down|be honest)|here'?s (what you need|the thing|how|why)|the thing is|without further ado|real talk|it'?s (worth noting|important to note)|in today'?s (world|landscape|fast-paced))${WE}" "$@"
scan strong "arguing with no one" -i "${WB}(to be clear|don'?t get me wrong|i'?m not saying|this is not to say|some might (say|argue)|one might be tempted|it would be easy to just)${WE}" "$@"
scan strong "one-line closers" -i "${WB}(that'?s the real win|read that again|let that sink in|this changes everything|game.?changer|the future (looks bright|is bright)|exciting times ahead|a step in the right direction)${WE}" "$@"
scan strong "stock AI words" -i "${WB}(delve[sd]?|delving|tapestry|testament|pivotal|crucial(ly)?|seamless(ly)?|leverag(e|es|ed|ing)|utiliz(e|es|ed|ing)|facilitat(e|es|ed|ing)|empower(s|ed|ing)?|streamlin(e|es|ed|ing)|cutting.edge|game.changing|holistic|synerg(y|ies|istic)|elevat(e|es|ed|ing)|embark(s|ed|ing)?|ever.evolving|underscor(e|es|ed|ing)|showcas(e|es|ed|ing)|foster(s|ed|ing)?|meticulous(ly)?|intricate|intricacies|paramount|transformative|multifaceted|realm|beacon|vibrant|groundbreaking|revolutioniz(e|es|ed|ing)|unlock(s|ed|ing)? (the )?(power|potential)|supercharge[sd]?)${WE}" "$@"
scan strong "inflated significance" -i "${WB}(stands as|serves as|plays a (key|crucial|vital|pivotal|central) role|marks a (pivotal|crucial|significant|new)|a testament to|in the heart of|nestled|reflects a broader|enduring legacy|setting the stage)${WE}" "$@"
scan strong "chatbot residue" -i "${WB}(great question|i hope this helps|let me know if|would you like me to|should i continue|you'?re absolutely right)${WE}|${WB}(certainly|of course|absolutely)!" "$@"
scan strong "knowledge disclaimers" -i "${WB}(as of my (last|knowledge)|training (data|cutoff)|not (publicly|widely) (available|documented)|it is believed that)${WE}" "$@"
scan strong "recap endings" -i "^[[:space:]]*((in conclusion|in summary|to sum up|ultimately|at the end of the day)${WE}|overall,)" "$@"
scan weak   "rather than / negative listing" -i "${WB}rather than${WE}|^[[:space:]]*(no|not) [^.]{0,40}\. (no|not) " "$@"
scan weak   "vague connection" -i "${WB}(associated with|in connection with|linked to|tied to)${WE}" "$@"
scan weak   "-ing riders" -i ", (highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|showcasing|fostering|contributing to)${WE}" "$@"
scan weak   "stacked qualifiers" -i "${WB}(could potentially|might arguably|it'?s also possible|in some cases it may)${WE}" "$@"
scan weak   "empty adverbs" -i "${WB}(actually|basically|essentially|literally|simply|truly|really|very|quite|extremely|incredibly|fundamentally|importantly|effectively|significantly)${WE}" "$@"
scan weak   "bold label + colon list" -i "^[[:space:]]*[-*] \*\*[^*]+:\*\*" "$@"
scan weak   "emoji or arrow decoration" "" "→|🚀|💡|✅|✨|🔥|📌|⚡|🎯|👉|💪|🎉" "$@"
scan weak   "title case heading" "" "^#{2,} ([A-Z][a-z]+ ){2,}[A-Z][a-z]+[[:space:]]*$" "$@"

printf '\nstrong: %s  weak: %s\n' "$strong" "$weak"
[ "$strong" -eq 0 ]
