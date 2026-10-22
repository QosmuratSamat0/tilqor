# Project proposal

Task: TIL-3.

## 1. Title

**Development of a crowdsourcing platform for collecting and verifying Kazakh language data, with daily practice and terminology dictionary modules.**

Working name: **Tilqor** (temporary).

## 2. Team and supervisor

Group SE-2430.

| Member | Role | Main responsibilities |
|---|---|---|
| Kosmurat Samat | Tech lead, architect | Architecture, data quality model, DevOps, optional AI features, repository and YouTrack |
| Alpamys Abylaikhan | Analyst, UX lead and developer | Existing system comparison, prototype and user scenarios, README, literature review analysis table |
| Dovutbekov Ulykbek | Requirements and research lead, developer | User survey, requirements and acceptance criteria, risks and milestones, search and verification of literature sources |

Supervisor: **Latuta Konstantin Nikolaevich**.

The split is preliminary and is tracked in YouTrack (project TIL).

## 3. Problem statement

Each statement is marked as **verified** (supported by a source or by our own check) or **assumption** (our hypothesis, still to be confirmed by the survey or the literature review).

1. There is little verified parallel text data for Kazakh, so AI and NLP models for Kazakh lack training and evaluation data. *Assumption: to be supported by sources in the literature review (TIL-12, TIL-13).*
2. In fields such as medicine, IT and engineering there are no single accepted Kazakh terms, and Russian connectors ("короче", "но") are common in Kazakh speech and writing. *Assumption: to be checked with the survey (TIL-8).*
3. Existing resources solve only parts of the problem *(details and sources in the system comparison, TIL-9)*:
   - **KSC (ISSAI)** collects speech (audio), not text pairs. The corpus size of about 332 hours is reported in Khassanov et al., EACL 2021 and on OpenSLR; the arXiv version gives 335 hours. *To verify against both sources in the literature review.*
   - **termincom.kz**: terms are approved top-down by a commission.
   - **sozdikqor.kz, qazcorpora.kz**: reference dictionaries and corpora, without user voting.
   - **Common Voice**: crowdsourced speech collection, not text pairs or terms.
4. As of 17.10.2026, our search did not find a platform where users suggest and vote on Kazakh terms and ru-kk translations with a measurable data quality model. *Verified by our own search; the search was not exhaustive.*

## 4. Target users

- Native speakers and learners of Kazakh
- Students
- Teachers of Kazakh
- Translators
- NLP researchers (users of the exported dataset)

Which groups actually took part in the survey is reported in `docs/survey/` (TIL-8).

## 5. Aim

To build a web platform where users create and verify Kazakh language data (ru-kk sentence pairs and Kazakh terms) through micro-tasks and voting, with a **measurable data quality model**, and where only accepted data is used for the dictionary, daily practice and dataset export.

## 6. Objectives

1. Analyse existing systems and literature on crowdsourced language data and annotation quality (TIL-9, TIL-12, TIL-13).
2. Collect evidence of relevance from 3–5 real user representatives (TIL-8).
3. Specify functional and non-functional requirements with acceptance criteria (TIL-11).
4. Design the architecture and the data model (TIL-5, TIL-6).
5. Implement the collection and verification core with the data quality model.
6. Implement the terminology dictionary, the daily practice catalogue and the dataset export.
7. Evaluate the quality model against a simple baseline (TIL-7).

## 7. Solution overview

One end-to-end loop: a user's contribution, once accepted, immediately appears in the dictionary and in daily practice.

### Modules

1. **Collection and verification (core).** The system gives micro-tasks by domain (IT, medicine, engineering, everyday life). Task types:
   - translate a sentence ru → kk;
   - suggest one's own version of a sentence;
   - choose or suggest a Kazakh term.

   For terms, the variants are shown in random order without vote counts, plus a field for one's own variant. For translations, a user first writes their own translation "blind" and only then sees other users' variants.
2. **Daily practice.** A catalogue with the top words, the word of the day and hints on Kazakh connectors (және, сонымен, қысқасы, дегенмен). No exercises.
3. **Terminology dictionary.** Search, recommended variant, alternatives, domain, status (in voting / accepted).
4. **Export.** CSV or JSON, only from accepted records.

### Roles and data

- Roles: participant, reviewer, moderator/admin.
- Main entities: User, SourceSentence, Task, Contribution, Review, Term.
- Record statuses: `submitted`, `in_review`, `accepted`, `rejected`, `needs_edit`.

## 8. Data quality model

This model is what separates the project from a simple CRUD application.

### Decision rule

