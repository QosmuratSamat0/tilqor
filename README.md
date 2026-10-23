# Tilqor

**Development of a crowdsourcing platform for collecting and verifying Kazakh language data, with daily practice and terminology dictionary modules.**

Tilqor is a web platform where people translate Russian sentences into Kazakh and choose or suggest Kazakh variants of terms, while other users review and vote. Only records accepted by a measurable data quality model go into the terminology dictionary, the daily catalogue (top words, word of the day, Kazakh connector hints) and an exportable dataset (CSV / JSON).

Diploma project, group SE-2430. *Tilqor is a working name.*

- YouTrack project: https://qosmuratsamat.youtrack.cloud/projects/TIL
- Prototype (Figma): https://www.figma.com/design/qIYMTuvz3jta6YBrgxWRDp/Untitled?node-id=0-1

## Problem

- There is little **verified** Kazakh–Russian text data, so Kazakh NLP models lack training and evaluation data.
- In IT, medicine and engineering there are often no single accepted Kazakh terms, and Russian connectors ("короче", "но") are common in Kazakh speech and writing.
- Existing systems solve only parts of the problem: KSC and Common Voice collect speech, termincom.kz approves terms top-down through a commission, and dictionaries such as sozdikqor.kz are for lookup only ([system comparison](docs/systems-comparison.md)).

Survey evidence (14 responses, 2026-10-23, [results](docs/survey/results.md)): 11 of 14 respondents rate a terminology glossary as important or critically important, 10 of 14 find Kazakh connector hints useful, and 8 of 14 prefer community voting with expert review of disputed cases. The sample is small and exploratory.

## Target users

- Native speakers and learners of Kazakh
- Students and teachers
- Translators
- NLP researchers who use the exported dataset

## Expected outcomes

1. A working web application (MVP): contribution and verification core, terminology dictionary, daily catalogue and export.
2. An exported dataset of accepted ru–kk records in CSV and JSON.
3. An evaluation of the quality model against a simple majority baseline ([verification plan](docs/verification-plan.md)).
4. Project documentation: requirements, architecture, diagrams and test plan.

## Scope

