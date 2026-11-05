# i18n Key Convention (`kk` / `ru`)

All user-facing UI strings live in `src/shared/i18n/ru.json` and `src/shared/i18n/kk.json`.

## Key Naming Rules

- Keys are nested by feature or shared domain (`app`, `nav`, `domains`, `taskTypes`, `status`, `pagination`, `auth`, `home`, `tasks`, `contribute`, `review`, `my`, `dictionary`).
- Leaf key names use `camelCase` (`submitTranslation`, `acceptTermsLabel`, `emptyTitle`).
- Avoid hardcoding Russian or Kazakh strings inside `.tsx` components; always look up keys via `useTranslation()`.
- API codes are the exception to camelCase: keep the backend code verbatim in
  `feedback.warning.<code>`, `feedback.error.<code>` and `review.reasonCode.<code>`
  (for example, `feedback.error.text_too_long` and `review.reasonCode.wrong_term`).

## API feedback (TIL-36)

Warnings carry `{code, params, message}`. `feedback.ts` translates their code and
interpolates parameters; connector arrays become comma-separated text. Errors keep
their field messages plus `codes`, or `detail` plus `code`. Interpolation parameters
are keyed by field, for example `params.text_kk.max_length`.

`ApiError` keeps codes and parameters separate from field messages. The contribute,
review and own-version forms use the shared translator; an unknown code keeps the
server's message as the fallback. New keys must also be added to `kk.json` with empty
values until TIL-28. Review comments and moderator explanations are user content,
so only their reason codes are translated.

## Fallback Behaviour (`kk.json` in TIL-24 → TIL-28)

- `ru.json` contains working Russian UI texts.
- `kk.json` contains the **exact same key structure** as `ru.json` with empty string (`""`) values as placeholders for TIL-28 (Kazakh localisation).
- `i18next` is configured with `fallbackLng: "ru"` and `returnEmptyString: false`, so any empty string in `kk.json` automatically falls back to the Russian string in `ru.json`.

