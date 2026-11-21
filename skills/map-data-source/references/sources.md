# Sources and departures

Observed 2026-11-20. Methods literature ideas marked "lane" were pinned by research lane
2026-11-20, not rechecked; ideas marked "local" are this bundle's own unverified restatement
from the citation alone. Agent skill commit SHAs and repository licenses below were verified
against GitHub on 2026-11-20. Ideas only are restated. No upstream text, code, prompt or
fixture was copied; all prose, scripts and fixtures here are original.
Recheck trigger: a new revision of a listed skill, or a real source where the map missed a
key, a join trap or drift.

## Methods literature

| Source | Idea restated | Local use |
| --- | --- | --- |
| Kimball, "Declaring the Grain" (2003) | Lane: declare the grain first | Step 3 writes the grain sentence before `keys` |
| Rostin et al., WebDB 2009 | Lane: value inclusion is necessary, not sufficient, for a foreign key; a person confirms | `joins` reports candidates only |
| Jiang and Naumann, HoPF, 2019 | Local: key and foreign key discovery as a ranked candidate problem | Key and join results are ranked, never confirmed |
| Abedjan, Golab and Naumann, VLDB Journal 2015 | Lane: a taxonomy of data profiling tasks | `survey`, `keys` and `joins` split the profiling work |
| Gebru et al., Datasheets for Datasets, arXiv 1803.09010 | Local: document how data was made and its caveats | Table fields for coverage, freshness and caveats |
| Data Package v2 Table Schema | Lane: `primaryKey`, `foreignKeys` and `missingValues` | Dictionary fields for keys, relationships and missing codes |
| Wretblad et al., arXiv 2408.04691 | Lane: generated column descriptions help; ambiguous columns need experts | Meaning status separates `inferred` from `sme-confirmed` |
| Akidau et al., VLDB 2015 | Lane: event time and processing time differ | Event and load time are separate dictionary fields |
| Little, 2021, missing-data assumptions | Lane: missing-data assumptions; local: MAR and MNAR cannot be separated from data alone | Missingness is recorded as an assumption with its basis |

## Agent skills

| Source | Revision | License | Idea restated (lane) | Local departure |
| --- | --- | --- | --- | --- |
| [GoogleCloudPlatform/data-agent-kit-plugin](https://github.com/GoogleCloudPlatform/data-agent-kit-plugin), curate-context | `716f429da2671acbb1faaa3944948ff9e86c5cd4` | Apache-2.0 | Literal "no description in source" marker, open questions, approval gates | The marker is one of four meaning statuses, each with required evidence |
| [dbt-labs/dbt-agent-skills](https://github.com/dbt-labs/dbt-agent-skills), discovering-data | `b8facde20b7a92c40ce3e6b86b71c4b92aa44040` | Apache-2.0 | Count orphans when exploring joins | Orphans sit beside containment, parent uniqueness and fan-out |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills), exploratory-data-analysis | `ec59a29a03d5c40f73ab40878df04860bc00e876` | MIT | Fix the unit of observation and the missing codes first | Grain is proven with exact counts; sentinel extremes are detected |
| [openai/plugins](https://github.com/openai/plugins), create-data-context | `981b02c0c44058b595f3b4180002c3ae3c806d40` | No SPDX license (marked proprietary) | Idea only, no text: an evidence register and coverage labels | Evidence is a required field on every dictionary row and claim |

Research found no existing skill that ships tools for grain and key inference, join
discovery by value overlap, drift across multi-file drops, or re-checking dictionary claims.
That is a search result as of the observation date, not a proof.