- Only "accept", "reject" and "edit" votes count; "don't know" does not.
- Each reviewer has a weight *w* from 0.5 to 2; a new reviewer starts with *w* = 1.
- A record needs at least 3 counted votes.
- For each decision, the weighted share is computed:
  - A = sum of weights for "accept" / sum of all weights
  - R = sum of weights for "reject" / sum of all weights
  - E = sum of weights for "edit" / sum of all weights
- If A ≥ 0.66, the record is **accepted**; if R ≥ 0.66, it is **rejected**; if E ≥ 0.66, it **needs editing** and a new version is created.
- *Proposed addition:* a decision is made only if at least 2 different people voted for it, so that one high-weight reviewer cannot decide alone.
- Otherwise one more reviewer is added, up to 5 votes; after that a moderator decides.

With three equal weights, 2 votes out of 3 give 0.67, so the simple "2 of 3" rule still holds. The threshold 0.66 is a parameter.

For **translations**, each variant is reviewed separately ("accept / reject / edit"). Choosing the best of several variants is used only for **terms**.

### Reviewer weight and control tasks

- A reviewer's weight grows when their votes match the final decision and decreases when they do not.
- Control tasks with a known answer are mixed into normal tasks to filter out random clicking.
- A reviewer cannot review their own contribution.
- *Proposed default values (to be fixed in the requirements, TIL-11):* +0.05 for a vote that matches the final decision, −0.10 for one that does not, +0.05 / −0.20 for a correct / wrong control task. With these values, random clicking among three options lowers the weight on average, while a reviewer who matches the decision in 80% of cases slowly gains weight.

All numeric values are configuration parameters, not hard-coded.

### Automatic checks

Kazakh letters present, text length, duplicates, Russian connectors.

### Agreement metric

The main agreement metric is **Krippendorff's alpha**, because it handles a different number of reviewers per record and missing votes. Cohen's kappa works only for two raters, and Fleiss' kappa needs the same number of raters for every record.

## 9. Expected outcomes

1. A working web application (MVP) with the collection and verification core, terminology dictionary, daily practice catalogue and export.
2. An exported dataset of accepted records in CSV and JSON.
3. An evaluation of the quality model against a baseline (simple majority without weights and without control tasks), as described in the verification plan (TIL-7).
4. Project documentation: requirements, architecture, diagrams, test plan.

## 10. Scope

### In scope

- Collection and verification core with the data quality model
- Terminology dictionary
- Daily practice catalogue (top words, word of the day, connector hints)
- CSV / JSON export of accepted records
- Basic points and ranking
- Optional basic AI feature (for example, duplicate search)

### Out of scope

- Audio collection
- A pilot with real users (removed from the original application)
- Mobile application
- Training our own AI models
- Complex achievements and gamification

## 11. Engineering complexity

The project is more than forms over a database:

- **Weighted consensus** with several outcomes, an escalation path (extra reviewers, then a moderator) and record versioning.
- **Reviewer reputation** that changes over time and depends on control tasks.
- **Bias control:** blind translation and random ordering of variants without vote counts.
- **Measurable quality:** inter-rater agreement (Krippendorff's alpha) and comparison with a baseline.
- **Data pipeline:** automatic checks, statuses and export of only accepted data.
- **Engineering practice:** Docker, CI with GitHub Actions, automated tests.

## 12. Why the scope is realistic

- Audio, a mobile app, model training and the pilot are explicitly out of scope.
- AI is optional and basic.
- Daily practice is a catalogue, not an exercise engine.
- The stack is one the team already uses: Python, Django / DRF, PostgreSQL, Docker, GitHub Actions; the frontend is planned as Vite + React (preliminary).
- Without a pilot, the quality model is evaluated on a small test: 5–10 people and 100–200 records with a reference labelling (for example, by a Kazakh teacher). If real votes are not available, a simulation of votes with known accuracy may be used, and it will be clearly labelled as a simulation.

## 13. Open questions

- **Source of Russian sentences** (Tatoeba, OPUS, Wikipedia): licences must be checked. Wikipedia text is CC BY-SA, so a derived dataset would also have to be ShareAlike. For the MVP, sources with simple attribution or our own sentences are safer. Tracked as a risk in TIL-4.
- **Dataset licence** (for example, CC BY) and user consent.
- **Exact reviewer weight rules and the "at least 2 people" rule:** to be fixed in the requirements (TIL-11).
- **Survey results and literature:** only real interviews (TIL-8) and sources the team has actually read (TIL-12, TIL-13).

## 14. Related documents

- Survey template: [`survey/template.md`](survey/template.md)
- Prototype (Figma): https://www.figma.com/design/qIYMTuvz3jta6YBrgxWRDp/Untitled?node-id=0-1
- YouTrack project: https://qosmuratsamat.youtrack.cloud/projects/TIL
