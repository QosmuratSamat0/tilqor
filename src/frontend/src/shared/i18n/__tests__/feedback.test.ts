import { describe, expect, it } from "vitest";
import i18n from "../index";
import { errorFeedback, warningText } from "../feedback";
import { parseErrorPayload } from "../../api/client";

describe("coded API feedback", () => {
  it("translates warnings and interpolates connector lists", () => {
    const text = warningText({ code: "russian_connectors", params: { connectors: ["и", "но"] },
      message: "Russian connectors." }, i18n.t);
    expect(text).toContain("русские связки: и, но");
  });

  it.each([
    ["empty_text", "Введите текст на казахском языке."],
    ["duplicate_variant", "Такой вариант уже есть в задании. Предложите другой."],
    ["text_too_long", "Текст не должен превышать 200 символов."],
    ["reason_required", "Выберите причину для отклонения или запроса правки."],
    ["comment_required", "Для причины «Другое» напишите комментарий."],
  ])("translates error %s", (code, expected) => {
    const parsed = parseErrorPayload(400, { text_kk: ["Server message."],
      codes: { text_kk: [code] }, params: { text_kk: { max_length: 200 } } });
    expect(errorFeedback(parsed, i18n.t).fields.text_kk).toEqual([expected]);
    expect(parsed.fieldErrors).not.toHaveProperty("codes");
  });

  it("translates detail plus code, and preserves unknown-code messages", () => {
    const known = parseErrorPayload(403, { detail: "Accept terms.", code: "terms_not_accepted" });
    expect(known.fieldErrors).toEqual({});
    expect(errorFeedback(known, i18n.t).detail).toBe("Примите условия публикации перед отправкой текста.");
    const unknown = parseErrorPayload(400, { detail: "New server error.", code: "future_error" });
    expect(errorFeedback(unknown, i18n.t).detail).toBe("New server error.");
    expect(warningText({ code: "future_warning", params: {}, message: "New server warning." }, i18n.t))
      .toBe("New server warning.");
    const unknownField = parseErrorPayload(400, { text_kk: ["New field error."], codes: { text_kk: ["future"] } });
    expect(errorFeedback(unknownField, i18n.t).fields.text_kk).toEqual(["New field error."]);
  });
});
