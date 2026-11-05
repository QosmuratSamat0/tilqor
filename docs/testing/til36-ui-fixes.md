# TIL-36: UI fixes and local verification

Date: 2026-11-06 (Asia/Qyzylorda). Task:
[TIL-36](https://qosmuratsamat.youtrack.cloud/issue/TIL-36), supplied as
`Downloads/TIL-36-task.md`. Branch: `TIL-36-ui-fixes`.
All four fixes were implemented and exercised locally. No production changes,
push or pull request were made.

## Feedback and API contracts

`CheckResult` contains pure `(code, params)` tuples for errors and warnings.
The submission service supplies the English messages for API clients. Warnings
are serialized as, for example:

```json
{"warnings":{"text_kk":[{"code":"russian_connectors","params":{"connectors":["и","но"]},"message":"Text contains Russian connector(s): и, но."}]}}
```

The shared `common.feedback` mechanism preserves existing error messages.
`FeedbackError.as_dict()` adds service-error codes; the DRF exception handler adds
the codes already carried by serializer and authentication errors. Field errors
and detail errors remain distinct:

```json
{"text_kk":["Text cannot exceed 1000 characters."],"codes":{"text_kk":["text_too_long"]},"params":{"text_kk":{"max_length":1000}}}
```

```json
{"detail":"This version is closed for review.","code":"review_closed"}
```

The frontend parses codes separately from messages and uses the shared
`shared/i18n/feedback.ts` translator. Required codes, normal conflict/load errors,
connector lists and maximum lengths have Russian translations. Unknown codes
fall back to their server message. The matching Kazakh keys remain empty for
TIL-28; the existing Russian fallback still applies.

Task detail includes `own_contribution: null` or `{id, status,
latest_version_number}` for the current user. A single query fetches their latest
version; translation visibility reuses that result. Detail needs at most three
queries, including visible variants; the task list retains two queries and does
not include this field. Anonymous API requests retain the existing 403 policy
with no own-contribution field; the selector returns null for an anonymous user.
Another authenticated user's detail returns null.

Successful submission updates the query cache and keeps a local submission
snapshot while refetching. The form disappears immediately, remains hidden after
a stale refetch or reload, and is replaced with a status badge and the
«Мои переводы» link. Success and warnings survive the immediate refetch. The same
rule hides an already-submitted term suggestion without removing term voting.

## Radios and review reasons

The decision radios already had wrapping labels and a fieldset/legend. This
markup was preserved; `ReviewPage.test.tsx` now asserts exact visible accessible
names through `getByRole("radio", {name: ...})` and the named group.

Term preference buttons became a native radio group. Labels contain only the
visible variant text, with author/status metadata outside the label. Native
checked indicators supplement color. Existing global `:focus-visible` outlines
apply to the input itself. Saving keeps radios enabled and queues writes in
order, preserving keyboard focus and preventing a late response from replacing
the latest choice. A regression test covers rapid choices and focus retention.

`ReviewReason` defines `wrong_term`, `russian_connector`, `grammar` and `other`.
Pure validation is shared by the serializer and locked service. Reject/edit
require a code; `other` requires a comment containing non-whitespace text;
accept/abstain prohibit a code. Two database constraints enforce these rules
even on direct writes. The admin includes the reason code in its list/filter.
The reason group and comment errors are linked to their fields through
`aria-describedby` and `aria-invalid`.

`decision_reasons` now contains `{code, comment}` objects, retaining only reasons
matching the final decision and deduplicating identical pairs. Moderator reasons
retain their free text and use a null code. The author UI translates the code and
also displays the comment, including code-only and moderator-only reasons.

Migration `verification.0004_review_reason_codes` assigns `other` to existing
reject/edit reviews without changing their comments. On rollback, a new coded
review without a comment receives its English reason label as legacy free text;
existing comments remain unchanged. The PostgreSQL test exercises both directions
on real rows. It caught deferred FK trigger events before the reverse column drop;
the migration now flushes those events before dropping the field.

The request/response contract changed: older clients must add `reason_code` to
reject/edit requests. The stored-data migration and the regenerated frontend
types accompany this change. No rollout was performed.

## Automated checks: actual output

Python 3.12.10, Django 5.2.18, local PostgreSQL 16. The final `make check` output
below omits only pytest's progress dots:

```text
make check
.venv\Scripts\python.exe -m ruff check src/backend tests
All checks passed!
.venv\Scripts\python.exe src/backend/manage.py makemigrations --check --dry-run
No changes detected
.venv\Scripts\python.exe -m pytest -q
395 passed in 152.34s (0:02:32)
```

The backend suite covers warning parameters, all seven required error codes,
own-submission privacy and query budgets, the decision × code × comment matrix
at the pure/API/service/DB boundaries, author reason objects, migration upgrade
and rollback, and the existing quality-model/concurrency tests.

`npm ci` completed before the frontend checks. Its output included:

```text
added 269 packages, and audited 270 packages in 32s
65 packages are looking for funding
10 moderate severity vulnerabilities
```

The dependency files were unchanged. `npm run api:types` regenerated
`src/shared/api/schema.d.ts` from `http://localhost:8000/api/schema/`.
Final frontend output (Vitest timing detail omitted):

```text
> tilqor-frontend@0.1.0 lint
> eslint .

> tilqor-frontend@0.1.0 typecheck
> tsc --noEmit

> tilqor-frontend@0.1.0 test
> vitest --run

 Test Files  11 passed (11)
      Tests  42 passed (42)

> tilqor-frontend@0.1.0 build
> tsc --noEmit && vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 131 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.49 kB │ gzip:   0.36 kB
dist/assets/index-BXwcDUGv.css   27.44 kB │ gzip:   4.66 kB
dist/assets/index-Dg1WCV64.js   387.07 kB │ gzip: 119.04 kB

✓ built in 487ms
```

The frontend suite exercises Russian warning/error interpolation and unknown-code
fallbacks, hidden forms after submission/reload/stale refetch, exact radio names
and group labels, required reasons/comments, author reason rendering, and equal
`ru.json`/`kk.json` key sets.

## Live local walkthrough

Started `docker compose up -d db backend` and `make fe-dev`. Chrome
156.0.8078.80 was driven through Playwright against the real Vite proxy and API,
using dedicated local fixture accounts; requests were not mocked. Two additional
local reviewer votes per target version finalized the actual weighted model.

The browser printed these successful checks:

```text
PASS: Russian warnings and success stay visible after refetch; submission form disappears
PASS: Reload preserves the submitted status and keeps the form hidden
PASS: Keyboard Tab/Space/arrows: Ваш выбор термина
PASS: Keyboard Tab/Space/arrows: Ваше решение
PASS: Keyboard Tab/Space/arrows: Причина решения
PASS: Edit + Other without comment shows a Russian error linked to the comment
PASS: Review API 201 and matching decision/reason/comment: edit/other
PASS: Review API 201 and matching decision/reason/comment: reject/russian_connector
PASS: Author sees translated categorical and commented reasons after actual weighted finalizations
```

The no-Kazakh-letter translation also contained `и`, producing both Russian
warnings. The author saw «Русская связка» and «Другое: Уточните формулировку.»
after finalization. API decisions, reason codes and comments matched the submitted
values; no API mismatch was found in these flows.

All radios in the three groups were reached and selected with Tab, Space and
arrow keys. The focused native input had a visible outline. The walkthrough
initially exposed focus loss when disabling the term fieldset during saving;
the queued-write fix was then verified by repeating the walkthrough.

Full-page captures of saved translation, term selection, required-comment error
and author reasons were inspected at 1440, 768 and 390 px. No horizontal overflow,
clipped controls or overlapping text appeared in those captures. This was desktop
Chrome with emulated viewport sizes; a physical mobile device and screen-reader
test were not performed. This evidence covers these scoped controls, not the
complete NFR-08 product audit or the production usability test TIL-29.
