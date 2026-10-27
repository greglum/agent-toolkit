#!/bin/sh
# Grep the strongest AI-writing tells and print file:line hits, grouped by tell.
# Works on any text or source file (Markdown, TSX, JSON catalogs, templates).
# Exit 1 on strong hits, 0 on weak/no hits, 2 on usage or a scan failure.
#
# Usage: tells.sh FILE...
#
# Strong tells justify an edit on one sighting (humanizer §1-§5, §8, §12-§13, §22-§23).
# Weak tells need company from other tells in the same passage before acting.
# Patterns follow blader/humanizer 3.0.0 (MIT), petergyang/no-ai-slop (MIT), and
# hardikpandya/stop-slop (MIT); see the skill's SKILL.md for the workflow.
# humanizer's tell categories come from "Wikipedia:Signs of AI writing" by Wikipedia
# contributors, https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing, licensed
# CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Only short keywords and
# stock phrases are kept here as search patterns; no article prose is included.

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
  printf '%s\n' "$hits" | sed "s|^$PWD/||" | cut -c1-220
  if [ "$level" = strong ]; then strong=$((strong + count)); else weak=$((weak + count)); fi
}

scan strong "dashes as connector" -i "—|–|[[:space:]]--[[:space:]]" "$@"
# shellcheck disable=SC1111
scan strong "curly quotes" "" "“|”|‘|’" "$@"
scan strong "not X but Y" -i "\bnot (just|only|merely|simply) [^.]*\bbut\b|\bit'?s not [^.]*, it'?s\b|\bthis (is not|isn'?t) (about|to say)\b" "$@"
scan strong "staged run-up" -i "\b(let'?s (dive|explore|break (this|it) down|be honest)|here'?s (what you need|the thing|how|why)|the thing is|without further ado|real talk|it'?s (worth noting|important to note)|in today'?s (world|landscape|fast-paced))\b" "$@"
scan strong "arguing with no one" -i "\b(to be clear|don'?t get me wrong|i'?m not saying|this is not to say|some might (say|argue)|one might be tempted|it would be easy to just)\b" "$@"
scan strong "one-line closers" -i "\b(that'?s the real win|read that again|let that sink in|this changes everything|game.?changer|the future (looks bright|is bright)|exciting times ahead|a step in the right direction)\b" "$@"
scan strong "stock AI words" -i "\b(delve[sd]?|delving|tapestry|testament|pivotal|crucial(ly)?|seamless(ly)?|leverag(e|es|ed|ing)|utiliz(e|es|ed|ing)|facilitat(e|es|ed|ing)|empower(s|ed|ing)?|streamlin(e|es|ed|ing)|cutting.edge|game.changing|holistic|synerg(y|ies|istic)|elevat(e|es|ed|ing)|embark(s|ed|ing)?|ever.evolving|underscor(e|es|ed|ing)|showcas(e|es|ed|ing)|foster(s|ed|ing)?|meticulous(ly)?|intricate|intricacies|paramount|transformative|multifaceted|realm|beacon|vibrant|groundbreaking|revolutioniz(e|es|ed|ing)|unlock(s|ed|ing)? (the )?(power|potential)|supercharge[sd]?)\b" "$@"
scan strong "inflated significance" -i "\b(stands as|serves as|plays a (key|crucial|vital|pivotal|central) role|marks a (pivotal|crucial|significant|new)|a testament to|in the heart of|nestled|reflects a broader|enduring legacy|setting the stage)\b" "$@"
scan strong "chatbot residue" -i "\b(great question|i hope this helps|certainly!|of course!|absolutely!|let me know if|would you like me to|should i continue|you'?re absolutely right)\b" "$@"
scan strong "knowledge disclaimers" -i "\b(as of my (last|knowledge)|training (data|cutoff)|not (publicly|widely) (available|documented)|it is believed that)\b" "$@"
scan strong "recap endings" -i "^[[:space:]]*(in conclusion|in summary|to sum up|ultimately|overall,|at the end of the day)\b" "$@"
scan weak   "rather than / negative listing" -i "\brather than\b|^[[:space:]]*(no|not) [^.]{0,40}\. (no|not) " "$@"
scan weak   "vague connection" -i "\b(associated with|in connection with|linked to|tied to)\b" "$@"
scan weak   "-ing riders" -i ", (highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|showcasing|fostering|contributing to)\b" "$@"
scan weak   "stacked qualifiers" -i "\b(could potentially|might arguably|it'?s also possible|in some cases it may)\b" "$@"
scan weak   "empty adverbs" -i "\b(actually|basically|essentially|literally|simply|truly|really|very|quite|extremely|incredibly|fundamentally|importantly|effectively|significantly)\b" "$@"
scan weak   "bold label + colon list" -i "^[[:space:]]*[-*] \*\*[^*]+:\*\*" "$@"
scan weak   "emoji or arrow decoration" "" "→|🚀|💡|✅|✨|🔥|📌|⚡|🎯|👉|💪|🎉" "$@"
scan weak   "title case heading" "" "^#{2,} ([A-Z][a-z]+ ){2,}[A-Z][a-z]+[[:space:]]*$" "$@"

printf '\nstrong: %s  weak: %s\n' "$strong" "$weak"
[ "$strong" -eq 0 ]
