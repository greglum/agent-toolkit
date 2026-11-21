# Sources and departures

Observed 2026-11-18, Pacific time. All bundled code and prose are original. No upstream text, prompts
or code were copied; only ideas were adopted.

| Primary source and revision | Adopted idea | Rights |
| --- | --- | --- |
| [Datadog system-tests review learning](https://github.com/DataDog/system-tests/blob/af85032fbe471e54f2eeb57bd0ddf041fe9ccbba/docs/ai/review-learning.md), commit `af85032` | Windowed collection of merged pull requests, a minimum evidence bar, a rejected-proposal list, a cap per run and human approval of each rule | Apache-2.0 repository; idea only |
| [Self-Healing Harness, arXiv 2609.24130 v1](https://arxiv.org/abs/2609.24130v1) (2026-09-21) | 211 of 383 rejected self-modifications fixed their trigger but broke a working case, so a recommendation names a bad case and a protected good case | arXiv preprint; finding cited, no text copied |
| [SkillsBench, arXiv 2602.12670 v4](https://arxiv.org/abs/2602.12670v4) (2026-06-14) | Curated skills helped and self-generated skills fell below no skill, so this skill reports and a person decides | arXiv preprint; finding cited, no text copied |
| [Notion eslint-seatbelt ratchets](https://www.notion.com/blog/how-we-evolved-our-code-notions-ratcheting-system-using-custom-eslint-rules) (2025-03-03) and [Böckeler, harness engineering](https://martinfowler.com/articles/harness-engineering.html) (undated) | Ratcheted adoption, and failure output written for the next agent | Essays; idea only |

Departures: this skill only reports. It runs no repository code, gates or hooks, keeps its state
outside the repository, and leaves the choice and proof of a control to `encode-correction`.

Recheck when a real run shows a missed recurrence or a misleading coverage line.
