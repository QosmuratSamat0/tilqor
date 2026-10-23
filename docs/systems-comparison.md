# Comparison of existing systems

Owner: Alpamys. Sources accessed on 2026-10-23.

This comparison supports the thesis topic "Development of a Crowdsourcing Platform for Collecting and Verifying Kazakh Language Data with Daily Language Practice and Terminology Glossary Modules". Five existing systems were chosen because each covers at least one part of the proposed solution: crowdsourced data collection, verification, language practice, or terminology. The proposed platform (Tilqor) is added as a last column so the difference is visible at a glance. Every claim about an existing system carries a source number that points to the list at the end. A dash means the reviewed sources do not mention the feature, which is not the same as proof that it is absent.

Systems not included: Tilqural.kz is a step-by-step course with five levels and mobile apps [11][12], so it adds nothing beyond Soyle.kz for this comparison. Qazcorpora.kz is described as a project for small corpora and a future national corpus platform [16]; the sources say nothing about crowd contribution or verification, so it was not compared. Duolingo was left out because one learning-app review states that it has no Kazakh course [13], and the sources claiming otherwise were weaker.

## Comparison table

| Criterion | KSC (ISSAI, Nazarbayev University) | Mozilla Common Voice (Kazakh) | termincom.kz | Sozdikqor.kz | Soyle.kz | Tilqor (proposed) |
|---|---|---|---|---|---|---|
| Main purpose | Open speech corpus for Kazakh speech recognition, synthesis and speaker recognition [1] | Public voice dataset built from volunteer recordings and validations [5][6] | National terminology database run by state bodies [8][10] | Platform for looking up word meanings in industry dictionaries and encyclopedias [16][17] | Free online portal for learning literary and conversational Kazakh [11][14] | Crowdsourcing of Kazakh language data, with practice and glossary modules |
| Type of data | Transcribed speech: about 332 hours, over 153,000 utterances [2] | Read speech: 2,834 clips, 3.89 hours (2.5 validated), 201 speakers, 6,470 sentences [5] | Terms; about 18,000 in the Kazakhstan base at the time of the report [8] | Dictionary entries, including regional and new technological words [17] | Flashcards, phrases, exercises, tests, books [11] | Kazakh–Russian text pairs and term proposals |
| Public contribution of data | Speakers recorded sentences through a web platform for computers and smartphones [1][4]; no ongoing open contribution is described | Anyone can record clips and submit sentences, including batches of up to 1,000 [6][7][15] | Public discussion of proposed terms in the "Алаң" section [9]; open term submission is not described | — | — | Microtasks: translation ru→kk, choosing and proposing terms |
| Verification of data | Inspected by native Kazakh speakers [2]; checked with speech recognition experiments (2.8% character and 8.7% word error rate) [3] | Clips are validated by other contributors; sentences must be accepted by two reviewers [6][7] | Terms go to a commission, with sector sections and linguistic expertise; public discussion lasts at least 10 days [9] | — | — | Peer review of contributions and community voting on terms |
| Daily practice | — | Intended uses include language learning, but no learning module is described [5] | — | — | Flashcards, interactive exercises, tests; the wider project also has a game, karaoke and a Telegram bot [11][14] | Top words, word of the day, hints on Kazakh connectors (no exercises) |
| Terminology glossary | — | — | Core function: searchable term base [8][10] | Core function: dictionary lookup [16][17] | A dictionary exists in the same project, named Sozdik.Soyle [14] | Glossary with community proposals and voting |
| Kazakh–Russian pairs and community voting on terms | — | — | Public discussion of terms [9]; pairs and voting are not described | — | — | Both, combined in one platform |
| Openness | CC BY 4.0 [2]; available on request [1] | CC0 dataset; re-hosting forbidden [5] | Open web access; data licence not stated | Web access; data licence not stated | Free [11] | To be decided in the design |
| Platforms | Web recording tool [1] | Web platform [6] | Website [8] | Website [16] | Web, mobile app, Telegram bot [14] | Web |

The Tilqor column describes the project's intended scope, not evidence about an existing system, so it has no source numbers.

## Capabilities and limitations, with evidence

KSC is a finished research corpus rather than a continuing platform. The sources describe how it was built and released, and they report quality checks by native speakers [2][3]. Its successor KSC2 grew to over a thousand hours but added data from television, radio, parliament and podcasts rather than from a continuing crowd workflow [3]. Limitation for our topic: the sources show no daily practice or glossary module, and access is by request [1].

Common Voice is the closest match for the crowdsourcing and peer verification mechanics. Contributors donate voice, validate others and write sentences, and sentence acceptance needs two reviewers [6][7]. For Kazakh, the datasheet shows a small dataset, with 2.5 validated hours from 201 speakers [5]. The data is only read speech, and the sources show no terminology work, no Kazakh–Russian pairs and no structured practice for learners.

