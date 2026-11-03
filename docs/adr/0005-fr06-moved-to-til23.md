# 0005. FR-06 (contributor permission) is implemented in TIL-23, not TIL-22

- **Status:** Accepted
- **Date:** 2026-11-02
- **Source:** TIL-22 (PR #19, YouTrack comment), decided by the tech lead when the TIL-22 task was written

## Context
TIL-22 lists FR-03 – FR-08, but its acceptance criteria do not include FR-06. FR-06 needs a stored
contributor permission for the publication terms, which the `User` model does not have yet, and it matters
mostly for export eligibility.

## Decision
FR-06 is implemented together with the export in TIL-23. Source provenance on `SourceSentence`
(original or licence + attribution) already exists and is not changed.

## Consequences
- TIL-22 did not change the `accounts` app or add migrations.
- TIL-23 must add the contributor permission, require it on submission, and exclude records without it from export.
