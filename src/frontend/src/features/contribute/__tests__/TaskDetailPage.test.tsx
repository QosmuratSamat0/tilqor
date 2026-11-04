import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { api } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { TaskDetailPage } from "../TaskDetailPage";

describe("TaskDetailPage (translation and term flows)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("hides other variants before translation submission and shows warnings + variants after submission", async () => {
    const user = userEvent.setup();

    const detailSpy = vi
      .spyOn(api.tasks, "detail")
      .mockResolvedValueOnce({
        id: 10,
        type: "translation",
        domain: "it",
        text_ru: "Кэширование ускоряет обработку запросов.",
        definition: "",
        created_at: "2026-04-01T10:00:00Z",
        variants: [],
      })
      .mockResolvedValueOnce({
        id: 10,
        type: "translation",
        domain: "it",
        text_ru: "Кэширование ускоряет обработку запросов.",
        definition: "",
        created_at: "2026-04-01T10:00:00Z",
        variants: [
          {
            id: 101,
            text_kk: "Кэштеу сұраныстарды өңдеуді жылдамдатады.",
            status: "submitted",
            public_name: "Aigerim",
            created_at: "2026-04-01T10:05:00Z",
          },
        ],
      });

    const submitSpy = vi
      .spyOn(api.tasks, "submitContribution")
      .mockResolvedValueOnce({
        id: 50,
        task_id: 10,
        created_at: "2026-04-01T10:05:00Z",
        version: {
          id: 101,
          number: 1,
          text_kk: "Кэштеу сұраныстарды өңдеуді жылдамдатады",
          status: "submitted",
          created_at: "2026-04-01T10:05:00Z",
        },
        warnings: {
          text_kk: ["Перевод слишком короткий по сравнению с оригиналом."],
        },
      });

    renderWithProviders(<TaskDetailPage />, {
      route: "/tasks/10",
      path: "/tasks/:id",
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
      await screen.findByText("Кэширование ускоряет обработку запросов.")
    ).toBeInTheDocument();

    expect(
      screen.getByText(/Другие варианты скрыты до отправки вашего перевода/i)
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("region", { name: /Варианты участников/i })
    ).not.toBeInTheDocument();

    await user.type(
      screen.getByLabelText(/Ваш перевод на казахский язык/i),
      "Кэштеу сұраныстарды өңдеуді жылдамдатады"
    );
    await user.click(
      screen.getByRole("button", { name: /Отправить перевод/i })
    );

    expect(submitSpy).toHaveBeenCalledWith(
      10,
      "Кэштеу сұраныстарды өңдеуді жылдамдатады"
    );

    expect(
      await screen.findByText(
        "Перевод слишком короткий по сравнению с оригиналом."
      )
    ).toBeInTheDocument();

    expect(
      await screen.findByText("Кэштеу сұраныстарды өңдеуді жылдамдатады.")
    ).toBeInTheDocument();
    expect(detailSpy).toHaveBeenCalledTimes(2);
  });

  it("renders term variants in API order and allows choosing a preference", async () => {
    const user = userEvent.setup();

    vi.spyOn(api.tasks, "detail").mockResolvedValueOnce({
      id: 22,
      type: "term",
      domain: "it",
      text_ru: "Компилятор",
      definition: "Программа, переводящая исходный код в машинный код.",
      created_at: "2026-04-01T10:00:00Z",
      variants: [
        {
          id: 201,
          text_kk: "Компилятор",
          status: "accepted",
          public_name: "Tilqor team",
          created_at: "2026-04-01T10:00:00Z",
        },
        {
          id: 202,
          text_kk: "Құрастырғыш",
          status: "submitted",
          public_name: "Nurlan",
          created_at: "2026-04-01T10:01:00Z",
        },
      ],
    });

    const prefSpy = vi
      .spyOn(api.tasks, "setPreference")
      .mockResolvedValueOnce({
        id: 1,
        task_id: 22,
        version_id: 202,
        updated_at: "2026-04-01T10:10:00Z",
      });

    renderWithProviders(<TaskDetailPage />, {
      route: "/tasks/22",
      path: "/tasks/:id",
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

    expect(await screen.findByText("Құрастырғыш")).toBeInTheDocument();

    const chooseButtons = screen.getAllByRole("button", {
      name: /Выбрать этот вариант/i,
    });
    expect(chooseButtons).toHaveLength(2);

    await user.click(chooseButtons[1]);
    expect(prefSpy).toHaveBeenCalledWith(22, 202);
    expect(
      await screen.findByRole("button", { name: /Ваш выбор сохранён/i })
    ).toBeInTheDocument();
  });
});

