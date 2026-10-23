# User survey evidence

Task: [TIL-8 - User survey](https://qosmuratsamat.youtrack.cloud/issue/TIL-8).

Owner: Dovutbekov Ulykbek.

Status: preparation only. No completed response records have been supplied in this directory. This does not establish whether interviews took place elsewhere. TIL-8 remains In Progress until real responses and their summary meet its acceptance criteria.

## Collecting responses

Use the [TIL-2 template](template.md). A [Russian questionnaire](questionnaire-ru.md) provides the same eleven questions and six feature ratings for Russian-speaking respondents. Record the actual language used; Russian questionnaire text alone does not establish a respondent's language.

1. Survey at least 3 real user representatives; aim for 5. Appropriate roles include students, teachers, translators, researchers, native speakers, and learners who use Kazakh in study or work.
2. Explain the diploma-project purpose and obtain permission to use anonymized answers in the project repository. Declining to answer is allowed. Do not publish a person's contact details, identifying chat screenshots, or answers without permission.
3. Copy the questionnaire to `responses/R1.md`, `responses/R2.md`, and so on only when recording an actual respondent. A blank questionnaire is not a response and must not be counted.
4. Enter the real survey date, role, method, language, and consent. Record answers in the language and wording supplied. Mark an unanswered question as `Not answered`; do not fill gaps or infer missing feature ratings. Keep any translation separately labelled.
5. Review each record against the source supplied by the respondent. Preserve consent and source evidence outside the public repository when it contains personal information; do not invent source references.
6. Update the [summary](summary.md) using only eligible completed response records. Link findings to respondent IDs and question numbers. Keep verified findings and assumptions separate.

## Analysing the evidence

A verified finding must be supported by several real respondents, as required by TIL-2. A single person's statement may be reported as an individual observation, with its source, without generalizing it to the sample. Contradictory answers and missing data must remain visible.

For any count, state the question's actual number of answers. For feature ratings, report the number of ratings and the calculation used; missing ratings are not zero. Report willingness to participate as stated intention, not observed participation. Explain which requirement or product decision each supported finding affects, including a decision to retain the current scope. Record unsupported ideas as assumptions.

## Completion checklist

- [ ] At least 3 real respondents are documented; the actual count is reported, including any shortfall from the target of 5.
- [ ] Every counted response includes an actual date, role, survey language, and permission to use its anonymized answers.
- [ ] Answers are based on the real source, with omissions and any translations labelled.
- [ ] The summary separates verified findings from assumptions and links evidence to the response records.
- [ ] Recruitment method, sample limits, contradictory answers, and implications for requirements are reported.
- [ ] A different team member reviews the evidence and summary in the PR.
- [ ] The PR or commit is linked from TIL-8 before marking the task complete.
