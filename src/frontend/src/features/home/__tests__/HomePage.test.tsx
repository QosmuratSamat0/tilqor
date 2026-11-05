import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { api } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { HomePage } from "../HomePage";

describe("HomePage daily goal", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(api.catalogue, "today").mockResolvedValue({
      date: "2026-11-04",
      word_of_the_day: null,
      top_words: [],
      connector_hints: [],
    });
  });

  it("shows only the hint without numbers for anonymous users", async () => {
    renderWithProviders(<HomePage />, {
      route: "/",
      path: "/",
      user: null,
    });

    expect(
      screen.getByText(/Войдите в аккаунт, чтобы отслеживать свой вклад/i)
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/Выполнено пользователем:/i)
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("counts only contributions whose first version was created today (Asia/Almaty) out of 10 and ignores yesterday's", async () => {
    const nowIso = new Date().toISOString();
    const yesterdayIso = new Date(
      Date.now() - 24 * 60 * 60 * 1000
    ).toISOString();

    vi.spyOn(api.contributions, "me").mockResolvedValueOnce([
      {
        id: 1,
        task_id: 101,
        task_type: "translation",
        domain: "it",
        text_ru: "Сегодняшний вклад",
        created_at: nowIso,
        versions: [
          {
            id: 11,
            number: 1,
            text_kk: "Бүгінгі үлес",
            status: "submitted",
            decision_reasons: [],
            created_at: nowIso,
          },
        ],
      },
      {
        id: 2,
        task_id: 102,
        task_type: "term",
        domain: "it",
        text_ru: "Вчерашний вклад с сегодняшней второй версией",
        created_at: yesterdayIso,
        versions: [
          {
            id: 21,
            number: 1,
            text_kk: "Кешегі үлес",
            status: "needs_edit",
            decision_reasons: [{ code: "wrong_term", comment: "Правка" }],
            created_at: yesterdayIso,
          },
          {
            id: 22,
            number: 2,
            text_kk: "Жаңартылған үлес",
            status: "submitted",
            decision_reasons: [],
            created_at: nowIso,
          },
        ],
      },
    ]);

    renderWithProviders(<HomePage />, {
      route: "/",
      path: "/",
      user: {
        id: 1,
        username: "arman",
        email: "arman@example.com",
        display_name: "Arman",
        role: "participant",
        accepted_terms: true,
        accepted_terms_version: "1.0",
      },
    });

    expect(
      await screen.findByText("Выполнено пользователем: 1 из 10")
    ).toBeInTheDocument();
  });
});
