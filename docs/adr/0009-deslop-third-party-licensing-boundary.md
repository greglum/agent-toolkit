# 0009: Keep deslop/tells.sh Limited to Short Pattern Keywords and Track Third-Party Attribution

- Status: Accepted
- Date: 2026-11-20

## Context

skills/deslop/scripts/tells.sh adapts AI-writing tell lists from blader/humanizer 3.0.0 (MIT), petergyang/no-ai-slop (MIT), and hardikpandya/stop-slop (MIT), whose categories trace back to Wikipedia's 'Signs of AI writing' (CC BY-SA 4.0). Repository-root THIRD_PARTY_NOTICES.md already records the full MIT licenses and CC BY-SA attribution, while skills/deslop can also be installed as a standalone bundle.

## Decision

Keep tells.sh strictly limited to short keywords and stock search patterns with zero Wikipedia article prose included, and maintain the full MIT and CC BY-SA 4.0 attribution records in THIRD_PARTY_NOTICES.md (and skill-level licensing metadata if distributed standalone) rather than inline script header comments.

## Consequences

Removing inline comments from tells.sh does not lose legal provenance or the non-prose CC BY-SA compliance boundary; future contributors must not paste Wikipedia prose into pattern files.

## Code References

- `skills/deslop/scripts/tells.sh:10`
- `skills/deslop/scripts/tells.sh:11`
- `skills/deslop/scripts/tells.sh:12`
- `skills/deslop/scripts/tells.sh:13`
- `skills/deslop/scripts/tells.sh:14`
- `skills/deslop/scripts/tells.sh:15`
