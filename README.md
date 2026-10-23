# Tilqor

A crowdsourcing platform for collecting and verifying Kazakh language data, with daily practice and terminology dictionary modules.

Diploma project, group SE-2430.

## Team
- Kosmurat Samat: tech lead
- Alpamys Abylaikhan
- Dovutbekov Ulykbek

Supervisor: Konstantin N. Latuta.

## Repository structure
- docs/: proposal, requirements, literature review, comparisons, verification plan, risks
- diagrams/: diagram sources (src/) and images (png/)
- src/: code (empty for now)
- tests/: tests (empty for now)
- config.example.env: example settings; never commit the real .env

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

## Git rules
- Every piece of work has a task in YouTrack (project TIL).
- Branch TIL-N-short-name, commit message TIL-N: description.
- Changes reach main only via a PR reviewed by another team member.
- No passwords or tokens in the repository.