# i18n Key Convention (`kk` / `ru`)

All user-facing UI strings live in `src/shared/i18n/ru.json` and `src/shared/i18n/kk.json`.

## Key Naming Rules

- Keys are nested by feature or shared domain (`app`, `nav`, `domains`, `taskTypes`, `status`, `pagination`, `auth`, `home`, `tasks`, `contribute`, `review`, `my`, `dictionary`).
- Leaf key names use `camelCase` (`submitTranslation`, `acceptTermsLabel`, `emptyTitle`).
- Avoid hardcoding Russian or Kazakh strings inside `.tsx` components; always look up keys via `useTranslation()`.

## Fallback Behaviour (`kk.json` in TIL-24 → TIL-28)

- `ru.json` contains working Russian UI texts.
- `kk.json` contains the **exact same key structure** as `ru.json` with empty string (`""`) values as placeholders for TIL-28 (Kazakh localisation).
- `i18next` is configured with `fallbackLng: "ru"` and `returnEmptyString: false`, so any empty string in `kk.json` automatically falls back to the Russian string in `ru.json`.
