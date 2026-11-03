import { describe, expect, it } from "vitest";
import i18n from "../index";
import ru from "../ru.json";
import kk from "../kk.json";

function collectKeyPaths(obj: Record<string, unknown>, prefix = ""): string[] {
  const keys: string[] = [];
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === "object" && !Array.isArray(value)) {
      keys.push(...collectKeyPaths(value as Record<string, unknown>, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys.sort();
}

describe("i18n translation files (ru.json and kk.json)", () => {
  it("has identical key sets in ru.json and kk.json", () => {
    const ruKeys = collectKeyPaths(ru as Record<string, unknown>);
    const kkKeys = collectKeyPaths(kk as Record<string, unknown>);
    expect(kkKeys).toEqual(ruKeys);
    expect(ruKeys.length).toBeGreaterThan(0);
  });

  it("falls back to Russian strings when language is kk and kk values are empty", async () => {
    await i18n.changeLanguage("kk");
    expect(i18n.t("nav.dictionary")).toBe(ru.nav.dictionary);
    await i18n.changeLanguage("ru");
  });
});

