# Report format

Load from Step 6 when writing the review output.

## Terminal output (default)

```
## PR Review: #<number or local> <title or local comparison>

**Comparison:** <base-sha>..<head-sha> (<merge-base or explicit-two-endpoint>)
**PR metadata:** <PR base and merge base, or unavailable reason>
**Changes:** <additions>+ / <deletions>- across <file-count> files
**Intent:** [1-sentence summary of what this PR does]

---

### Findings

#### [severity] [file:line-range] [short title]
**Confidence:** <score>/100
[Description of the issue and why it matters]
[Suggested fix if applicable]

---

### Summary

<count> candidates below the <threshold> threshold.

### Verdict: APPROVE | REVISE | REJECT

[Clear rationale based on findings]
```

Include complete covered paths, artifact handling, unavailable or partially inspected
content, freshness, applicable instructions, unrun gates, and preservation of files/index/refs.

For repeat reviews, include the prior comparison, each prior finding's disposition and identity,
and the coverage evidence reused or invalidated. Keep unresolved findings in the verdict.