termincom.kz handles terminology through an official process. Terms pass through sector sections, linguistic expertise and a commission, and proposed terms are published for public discussion for at least 10 days [9]. Officials have admitted that some disputed terms entered use without ever being approved [8]. The site is aimed at lookup and standardization, and the sources do not describe user-submitted terms, voting or any practice mode.

Sozdikqor.kz is the closest existing system to our glossary module. It lets users see the meaning of words and expressions across industry dictionaries and encyclopedias, including old, regional and new technological words [16][17]. The sources describe it as a lookup resource and do not mention user contributions, verification by the crowd or practice features.

Soyle.kz covers the learning side. It offers flashcards, exercises and tests, plus a game, karaoke and a Telegram bot in the wider project [11][14]. The sources do not describe it as collecting data from learners or verifying it.

## Conclusion: why the proposed solution is needed

Among the systems reviewed, each covers one part of the problem and none covers all of it. Speech corpora and Common Voice collect and verify data, but they are limited to speech, and Common Voice has only a few hours for Kazakh [5]. Learning portals give practice but are not described as sources of reusable language data. Terminology portals standardize terms and lookups through an official process, with limited public input [8][9].

The proposed platform joins these parts around one idea: the data comes from microtasks, and the practice module keeps users coming back. Microtasks such as translating Russian into Kazakh, choosing the best term and proposing new terms produce Kazakh–Russian text pairs and term candidates. Peer review and community voting verify them, similar to the validation step in Common Voice [6][7]. The practice module is a catalogue with top words, a word of the day and hints on Kazakh connectors (for example, сонымен and дегенмен instead of Russian ones); it supports the contributors rather than producing data itself. The glossary adds the lexical layer that corpora and learning apps lack, while staying compatible with the official discussion process behind termincom.kz [9].

Limits of this review: it relies on public pages and papers, and some figures are dated (for example the term count at termincom.kz [8]). The Common Voice datasheet [5] was opened and its figures checked on 2026-10-23, but live features of the other systems were not tested hands-on. Before final submission, each system should be opened once to confirm that the current interface still matches these sources.

## Sources

1. A Crowdsourced Open-Source Kazakh Speech Corpus and Initial Speech Recognition Baseline: https://arxiv.org/pdf/2009.10334
2. OpenSLR, Kazakh Speech Corpus (SLR102): https://openslr.org/102/
3. ISSAI, KSC2 publication page: https://issai.nu.edu.kz/ksc2/ and KSC publication page https://issai.nu.edu.kz/2021/05/11/a-crowdsourced-open-source-kazakh-speech-corpus-and-initial-speech-recognition-baseline/
4. Nazarbayev University news on the KSC launch: https://nu.edu.kz/news-en/nu-scientists-launch-automated-kazakh-speech-recognition-project/
5. Common Voice Scripted Speech 25.0, Kazakh datasheet: https://mozilladatacollective.com/datasets/cmn29sufc018ymm071hvsk595
6. Common Voice FAQ: https://commonvoice.mozilla.org/en/faq
7. The new Common Voice Sentence Collector: https://www.mozillafoundation.org/en/blog/the-new-common-voice-sentence-collector
8. Informburo, Ministry of Culture on disputed Kazakh terms and termincom.kz: https://informburo.kz/novosti/minkultury-ne-utverzhdal-spornye-terminy-na-kazahskom-yazyke.html
9. Zakon.kz, unification of terms in the state language: https://www.zakon.kz/pravo/6437540-terminy-na-gosudarstvennom-yazyke-budut-unifitsirovat-v-kazakhstane.html
10. Kazinform, seminar on the terminology base: https://www.inform.kz/ru/terminologicheskaya-baza-dolzhna-obespechivat-poisk-dlya-lyubogo-yazykovogo-napravleniya-adil-bek-kaba_a3804540
11. Qazmonitor, free Kazakh learning resources: https://qazmonitor.com/lifestyle/2251/learning-kazakh-free-online-and-offline-courses-to-master-your-language-skills
12. Government of Kazakhstan, where to learn Kazakh: https://www.gov.kz/situations/730/intro?lang=en
13. Ling blog on Kazakh learning apps (Duolingo note): https://ling-app.com/blog/apps-to-learn-kazakh/
14. Kazinform, free internet projects for learning Kazakh: https://www.inform.kz/ru/kakie-besplatnye-internet-proekty-razrabotany-dlya-izucheniya-kazahskogo-yazyka_a3788372
15. Common Voice, small batch sentence submission: https://www.mozillafoundation.org/en/blog/small-batch-sentence-submission-comes-to-common-voice
16. KazNU library, electronic portals for the Kazakh language (Sozdikqor.kz, Qazcorpora.kz): https://elibrary.kaznu.kz/en/node/11036
17. DKnews, useful websites for learning Kazakh: https://dknews.kz/en/articles-in-english/198440-useful-websites-for-learning-kazakh-language
