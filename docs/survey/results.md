# User survey results

Task: [TIL-8](https://qosmuratsamat.youtrack.cloud/issue/TIL-8).

Owner: Dovutbekov Ulykbek.

Report prepared: 2026-10-23. Status: evidence and analysis prepared for team review; final task acceptance is pending.

The supplied form export contains **14 response records**, all dated **2026-10-23**. Within this sample, 11 respondents rate a terminology glossary as important or critically important, and 10 select Kazakh connector hints as useful. Approval preferences are divided: 8 select community votes with expert review of disputes, 5 select experts and official sources only, and 1 is unsure. These findings support retaining the glossary, connector hints, and moderation; they do not validate the numerical quality model.

## Source and method

The owner supplied an XLSX export of the [survey response spreadsheet](https://docs.google.com/spreadsheets/d/14VbiQaXCewkmilObIvh0kajZpsctBWbssDoAFLjBjjY/edit#gid=1492786306). The worksheet is named `Ответы на форму (1)` in the source. Row 1 contains the timestamp and 16 question headers; rows 2-15 contain the 14 responses. The original workbook remains outside Git.

Source workbook SHA-256: `7590fa3d6c6a9d32212d09bd584f4bdb6c1c12e16c59a46c0ac0a8b98d2ea4b2`.

[Response records](#response-records) assign R1-R14 in source-row order and identify the source cells. English parts of multilingual option labels are transcribed without changing the selected options. Russian free comments are translated and labelled; blank comments remain missing answers. The recorded date is preserved without timezone conversion: the exported timestamps contain no timezone offset. Exact times are not published.

The source contains no names, emails, or phone numbers. Recruitment channels, invitation counts, response rate, consent wording, and individual identity checks were not supplied. The records are the survey responses supplied by the owner; independent proof of 14 unique identities is not claimed. There are no identical complete answer vectors, but this does not establish unique participation.

## Respondents and method

The sample comprises 6 teachers/educators (R2, R6, R7, R8, R10, R12), 3 students (R3, R9, R13), 2 IT professionals/developers (R1, R11), 1 researcher/academic (R4), and 2 respondents reporting Other (R5, R14). All have a recorded survey date of 2026-10-23 and are listed individually in [response records](#response-records).

Every question and predefined answer appears together in **English, Kazakh, and Russian**. This trilingual form is recorded as the questionnaire language for each respondent. An individual's chosen reading/completion language is not captured. Q2 asks native language and must not be used to infer completion language. The owner should clarify this distinction with the reviewer if individual completion language is required for acceptance.

Native-language answers are Kazakh (9), Russian (4), and bilingual Kazakh/Russian (1). Self-reported Kazakh proficiency is native speaker (10), beginner (3), and intermediate (1). These are distinct from questionnaire language. The method is a form-response survey; recruitment details and individual consent evidence are not present in the export.

Each of Q1-Q15 has 14 recorded answers. Q16 has 3 answers and 11 blanks. No response is excluded or imputed. Multi-select counts use the 14 answers to that question as the denominator and may overlap.

## Verified findings

Under TIL-2, a verified finding is supported by several recorded responses. Here, verified means supported within this sample; it does not establish population-wide prevalence, observed behaviour, or system performance. Question numbers refer to the [actual form](#questionnaire-used-in-the-survey).

| ID | Verified finding | Supporting records | Contrary evidence or qualification |
|---|---|---|---|
| V1 | 13/14 report terminology problems at least rarely; 9/14 report them occasionally or very often. | Q5: occasionally R2, R3, R4, R5, R9, R10, R11, R13; very often R6; rarely R1, R7, R12, R14. | R8 answers never. No independently checked examples of incorrect terms were collected. |
| V2 | 11/14 rate the glossary important or critically important. | Q11: important R2, R5, R8, R9, R12; critically important R4, R6, R7, R10, R13, R14. | R1 and R3 say not important; R11 is neutral. |
| V3 | 10/14 select connector hints as useful, and 8/14 report often inserting Russian connectors. | Q9 hints: R1, R2, R5, R6, R7, R9, R10, R11, R12, R14. Q10 often: R1, R2, R3, R4, R5, R6, R8, R9. | These are distinct respondent sets. Q10 also has sometimes (3), rarely (2), and never (1). No learning effect was measured. |
| V4 | Error reporting (9/14) and validation (6/14) are selected more often than new submissions (3/14). | Q6 reporting: R2, R3, R4, R6, R7, R9, R10, R11, R14; validation: R2, R5, R7, R10, R13, R14; submissions: R12, R13, R14. | Multi-select willingness is not actual contribution volume. R11 also selects use without contribution. |
| V5 | 8/14 prefer community votes with expert dispute review; 5/14 prefer experts/official sources only. | Q13 hybrid: R2, R4, R5, R7, R8, R9, R12, R14; experts only: R1, R3, R6, R11, R13. | R10 is unsure. Unrestricted community approval is not established as a shared preference. |
| V6 | 11/14 express moderate or extreme interest in daily practice; 3/14 expect daily platform use. | Q8 moderate: R2, R5, R8, R9, R12, R13, R14; extreme: R3, R6, R7, R10. Q15 daily: R5, R7, R13. | Q8 also has slightly interested (2) and not interested (1). Q15 also has weekly or less (7), specific lookups only (3), and 2-3 times weekly (1). These are intentions. |
| V7 | 11/14 would choose a supplied term variant, with 5 also proposing their own. | Q7 choose and propose: R2, R5, R6, R7, R13; choose only: R3, R4, R9, R10, R12, R14. | R1 and R11 would view results only; R8 would not participate. The scenario is hypothetical. |

## Individual observations

R11 selects both error reporting and use without contributing in Q6. Both selections are retained; neither is corrected or removed. R11 also selects connector hints while reporting never using Russian connectors; that combination is retained and is not by itself proof of an error.

Q16 has two Russian negative comments (R9 and R14), translated as No in the response records, and the English comment Everything is fine (R13). The other 11 comments are blank. These comments contain no specific additional feature request and do not establish general satisfaction.

## Assumptions

| ID | Assumption not established by the responses | Evidence gap and next check |
|---|---|---|
| A1 | Weighted verification, the 0.66 threshold, two-person rule, weight changes, and control tasks improve quality over majority voting. | Q13 measures approval preference, not algorithm accuracy. Evaluate the model using reference labels and the TIL-7 baseline. |
| A2 | Interest or selected incentives will produce regular contributions and retention. | Q6, Q8, Q14, and Q15 record intentions. Observe actual behaviour in a bounded test. |
| A3 | Connector hints or daily content improve language proficiency. | Q9 measures stated usefulness; no learning outcomes were measured. |
| A4 | These responses represent all target users or establish dataset-export demand. | Recruitment is unknown, target roles are unevenly covered, and dataset download was not asked. Obtain targeted evidence before making these claims. |

## Feature ratings

The used form does not collect TIL-2's six 1-5 feature ratings. Its categorical answers and multi-select selections cannot be converted into those ratings. No mean rating or fabricated score is reported. Each count below has denominator 14, and selections within each question are non-exclusive.

| Daily-use selection (Q9) | Count | Respondents |
|---|---|---|
| Kazakh connector hints | 10/14 | R1, R2, R5, R6, R7, R9, R10, R11, R12, R14 |
| Short vocabulary quizzes | 6/14 | R3, R6, R7, R8, R12, R13 |
| Word of the day with an example | 4/14 | R3, R5, R10, R13 |
| Most-used-word list | 4/14 | R3, R9, R13, R14 |
| Flashcards with new terms | 2/14 | R4, R7 |

| Glossary domain (Q12) | Count |
|---|---|
| Science and engineering | 9/14 |
| Legal and administrative | 9/14 |
| IT and software | 8/14 |
| Business and economics | 6/14 |
| General everyday modern terms | 6/14 |

| Stated incentive (Q14) | Count |
|---|---|
| Badges, streaks, and achievements | 8/14 |
| Public leaderboards and rankings | 6/14 |
| Official contribution certificates | 6/14 |
| Visibility of contribution impact | 5/14 |

The [individual records](#response-records) preserve the selections underlying the domain and incentive counts. These answers do not prove that any incentive causes engagement.

## Implications for requirements

The requirement IDs below refer to the TIL-11 specification proposed in [PR #6](https://github.com/QosmuratSamat0/tilqor/pull/6). These are recommendations for team review, not claims of approved changes or implemented features.

| Evidence | Proposed decision | Requirement trace |
|---|---|---|
| V1, V2 | Retain the dictionary, accepted status, and source presentation. | FR-17, FR-18 |
| V3 and Q9 | Retain connector hints, top words, and word of the day at the proposed catalogue scope. | FR-19 |
| V4, V7 | Keep term selection and independent review easy to reach; do not assume most users will submit original content. | FR-05, FR-09, FR-10 |
| V5 | Retain dispute escalation; discuss the experts-only preference and expert qualification policy. | FR-12, FR-16 |
| A1 | Keep numerical quality settings labelled as engineering defaults and evaluate them against the baseline. | FR-11, FR-14, FR-15, FR-24, FR-25, FR-26 |
| Q14, A2 | Keep basic ranking as Should; avoid adding complex gamification, streaks, or certificates to the MVP. | FR-22; proposal scope exclusions |
| A4 | Keep export justified by the proposal; do not describe it as survey-validated demand. | FR-20 |

Quizzes and flashcards were selected by 6 and 2 respondents respectively. Record this interest without expanding the daily catalogue into an exercise engine.

## Relationship to TIL-2

The actual survey is a 16-question adaptation of the [11-question template](template.md). The differences are material and are recorded rather than filled with invented answers.

| Template topic | Used-form evidence | Coverage limitation |
|---|---|---|
| Respondent date, role, method, language, consent | Timestamp, Q1, form export, trilingual headers/options | Individual completion language and consent records are absent. |
| B1: writing/translation frequency | Q4: digital Kazakh use | Related measure, not specifically writing or translation. |
| B2: current tools/dictionaries | Not asked | No current-tool usage claims. |
| B3: inconveniences | Q5: terminology problems | Narrower than the open-ended template question. |
| B4: competing terms and choice | Q7: hypothetical scenario | No actual past example or current choice method. |
| C5: willingness to contribute | Q6, Q7 | Intentions, not observed participation. |
| C6: minutes per day | Not asked; Q15 asks visit frequency | Frequency cannot be converted into minutes. |
| C7: motivation | Q14 | Multi-select proposed incentives. |
| C8: trust in voting | Q13: approval-model preference | Related governance preference, not a direct trust score. |
| C9: six feature ratings | Q8, Q9, Q11, Q12 | Categorical interest and selections; no six-feature 1-5 ratings or dataset-download question. |
| C10: concerns | Not directly asked | No concerns or reasons for distrust reconstructed. |
| D11: free comment | Q16 | 3 answers and 11 blanks. |

## Limitations

This is a small exploratory sample with teachers accounting for 6/14 responses. Recruitment method and response rate are unknown. Other roles are unspecified, and the researcher category does not establish NLP specialization. No professional translator category is recorded. Anonymous rows cannot independently establish one-person-one-response compliance.

The form's multilingual option labels do not reveal individual reading language, and the workbook does not contain consent records. The organizer should retain the original form introduction and clarify those details if needed for acceptance. No affirmative consent or language choice is fabricated. Native language and comment language are not substitutes for completion language.

The numerical response target is exceeded, but this does not establish representativeness, eliminate questionnaire differences, prove implementation quality, or replace the TIL-7 evaluation.

## Review and completion

The evidence and summary are ready for team review. The owner should resolve the metadata and questionnaire-coverage questions above with the reviewer before TIL-8 is marked done. A report or PR alone is not approval.

## Questionnaire used in the survey

Survey form: [Open the original questionnaire](https://forms.gle/X2LuCQrKMEGaQosS8).

These are the English portions of the actual 16 question headers in the supplied workbook. Every header is displayed together in English, Kazakh, and Russian in the original form. This differs from the [11-question TIL-2 template](template.md); see the [coverage comparison](#relationship-to-til-2).

### Q1
1. Which category best describes your primary occupation or background?

### Q2
2. What is your native language?

### Q3
3. How would you rate your proficiency in the Kazakh language?

### Q4
4. How often do you use the Kazakh language in digital environments (apps, websites, documents)?

### Q5
5. How often do you encounter missing, confusing, or incorrect terminology in modern Kazakh digital content?

### Q6
6. In what ways would you be willing to contribute to Data Collection & Verification? (You can select multiple)

### Q7
7. You are shown a term (e.g., "cache") and several options in Kazakh. What would you do?

### Q8
8. How interested would you be in a Daily Language Practice module?

### Q9
9. What would you find useful every day? (You can select multiple)

### Q10
10. Do you ever insert Russian connectors ("koroche", "no", "to est") into Kazakh speech or text?

### Q11
11. How important is a centralized, community-driven Terminology Glossary for technical, scientific, and IT terms?

### Q12
12. Which subject areas need a Terminology Glossary the most? (You can select multiple)

### Q13
13. How do you think new Kazakh terms should best be approved?

### Q14
14. What incentives or gamification features would motivate you to stay active on the platform? (You can select multiple)

### Q15
15. How often do you expect to visit and use this platform once launched?

### Q16
16. Do you have any additional suggestions, comments, or feature requests?

## Response records

These 14 records are transcribed from rows 2-15 of the supplied form-response workbook. IDs follow source row order. The date is taken from the timestamp without timezone conversion; the export does not specify a timezone. The source workbook and SHA-256 hash are documented in the [summary](#source-and-method).

Questions and option labels in the actual form are shown together in English, Kazakh, and Russian. This English record uses the English part of each selected option, preserving the selections and any contradictions. The shortened connector-hint label omits only its illustrative language examples. Free comments are translated only where explicitly stated. No missing answer is supplied. The actual language read by each respondent and consent records are not captured by the export; native language is not a substitute.

Question numbers refer to the [actual 16-question form](#questionnaire-used-in-the-survey), not the 11-question TIL-2 template. Column A holds the timestamp; question Q1 is in column B and Q16 is in column Q.

### R1
| Field | Recorded value |
|---|---|
| Source cells | A2:Q2 |
| Survey date | 2026-10-23 |
| Role (Q1) | IT Professional / Developer |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Russian |
| Q3 | Beginner |
| Q4 | Never |
| Q5 | Rarely |
| Q6 | I would only use the platform without contributing |
| Q7 | Only viewed the results |
| Q8 | Not interested |
| Q9 | Tips on which Kazakh connective to use instead of Russian |
| Q10 | Often |
| Q11 | Not important |
| Q12 | Legal & Administrative |
| Q13 | Only experts and official sources |
| Q14 | Public leaderboards and rankings; Badges, streaks, and achievements; Official certificates of contribution; Contribution impact visibility |
| Q15 | Only when looking up specific terms |
| Q16 | Not answered (blank source cell). |

### R2
| Field | Recorded value |
|---|---|
| Source cells | A3:Q3 |
| Survey date | 2026-10-23 |
| Role (Q1) | Teacher / Educator |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Bilingual (Kazakh & Russian) |
| Q3 | Native speaker |
| Q4 | Daily |
| Q5 | Occasionally |
| Q6 | Validating existing terms and translations; Reporting translation errors and bugs |
| Q7 | Chose the best and proposed my own |
| Q8 | Moderately interested |
| Q9 | Tips on which Kazakh connective to use instead of Russian |
| Q10 | Often |
| Q11 | Important |
| Q12 | Information Technology & Software; Science & Engineering; Business & Economics; Legal & Administrative; General everyday modern terms |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Contribution impact visibility |
| Q15 | Once a week or less |
| Q16 | Not answered (blank source cell). |

### R3
| Field | Recorded value |
|---|---|
| Source cells | A4:Q4 |
| Survey date | 2026-10-23 |
| Role (Q1) | Student |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Rarely |
| Q5 | Occasionally |
| Q6 | Reporting translation errors and bugs |
| Q7 | Only chose from ready options |
| Q8 | Extremely interested |
| Q9 | Word of the day with an example; List of most used words; Short vocabulary quizzes |
| Q10 | Often |
| Q11 | Not important |
| Q12 | Business & Economics; Legal & Administrative; General everyday modern terms |
| Q13 | Only experts and official sources |
| Q14 | Badges, streaks, and achievements |
| Q15 | Once a week or less |
| Q16 | Not answered (blank source cell). |

### R4
| Field | Recorded value |
|---|---|
| Source cells | A5:Q5 |
| Survey date | 2026-10-23 |
| Role (Q1) | Researcher / Academic |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Rarely |
| Q5 | Occasionally |
| Q6 | Reporting translation errors and bugs |
| Q7 | Only chose from ready options |
| Q8 | Slightly interested |
| Q9 | Flashcards with new terms |
| Q10 | Often |
| Q11 | Critically important |
| Q12 | General everyday modern terms |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Official certificates of contribution |
| Q15 | Once a week or less |
| Q16 | Not answered (blank source cell). |

### R5
| Field | Recorded value |
|---|---|
| Source cells | A6:Q6 |
| Survey date | 2026-10-23 |
| Role (Q1) | Other |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Russian |
| Q3 | Intermediate |
| Q4 | Several times a week |
| Q5 | Occasionally |
| Q6 | Validating existing terms and translations |
| Q7 | Chose the best and proposed my own |
| Q8 | Moderately interested |
| Q9 | Word of the day with an example; Tips on which Kazakh connective to use instead of Russian |
| Q10 | Often |
| Q11 | Important |
| Q12 | Information Technology & Software; Science & Engineering; Legal & Administrative |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Official certificates of contribution; Contribution impact visibility |
| Q15 | Daily (for practice and contributions) |
| Q16 | Not answered (blank source cell). |

### R6
| Field | Recorded value |
|---|---|
| Source cells | A7:Q7 |
| Survey date | 2026-10-23 |
| Role (Q1) | Teacher / Educator |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Daily |
| Q5 | Very often |
| Q6 | Reporting translation errors and bugs |
| Q7 | Chose the best and proposed my own |
| Q8 | Extremely interested |
| Q9 | Tips on which Kazakh connective to use instead of Russian; Short vocabulary quizzes |
| Q10 | Often |
| Q11 | Critically important |
| Q12 | Information Technology & Software; Science & Engineering; Legal & Administrative |
| Q13 | Only experts and official sources |
| Q14 | Public leaderboards and rankings |
| Q15 | 2-3 times a week |
| Q16 | Not answered (blank source cell). |

### R7
| Field | Recorded value |
|---|---|
| Source cells | A8:Q8 |
| Survey date | 2026-10-23 |
| Role (Q1) | Teacher / Educator |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Daily |
| Q5 | Rarely |
| Q6 | Validating existing terms and translations; Reporting translation errors and bugs |
| Q7 | Chose the best and proposed my own |
| Q8 | Extremely interested |
| Q9 | Tips on which Kazakh connective to use instead of Russian; Short vocabulary quizzes; Flashcards with new terms |
| Q10 | Sometimes |
| Q11 | Critically important |
| Q12 | Information Technology & Software; Science & Engineering; Business & Economics; Legal & Administrative; General everyday modern terms |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Badges, streaks, and achievements; Official certificates of contribution; Contribution impact visibility |
| Q15 | Daily (for practice and contributions) |
| Q16 | Not answered (blank source cell). |

### R8
| Field | Recorded value |
|---|---|
| Source cells | A9:Q9 |
| Survey date | 2026-10-23 |
| Role (Q1) | Teacher / Educator |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Daily |
| Q5 | Never |
| Q6 | I would only use the platform without contributing |
| Q7 | Would not participate |
| Q8 | Moderately interested |
| Q9 | Short vocabulary quizzes |
| Q10 | Often |
| Q11 | Important |
| Q12 | Information Technology & Software; Science & Engineering; Business & Economics |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Contribution impact visibility |
| Q15 | Only when looking up specific terms |
| Q16 | Not answered (blank source cell). |

### R9
| Field | Recorded value |
|---|---|
| Source cells | A10:Q10 |
| Survey date | 2026-10-23 |
| Role (Q1) | Student |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Rarely |
| Q5 | Occasionally |
| Q6 | Reporting translation errors and bugs |
| Q7 | Only chose from ready options |
| Q8 | Moderately interested |
| Q9 | List of most used words; Tips on which Kazakh connective to use instead of Russian |
| Q10 | Often |
| Q11 | Important |
| Q12 | Legal & Administrative |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Public leaderboards and rankings; Badges, streaks, and achievements |
| Q15 | Once a week or less |
| Q16 | No. (English translation of the recorded Russian comment.) |

### R10
| Field | Recorded value |
|---|---|
| Source cells | A11:Q11 |
| Survey date | 2026-10-23 |
| Role (Q1) | Teacher / Educator |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Several times a week |
| Q5 | Occasionally |
| Q6 | Validating existing terms and translations; Reporting translation errors and bugs |
| Q7 | Only chose from ready options |
| Q8 | Extremely interested |
| Q9 | Word of the day with an example; Tips on which Kazakh connective to use instead of Russian |
| Q10 | Rarely |
| Q11 | Critically important |
| Q12 | Information Technology & Software; Science & Engineering; General everyday modern terms |
| Q13 | Unsure |
| Q14 | Public leaderboards and rankings; Badges, streaks, and achievements |
| Q15 | Once a week or less |
| Q16 | Not answered (blank source cell). |

### R11
| Field | Recorded value |
|---|---|
| Source cells | A12:Q12 |
| Survey date | 2026-10-23 |
| Role (Q1) | IT Professional / Developer |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Russian |
| Q3 | Beginner |
| Q4 | Rarely |
| Q5 | Occasionally |
| Q6 | Reporting translation errors and bugs; I would only use the platform without contributing |
| Q7 | Only viewed the results |
| Q8 | Slightly interested |
| Q9 | Tips on which Kazakh connective to use instead of Russian |
| Q10 | Never |
| Q11 | Neutral |
| Q12 | Science & Engineering; Business & Economics |
| Q13 | Only experts and official sources |
| Q14 | Badges, streaks, and achievements; Official certificates of contribution |
| Q15 | Only when looking up specific terms |
| Q16 | Not answered (blank source cell). |

### R12
| Field | Recorded value |
|---|---|
| Source cells | A13:Q13 |
| Survey date | 2026-10-23 |
| Role (Q1) | Teacher / Educator |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Russian |
| Q3 | Beginner |
| Q4 | Several times a week |
| Q5 | Rarely |
| Q6 | Submitting new terms and translations |
| Q7 | Only chose from ready options |
| Q8 | Moderately interested |
| Q9 | Tips on which Kazakh connective to use instead of Russian; Short vocabulary quizzes |
| Q10 | Sometimes |
| Q11 | Important |
| Q12 | Science & Engineering |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Badges, streaks, and achievements; Official certificates of contribution |
| Q15 | Once a week or less |
| Q16 | Not answered (blank source cell). |

### R13
| Field | Recorded value |
|---|---|
| Source cells | A14:Q14 |
| Survey date | 2026-10-23 |
| Role (Q1) | Student |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Rarely |
| Q5 | Occasionally |
| Q6 | Validating existing terms and translations; Submitting new terms and translations |
| Q7 | Chose the best and proposed my own |
| Q8 | Moderately interested |
| Q9 | Word of the day with an example; List of most used words; Short vocabulary quizzes |
| Q10 | Rarely |
| Q11 | Critically important |
| Q12 | Information Technology & Software; Legal & Administrative; General everyday modern terms |
| Q13 | Only experts and official sources |
| Q14 | Public leaderboards and rankings; Badges, streaks, and achievements |
| Q15 | Daily (for practice and contributions) |
| Q16 | Everything is fine (Original English comment; trailing source whitespace omitted.) |

### R14
| Field | Recorded value |
|---|---|
| Source cells | A15:Q15 |
| Survey date | 2026-10-23 |
| Role (Q1) | Other |
| Survey language | English / Kazakh / Russian trilingual form; individual reading language not recorded |

| Question | Recorded answer in English |
|---|---|
| Q2 | Kazakh |
| Q3 | Native speaker |
| Q4 | Daily |
| Q5 | Rarely |
| Q6 | Validating existing terms and translations; Submitting new terms and translations; Reporting translation errors and bugs |
| Q7 | Only chose from ready options |
| Q8 | Moderately interested |
| Q9 | List of most used words; Tips on which Kazakh connective to use instead of Russian |
| Q10 | Sometimes |
| Q11 | Critically important |
| Q12 | Information Technology & Software; Science & Engineering; Business & Economics; Legal & Administrative |
| Q13 | Community votes, and disputed cases are reviewed by experts |
| Q14 | Public leaderboards and rankings |
| Q15 | Once a week or less |
| Q16 | No. (English translation of the recorded Russian comment.) |
