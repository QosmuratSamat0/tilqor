# Literature review

Task: [TIL-13](https://qosmuratsamat.youtrack.cloud/issue/TIL-13) (sources: [TIL-12](https://qosmuratsamat.youtrack.cloud/issue/TIL-12)).
Owners: Alpamys, Ulykbek. Samat helps.

Project: crowdsourcing platform for collecting and verifying Kazakh language data (ru–kk sentence pairs and Kazakh terms), with daily practice and terminology glossary modules.

Scope: 25 sources. 20 are from 2021–2026; 5 older works are kept because the project's quality model is built directly on them (majority voting, annotator reliability, Krippendorff's alpha). All 25 are scientific publications (conference papers and journal articles); for [10] only the bibliographic record was seen, and the year of [25] is still to be confirmed. This is a narrative critical review, not a systematic one.

Reading status: every source was checked against its abstract or its publisher / ACL Anthology record. The "Read" column of the table says what was actually seen. The criterion "text is based on sources that were actually read" is met only after the full texts of the core sources are read (see the last section).

## Critical review

**Kazakh language resources.** Kazakh-specific work concentrates on corpora and model evaluation. KSC [18] is a crowdsourced speech corpus of about 332 hours checked by native speakers, and KazParC [17] is a parallel corpus of about 372,000 human-assisted sentences in Kazakh, English, Russian and Turkish. KazMMLU [3] (23,000 questions validated by native speakers and educators) and Maxutov et al. [4] (seven LLMs) show that models perform worse in Kazakh than in high-resource languages. Tleubayeva et al. [1] show the value of a small curated Kazakh corpus, and Fazylzhan [2] describes the conceptual foundations of the National Corpus of the Kazakh Language. What is known: validated Kazakh data is scarce, and models depend on it. What is not covered: how ordinary users can contribute and verify individual ru–kk pairs and terms in an ongoing process. The project therefore does not compete with national corpora; it adds a continuing, verified, bottom-up source of small records.

**Collection workflows.** Three approaches appear. Open crowdsourcing with peer validation is shown by Common Voice [19], where volunteers record and validate speech, and by Malmon [6], an open platform with gamification and an admin panel for Icelandic text simplification. Assisted contribution is shown by INMT-Lite [7], whose user study with the Gondi community reports lower cognitive load without loss of translation quality. Automated web ingestion is shown by de Jesus and Nunes [8] for Tetun. Yu et al. [5] add that dataset counts hide quality differences and that the availability of proficient workers tracks dataset availability. Limitation: none of these collects Kazakh text pairs or terms, and the Malmon abstract reports no evaluation of data quality. The project takes from them short micro-tasks, separate submission, review and publication stages, and contributor availability as an explicit risk (risk R-02).

**Verification and quality of crowd data.** This is the core of the project. Snow et al. [20] showed that non-expert annotations collected through crowdsourcing can reach high agreement with expert gold labels on five NLP tasks. Dawid and Skene [22] introduced estimating each annotator's error rate without knowing the true answer; MACE [21] applies the same idea to crowdsourced NLP labels, learns which annotators are trustworthy, reports considerable improvements over standard baselines, and achieves higher accuracy when annotated control instances are added. Uma et al. [24] survey methods for learning from annotator disagreement and show that the choice of evaluation matters. Klie et al. [9] annotated 591 dataset papers and found common errors in agreement and error-rate computation. Hayes and Krippendorff [23] argue for Krippendorff's alpha as a reliability measure that works with any number of raters and missing data. What the project takes: (1) reviewer weights that depend on agreement with final decisions, a simplified version of the annotator-reliability idea in [21][22]; (2) control tasks with known answers, as in [21]; (3) Krippendorff's alpha as the agreement metric [23]; (4) simple majority voting as the baseline for comparison [21]. Limitation: these works concern classification labels, not translations or term choice, and our weight-update rule is a heuristic, not the full statistical models of [21][22]. Whether it beats majority voting on Kazakh data is the project's hypothesis, tested in the verification plan (TIL-7).

**Terminology and lexical structure.** Ylonen [11] shows that Wiktionary can be turned into structured data with lemmas, translations, examples and lexical relations, and Bajčetić and Declerck [12] use such data to build specialized lexical datasets. Tran et al. [13] survey neural automatic term extraction, which produces candidate term lists. None of these addresses Kazakh, and Kazakh coverage in Wiktionary was not checked. The glossary therefore uses explicit fields (term, language, domain, definition, translation, example, source, status), and machine-suggested terms stay candidates until reviewed.

