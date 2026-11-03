import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import ru from "./ru.json";
import kk from "./kk.json";

export const LANGUAGE_STORAGE_KEY = "tilqor_lang";
export type SupportedLanguage = "ru" | "kk";

function getInitialLanguage(): SupportedLanguage {
  if (typeof window !== "undefined" && window.localStorage) {
    const saved = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (saved === "kk" || saved === "ru") {
      return saved;
    }
  }
  return "ru";
}

void i18n.use(initReactI18next).init({
  resources: {
    ru: { translation: ru },
    kk: { translation: kk },
  },
  lng: getInitialLanguage(),
  fallbackLng: "ru",
  returnEmptyString: false,
  interpolation: {
    escapeValue: false,
  },
});

export function setAppLanguage(lang: SupportedLanguage): void {
  if (typeof window !== "undefined" && window.localStorage) {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
  }
  if (typeof document !== "undefined") {
    document.documentElement.lang = lang;
  }
  void i18n.changeLanguage(lang);
}

export default i18n;