**In scope:** contribution and verification core with the data quality model (reputation-weighted voting, control tasks, Krippendorff's alpha), terminology dictionary, daily catalogue, CSV / JSON export of accepted records, basic points and ranking, an optional basic AI feature (duplicate search).

**Out of scope:** audio, a mobile app, a pilot with real users, training our own AI models, exercises and complex gamification.

Details: [proposal](docs/proposal.md), sections 10–12.

## Current status

**Stage: pre-defense-1 (2026-10-24).** Analysis, design and planning are done; there is no runnable code yet.

| Done | Next (pre-defense-2) |
|---|---|
| Proposal, literature review, system and technology comparisons | Backend core: accounts, tasks, contributions, review queue |
| Requirements with acceptance criteria (26 functional, 12 non-functional) | Quality model (decision rule, reputation, control tasks) with unit tests in CI |
| Architecture and diagrams, Figma prototype | First evaluation run on a frozen dataset |
| User survey (14 responses), risks and milestones, verification plan | |

## Team

| Member | Role | Responsibilities |
|---|---|---|
| Kosmurat Samat | Tech lead, architect | Architecture, data quality model, DevOps, optional AI features, repository and YouTrack |
| Alpamys Abylaikhan | Analyst, UX lead and developer | Existing system comparison, prototype and user scenarios, README, literature review |
| Dovutbekov Ulykbek | Requirements and research lead, developer | User survey, requirements and acceptance criteria, risks and milestones, literature sources |

Supervisor: **Latuta Konstantin Nikolaevich**.

## Technologies

| Part | Choice | Why |
|---|---|---|
| Backend | Python, Django + Django REST Framework | ORM, migrations, transactions, auth and admin built in |
| Database | PostgreSQL | Relational data, transactions for voting, trigram search for the dictionary |
| Frontend | Vite + React (preliminary) | Interactive screens over a REST API |
| Infrastructure | Docker, GitHub Actions | Same environment for everyone; tests on every pull request |

Comparison of alternatives: [technology comparison](docs/tech-comparison.md).

## Documentation

| Document | Content |
|---|---|
| [Proposal](docs/proposal.md) | Problem, users, aim, objectives, scope, quality model |
| [Literature review](docs/literature-review.md) | Critical review and analysis table of the sources |
| [Existing system comparison](docs/systems-comparison.md) | 5 systems compared against common criteria |
| [Technology comparison](docs/tech-comparison.md) | Server, storage, component interaction, frontend |
| [Requirements](docs/requirements.md) | Functional and non-functional requirements, priorities, acceptance criteria |
| [Architecture](docs/architecture.md) | Components, data flow, traceability to requirements |
| [Verification plan](docs/verification-plan.md) | Tests, metrics, measurement conditions, baseline |
| [Risks and milestones](docs/risks.md) | Risks, milestones, dependencies, responsibilities |
| [Survey results](docs/survey/results.md) | 14 responses, verified findings and assumptions |
| [Survey template](docs/survey/template.md) | Original questionnaire (TIL-2) |

Diagrams (PlantUML sources in [`diagrams/src`](diagrams/src), images in [`diagrams/png`](diagrams/png)):
[system context](diagrams/png/context.png) · [use cases](diagrams/png/use-case.png) · [components](diagrams/png/components.png)

## Prototype

Interactive prototype in Figma: https://www.figma.com/design/qIYMTuvz3jta6YBrgxWRDp/Untitled?node-id=0-1

The prototype shows the key user scenarios of the MVP. It is a design mock-up: no data is saved and the quality model is not running behind it.

### Screens

| Screen | What the user does | Requirements |
|---|---|---|
| Home | Sees the daily goal (10 short tasks) and progress; chooses a domain (IT, medicine, engineering, everyday life); sees the word of the day, top words of the week and Kazakh connector hints | FR-03, FR-19 |
| Term contribution | Sees a Russian term with its definition and Kazakh variants in random order without vote counts; chooses one, suggests their own or skips | FR-05 |
| Review | Reviews another user's ru → kk sentence translation: correct, wrong, edit or "don't know"; chooses a reason if wrong; sees own reliability (share of votes matching the final decision) and the rules: author hidden, no self-review, control tasks | FR-09, FR-10, FR-14, FR-15 |
| Dictionary | Searches for a term and filters by domain; sees the recommended variant, alternatives, domain and status (in voting / accepted); exports to CSV; suggests a missing term | FR-17, FR-18, FR-20 |

### Key scenarios

1. **Contribute a term:** Home → choose a task → Term contribution → choose a variant or suggest a new one → the contribution goes to review.
2. **Review a translation:** Home → Review → choose correct / wrong / edit / "don't know". After enough votes, the system makes a weighted decision (see [requirements](docs/requirements.md), section 4).
3. **Find a term:** Home → Dictionary → search → open the entry with the recommended variant and its alternatives.

### Not shown in the prototype

- Blind sentence translation ru → kk (FR-04) and the status of own submissions (FR-08)
- Moderator screens: escalated records, tasks, settings (FR-12, FR-21, FR-24)
- JSON export (FR-20; the prototype shows CSV only)

These are described in the [requirements](docs/requirements.md) and the [use case diagram](diagrams/png/use-case.png) and will be designed in the next stage.

## Setup, run and test

There is no runnable code yet. Setup, execution and testing instructions will be added here together with the first runnable version (planned for pre-defense-2). Configuration will use [`config.example.env`](config.example.env) with placeholder values; the real `.env` is never committed.

To regenerate the diagram images (requires Docker):

```bash
docker run --rm -v "$PWD/diagrams:/data" plantuml/plantuml -tpng -o /data/png /data/src/context.puml /data/src/use-case.puml /data/src/components.puml
```

## Repository structure

- `docs/`: proposal, literature review, comparisons, requirements, architecture, verification plan, risks, survey
- `diagrams/`: PlantUML sources (`src/`) and images (`png/`)
- `src/`: application code (empty until implementation starts)
- `tests/`: automated tests (empty until implementation starts)
- `config.example.env`: example settings with placeholder values

## Git rules

- Every piece of work has a task in [YouTrack](https://qosmuratsamat.youtrack.cloud/projects/TIL) (project TIL).
- Branch `TIL-N-short-name`, commit message `TIL-N: description`.
- Changes reach `main` only via a pull request reviewed by another team member.
- No passwords, tokens or personal data in the repository.
- Each pre-defense submission is tagged: `pre-defense-1`, `pre-defense-2`, `final-pre-defense`.
