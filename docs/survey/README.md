# User survey evidence

Task: [TIL-8 - User survey](https://qosmuratsamat.youtrack.cloud/issue/TIL-8).

Owner: Dovutbekov Ulykbek.

Status: 14 supplied survey-response records and an English summary prepared for team review. TIL-8 remains In Progress until review and outstanding metadata questions are resolved.

## Evidence and report

- [Response records](responses.md): dated records R1-R14 with reported roles, the observed questionnaire language, and answers transcribed in English from the multilingual form options.
- [Summary](summary.md): descriptive counts, verified findings, assumptions, limitations, and implications for requirements.
- [Actual questionnaire](questionnaire-used.md): English portions of the 16 questions used in the supplied form.
- [TIL-2 template](template.md): the original 11-question template, retained unchanged. The summary explains the differences from the used form.

All project documentation here is in English. English translations of Russian free comments are explicitly labelled. The original XLSX is retained outside Git; no JSON dataset or analysis code is required to read these Markdown deliverables.

## Collecting responses

Use the [TIL-2 template](template.md) for future collection. Record the actual language used; native language does not establish the language in which a person completed a survey.

1. Survey at least 3 real user representatives; aim for 5. Appropriate roles include students, teachers, translators, researchers, native speakers, and learners who use Kazakh in study or work.
2. Explain the diploma-project purpose and obtain permission to use anonymized answers in the project repository. Declining to answer is allowed. Do not publish a person's contact details, identifying chat screenshots, or answers without permission.
3. Add a respondent record only when recording an actual response. A blank questionnaire is not a response and must not be counted.
4. Enter the real survey date, role, method, language, and consent. Preserve source meaning and explicitly label translations or use of English portions of multilingual options. Mark an unanswered question as `Not answered`; do not fill gaps or infer missing feature ratings.
5. Review each record against the source supplied by the respondent. Preserve consent and source evidence outside the public repository when it contains personal information; do not invent source references.
6. Update the [summary](summary.md) using only eligible completed response records. Link findings to respondent IDs and question numbers. Keep verified findings and assumptions separate.

## Analysing the evidence

A verified finding must be supported by several real respondents, as required by TIL-2. A single person's statement may be reported as an individual observation, with its source, without generalizing it to the sample. Contradictory answers and missing data must remain visible.

For any count, state the question's actual number of answers. For feature ratings, report the number of ratings and the calculation used; missing ratings are not zero. Report willingness to participate as stated intention, not observed participation. Explain which requirement or product decision each supported finding affects, including a decision to retain the current scope. Record unsupported ideas as assumptions.

## Completion checklist

- [x] The supplied export contains 14 response records, exceeding the numerical target of 3-5; identities were not independently authenticated.
- [x] Every record has its actual recorded date, reported role, and the observed trilingual questionnaire language.
- [ ] The owner has clarified any required individual completion-language metadata and consent evidence, which are not recorded in the export.
- [x] Answers are based on the supplied source, with missing cells and English transcriptions/translations labelled.
- [x] The summary separates verified findings from assumptions and links evidence to the response records.
- [x] Sample limits, unknown recruitment details, contradictory answers, questionnaire differences, and implications for requirements are reported.
- [ ] A different team member reviews the evidence and summary in the PR.
- [ ] The PR or commit is linked from TIL-8 before marking the task complete.
