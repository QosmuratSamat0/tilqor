# Supervisor feedback

Task: [TIL-14](https://qosmuratsamat.youtrack.cloud/issue/TIL-14).

| Field | Value |
|---|---|
| Supervisor | Latuta Konstantin Nikolaevich |
| Date | 2026-10-24 |
| Received by | Kosmurat Samat (tech lead) |
| Reviewed version | Tag [`prob-period-1`](https://github.com/QosmuratSamat0/tilqor/tree/prob-period-1) and the consolidated report `SE-2430_Kosmurat_ProbPeriod1.pdf` |
| Decision | **Approved** |

## What was submitted for review

The team asked the supervisor for feedback on the key deliverables and decisions:

1. **Scope:** Kazakh–Russian text pairs and terms only; no audio, mobile app or pilot ([proposal](proposal.md), sections 10–12).
2. **Data quality model:** reputation-weighted voting with a 0.66 threshold and at least two people per decision, control tasks, Krippendorff's alpha ([proposal](proposal.md), section 8; [requirements](requirements.md), section 4).
3. **Evaluation without a pilot:** comparison with simple majority voting on 100–200 labelled records, with 5–10 people or a clearly labelled simulation ([verification plan](verification-plan.md), section 6).
4. **Technology stack:** Django + DRF, PostgreSQL, React, Docker ([technology comparison](tech-comparison.md)).

## Feedback and decisions

| Item | Supervisor's feedback | Team decision | Resulting change |
|---|---|---|---|
| Scope, quality model, evaluation plan, technology stack | Approved | Keep the decisions as documented | None required; the team proceeds to the MVP stage |

The supervisor's approval was communicated to the team on 2026-10-24. Any written confirmation or later comments from the supervisor will be added to this file, together with the team's decision on each comment and links to the resulting commits or pull requests.