**Daily practice.** Three reviews cover technology-assisted vocabulary learning. Okumuş Dağdeler [14] finds gamification the most common technological focus; Simonnet et al. [15] review 44 articles and report an overall positive influence on outcomes and engagement; Duan et al. [16] review 36 studies and note that collocation and contextual use remain underexplored. These are mostly second-language and English studies. In this project, daily practice is deliberately limited to a **catalogue** (top words, word of the day, Kazakh connector hints) built only from accepted records; exercises, flashcards and quizzes are out of scope for the MVP. The reviews support showing words in context with examples; any learning effect for Kazakh users is a hypothesis and is not measured in the MVP.

**Gap.** The closest system found is Abounegm et al. [25], a platform for underrepresented languages where learners submit language resources and peers rate them by voting. Its abstract reports technical testing and usability findings but no data-quality model or agreement measurement, and it does not target Kazakh. Within the reviewed sample, no source shows a Kazakh-focused platform that joins (a) ru–kk sentence pairs and term proposals, (b) reputation-weighted verification with control tasks and a measured agreement, and (c) a glossary and daily catalogue built only from verified records. This is a gap in the sample, not proof that none exists. The testable contribution is: micro-task contributions → weighted, measured verification → searchable glossary and daily catalogue → exportable dataset.

## Analysis table

| # | Source | Method | Result | Relevance to the project | Read |
|---|---|---|---|---|---|
| 1 | Tleubayeva et al. (2025) | Small Kazakh Language Corpus (news, scientific, Wikipedia texts); fine-tuned XLM-RoBERTa and a Kazakh RoBERTa | Reported better efficiency of NLP in a low-resource setting; figures not seen | Value of small curated Kazakh data; keep provenance and validated examples | Abstract (partial) |
| 2 | Fazylzhan (2023) | Conceptual article on the National Corpus of the Kazakh Language | Need for the corpus, development stages, annotation principles | Background: national corpus work is top-down; our platform adds bottom-up verified records | Publisher page summary |
| 3 | Togmanov et al. (2025), KazMMLU | 23,000 questions in Kazakh and Russian validated by native speakers and educators; several LLMs evaluated | Even the best models struggle in Kazakh and Russian | Native-speaker validation; AI output cannot be authoritative | Abstract |
| 4 | Maxutov et al. (2024) | Seven LLMs on Kazakh tasks (QA, reasoning, math, MT, spelling) | Lower quality than on English; weaker on generative tasks | AI suggestions only as optional candidates (FR-23) | Abstract |
| 5 | Yu et al. (2022) | Annotation of how 156 multilingual datasets were built; survey of researchers and crowd workers | Dataset counts mislead; worker availability tracks dataset availability | Track verified records, not totals; contributor supply is a risk | Abstract |
| 6 | Hjartarson & Friðriksdóttir (2024), Malmon | Open web crowdsourcing platform with gamification and admin panel; Icelandic | Architecture and interface described; no quality evaluation in abstract | Closest precedent for contribution flow and admin review | Abstract |
| 7 | Diddee et al. (2024), INMT-Lite | Offline interactive MT tool; user study with the Gondi community | Lower cognitive load, higher productivity, no loss of quality | Keep tasks short and low-effort | Abstract |
| 8 | de Jesus & Nunes (2024) | Crawler pipeline with tokenizer and language identification for Tetun | 321.7k sentences from over 22k pages | Separate ingestion from verification and publication | Abstract |
| 9 | Klie et al. (2024) | Analysis of quality management in 591 dataset papers | About 30% subpar; common errors in agreement and error-rate computation | Compute agreement correctly; check the alpha implementation (FR-26) | Abstract |
| 10 | Beck (2023) | Research synthesis on quality aspects of annotated data | Not read; bibliographic record only | Candidate support for error audits; use only after reading | Record only |
| 11 | Ylonen (2022), Wiktextract | Extraction of structured data from Wiktionary | Lemmas, forms, translations, examples, relations as JSON | Schema reference for glossary fields | Abstract |
| 12 | Bajčetić & Declerck (2022) | Specialized lexical datasets from Wiktionary | Method for domain- and attribute-specific lexical records | Supports explicit glossary fields; Kazakh not covered | Abstract |
| 13 | Tran et al. (ACM survey; preprint 2023) | Survey of neural automatic term extraction | Neural extraction produces candidate term lists | Extracted terms stay candidates until reviewed | Preprint abstract; ACM version not checked |
| 14 | Okumuş Dağdeler (2023) | Bibliometric analysis of 687 publications, 19 analyzed in depth | Gamification the most common technological focus | Trend map only, not effectiveness evidence | Abstract |
| 15 | Simonnet et al. (2025) | Systematic review, 44 articles, 2015–2023 | Overall positive influence on outcomes and engagement | Supports showing words in context; Kazakh effect untested | Abstract |
| 16 | Duan, Yunus & Ismail (2026) | PRISMA review of 36 studies, 2019–2025 | Gains in retention and motivation; collocation and context underexplored | Supports contextual examples in the catalogue; English only | Abstract |
| 17 | Yeshpanov, Polonskaya & Varol (2024), KazParC | Parallel corpus, ~372,000 human-assisted sentences (kk, en, ru, tr); NMT model Tilmash | Public corpus and model, CC BY 4.0 | Closest existing kk–ru text resource; our records complement it with verified small items | Abstract |
| 18 | Khassanov et al. (2021), KSC | Crowdsourced Kazakh speech corpus, ~332 h, 153,000+ utterances, checked by native speakers | ASR baseline: 2.8% CER, 8.7% WER | Native-speaker checking; speech only, no text pairs or terms | Abstract |
| 19 | Ardila et al. (2020), Common Voice | Volunteer speech recording with community validation, many languages | Large multilingual speech corpus | Model for peer validation by the community; speech only | Abstract |
| 20 | Snow et al. (2008) | Non-expert annotation via Mechanical Turk on five NLP tasks; bias correction | High agreement with expert gold labels; bias correction improves quality | Foundation: several non-expert votes can replace expert labels | Abstract (PDF) |
| 21 | Hovy et al. (2013), MACE | Unsupervised item-response model for crowd labels | Learns which annotators are trustworthy; better than standard baselines; better still with control instances | Basis for reviewer weights, control tasks and the majority baseline | Abstract (PDF) |
| 22 | Dawid & Skene (1979) | EM algorithm to estimate observer error rates without true labels | Maximum likelihood estimates of individual error rates | Foundation of annotator-reliability models; our weights are a simplified heuristic | Abstract (record) |
| 23 | Hayes & Krippendorff (2007) | Argument for a standard reliability measure; software macro | Krippendorff's alpha works for any number of raters and missing data | Justifies alpha as the agreement metric (FR-26) | Abstract |
| 24 | Uma et al. (2021) | Survey and comparison of methods for learning from annotator disagreement | Evaluation choice and dataset characteristics strongly affect results | Report disagreement and unresolved cases instead of hiding them | Abstract |
| 25 | Abounegm, Askarbekuly, Magomedov & Mazzara (AHFE Open Access) | Crowdsourcing platform for second-language learning; learners submit resources, peers vote | Good security, scalability, portability; usability improvements suggested | Closest similar system; no quality model or Kazakh focus | Abstract |

