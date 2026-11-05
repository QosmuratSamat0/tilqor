import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import { api } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { MyContributionsPage } from "../MyContributionsPage";

describe("MyContributionsPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the new version form ONLY when the latest version status is needs_edit", async () => {
    vi.spyOn(api.contributions, "me").mockResolvedValueOnce([
      {
        id: 1,
        task_id: 101,
        task_type: "translation",
        domain: "it",
        text_ru: "Сервер баз данных",
        created_at: "2026-04-01T09:00:00Z",
        versions: [
          {
            id: 11,
            number: 1,
            text_kk: "Деректер базасы сервері",
            status: "needs_edit",
            decision_reasons: [
              { code: "wrong_term", comment: "Используйте термин «Дерекқор сервері»." },
              { code: "russian_connector", comment: "" },
              { code: null, comment: "Комментарий модератора." },
            ],
            created_at: "2026-04-01T09:00:00Z",
          },
        ],
      },
      {
        id: 2,
        task_id: 102,
        task_type: "term",
        domain: "it",
        text_ru: "Маршрутизатор",
        created_at: "2026-04-01T09:10:00Z",
        versions: [
          {
            id: 21,
            number: 1,
            text_kk: "Бағыттауыш",
            status: "accepted",
            decision_reasons: [],
            created_at: "2026-04-01T09:10:00Z",
          },
        ],
      },
      {
        id: 3,
        task_id: 103,
        task_type: "translation",
        domain: "medicine",
        text_ru: "Клиническое исследование",
        created_at: "2026-04-01T09:20:00Z",
        versions: [
          {
            id: 31,
            number: 1,
            text_kk: "Клиникалық зерттеу",
            status: "in_review",
            decision_reasons: [],
            created_at: "2026-04-01T09:20:00Z",
          },
        ],
      },
    ]);

    renderWithProviders(<MyContributionsPage />, {
      route: "/my",
      path: "/my",
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

    expect(await screen.findByText("Сервер баз данных")).toBeInTheDocument();
    expect(
      screen.getByText("Неверный термин: Используйте термин «Дерекқор сервері».")
    ).toBeInTheDocument();
    expect(screen.getByText("Русская связка", { exact: true })).toBeInTheDocument();
    expect(screen.getByText("Комментарий модератора.", { exact: true })).toBeInTheDocument();

    const submitButtons = screen.getAllByRole("button", {
      name: /Отправить новую версию/i,
    });
    expect(submitButtons).toHaveLength(1);

    const cards = screen.getAllByRole("listitem");
    const acceptedCard = cards.find((el) =>
      el.textContent?.includes("Маршрутизатор")
    );
    expect(acceptedCard).toBeDefined();
    expect(
      within(acceptedCard!).queryByRole("button", {
        name: /Отправить новую версию/i,
      })
    ).not.toBeInTheDocument();
  });
});

