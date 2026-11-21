# Sources and departures

Observed 2026-11-18, Pacific time. All bundled code and prose are original. No upstream text or code
was copied; only ideas were adopted. Citations were checked against the publishers' records on
2026-11-18.

| Source | Adopted idea | Rights |
| --- | --- | --- |
| Śliwerski, Zimmermann and Zeller, "When do changes induce fixes?", MSR 2005, pp. 24-28, [doi:10.1145/1083142.1083147](https://doi.org/10.1145/1083142.1083147) (SZZ) | Link a fix to the changes that last touched the lines it removed | ACM paper; idea only |
| Kim, Zimmermann, Pan and Whitehead, "Automatic identification of bug-introducing changes", ASE 2006, pp. 81-90, [doi:10.1109/ASE.2006.23](https://doi.org/10.1109/ASE.2006.23) | Ignore non-semantic changes such as whitespace and formatting, and treat blame output as an approximation | IEEE paper; idea only |

Departures: blame is bounded by a lookback and a line cap per fix, add-only fixes are reported as
unattributed instead of guessed, and the unit of analysis is the verification layer that missed the
defect, not the defect itself. Unlike retro-guardrails, a tracked run advances the marker only when
`find_escapes.py` also reported no gap, so failed tracing is reread. Line-capped files are a reported
limit with a rerun hint, not a gap, so one large fix cannot hold the marker forever. This skill only
reports and runs no repository code, gates or hooks.

Recheck when a real run shows a misattributed escape or a missed escaped layer.