## Research questions for the evaluation

These match the [verification plan](verification-plan.md) (TIL-7):

- RQ1: On the same votes, is the weighted model with control tasks more accurate than simple majority voting? [20][21][22]
- RQ2: How many records remain unresolved or need a moderator, and how many votes does a decision need?
- RQ3: What is the agreement between reviewers, measured with Krippendorff's alpha? [23]
- RQ4: Can users find a verified Kazakh term with its recommended variant and alternatives?
- RQ5: How do users perceive the contribution and review flow?

## References

[1] Tleubayeva, A., Tabuldin, A., Aubakirov, S., et al. (2025). Development and Evaluation of a Small Kazakh Language Corpus. https://doi.org/10.1109/SIST61657.2025.11139363
[2] Fazylzhan, A. (2023). Conceptual Foundations of the National Corpus of the Kazakh Language [in Russian]. Etnosayasat, No. 2. https://doi.org/10.61572/2958-1427-2023-2-7-15
[3] Togmanov, M., et al. (2025). KazMMLU: Evaluating Language Models on Kazakh, Russian, and Regional Knowledge of Kazakhstan. ACL 2025. https://aclanthology.org/2025.acl-long.701/
[4] Maxutov, A., Myrzakhmet, A., Braslavski, P. (2024). Do LLMs Speak Kazakh? A Pilot Evaluation of Seven Models. SIGTURK 2024. https://aclanthology.org/2024.sigturk-1.8/
[5] Yu, X., Chatterjee, T., Asai, A., Hu, J., Choi, E. (2022). Beyond Counting Datasets: A Survey of Multilingual Dataset Construction and Necessary Resources. Findings of EMNLP 2022. https://aclanthology.org/2022.findings-emnlp.273/
[6] Hjartarson, H. B., Friðriksdóttir, S. R. (2024). Malmon: A Crowd-Sourcing Platform for Simple Language. READI 2024. https://aclanthology.org/2024.readi-1.2/
[7] Diddee, H., et al. (2024). INMT-Lite: Accelerating Low-Resource Language Data Collection via Offline Interactive Neural Machine Translation. LREC-COLING 2024. https://aclanthology.org/2024.lrec-main.797/
[8] de Jesus, G., Nunes, S. S. (2024). Data Collection Pipeline for Low-Resource Languages: A Case Study on Constructing a Tetun Text Corpus. LREC-COLING 2024. https://aclanthology.org/2024.lrec-main.390/
[9] Klie, J.-C., Eckart de Castilho, R., Gurevych, I. (2024). Analyzing Dataset Annotation Quality Management in the Wild. Computational Linguistics 50(3). https://doi.org/10.1162/coli_a_00516
[10] Beck, J. (2023). Quality Aspects of Annotated Data. AStA Wirtschafts- und Sozialstatistisches Archiv 17(3–4), 331–353. https://doi.org/10.1007/s11943-023-00332-y
[11] Ylonen, T. (2022). Wiktextract: Wiktionary as Machine-Readable Structured Data. LREC 2022. https://aclanthology.org/2022.lrec-1.140/
[12] Bajčetić, L., Declerck, T. (2022). Using Wiktionary to Create Specialized Lexical Resources and Datasets. LREC 2022. https://aclanthology.org/2022.lrec-1.370/
[13] Tran, H. T. H., Martinc, M., Caporusso, J., Doucet, A., Pollak, S. Recent Advances in Automatic Term Extraction: A Comprehensive Survey. ACM. https://doi.org/10.1145/3787584 (preprint: arXiv:2301.06767)
[14] Okumuş Dağdeler, K. (2023). A Systematic Review of Mobile-Assisted Vocabulary Learning Research. Smart Learning Environments 10. https://doi.org/10.1186/s40561-023-00235-z
[15] Simonnet, E., Loiseau, M., Lavoué, É. (2025). A Systematic Literature Review of Technology-Assisted Vocabulary Learning. Journal of Computer Assisted Learning 41(1), e13096. https://doi.org/10.1111/jcal.13096
[16] Duan, H., Yunus, M. M., Ismail, H. H. (2026). Mobile-Assisted English Vocabulary Learning: A Systematic Review of Platforms, Learning Outcomes, and Implications (2019–2025). International Journal of Learning, Teaching and Educational Research 25(2). https://doi.org/10.26803/ijlter.25.2.4
[17] Yeshpanov, R., Polonskaya, A., Varol, H. A. (2024). KazParC: Kazakh Parallel Corpus for Machine Translation. LREC-COLING 2024, 9633–9644. https://aclanthology.org/2024.lrec-main.842/
[18] Khassanov, Y., Mussakhojayeva, S., Mirzakhmetov, A., Adiyev, A., Nurpeiissov, M., Varol, H. A. (2021). A Crowdsourced Open-Source Kazakh Speech Corpus and Initial Speech Recognition Baseline. EACL 2021, 697–706. https://aclanthology.org/2021.eacl-main.58/
[19] Ardila, R., Branson, M., Davis, K., et al. (2020). Common Voice: A Massively-Multilingual Speech Corpus. LREC 2020, 4218–4222. https://aclanthology.org/2020.lrec-1.520/
[20] Snow, R., O'Connor, B., Jurafsky, D., Ng, A. (2008). Cheap and Fast – But is it Good? Evaluating Non-Expert Annotations for Natural Language Tasks. EMNLP 2008, 254–263. https://aclanthology.org/D08-1027/
[21] Hovy, D., Berg-Kirkpatrick, T., Vaswani, A., Hovy, E. (2013). Learning Whom to Trust with MACE. NAACL-HLT 2013, 1120–1130. https://aclanthology.org/N13-1132/
[22] Dawid, A. P., Skene, A. M. (1979). Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm. Journal of the Royal Statistical Society, Series C (Applied Statistics) 28(1), 20–28. https://doi.org/10.2307/2346806
[23] Hayes, A. F., Krippendorff, K. (2007). Answering the Call for a Standard Reliability Measure for Coding Data. Communication Methods and Measures 1(1), 77–89. https://doi.org/10.1080/19312450709336664
[24] Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., Poesio, M. (2021). Learning from Disagreement: A Survey. Journal of Artificial Intelligence Research 72, 1385–1470. https://doi.org/10.1613/jair.1.12752
[25] Abounegm, A., Askarbekuly, N., Magomedov, M., Mazzara, M. Crowdsourcing for Second Language Learning. AHFE Open Access, Human Factors in Software and Systems Engineering. https://doi.org/10.54941/ahfe1003773 (year to confirm)

## Before submission

- Read the full texts of the core sources, at least [17], [18], [20], [21], [23], [24], [25], and update the table from them. Until then the "actually read" criterion is not met.
- Read [10] (Beck), which has only a record, or remove it.
- Confirm the year of [25] and the ACM version and year of [13].
- Check the citation style with the supervisor.
