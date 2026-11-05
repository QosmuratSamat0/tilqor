import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { api, parseErrorPayload } from "../../../shared/api/client";
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
        own_contribution: null,
      })
      .mockResolvedValueOnce({
        id: 10,
        type: "translation",
        domain: "it",
        text_ru: "Кэширование ускоряет обработку запросов.",
        definition: "",
        own_contribution: { id: 50, status: "submitted", latest_version_number: 1 },
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
          text_kk: [
            { code: "no_kazakh_letters", params: {}, message: "No Kazakh letters." },
            { code: "future_warning", params: {}, message: "New server warning." },
          ],
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
        /В тексте нет специфических казахских букв/
      )
    ).toBeInTheDocument();

    expect(
      await screen.findByText("Кэштеу сұраныстарды өңдеуді жылдамдатады.")
    ).toBeInTheDocument();
    expect(detailSpy).toHaveBeenCalledTimes(2);
    expect(screen.getByText("New server warning.")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Мои переводы" })).toHaveAttribute("href", "/my");
    expect(screen.getByText("Ваш вариант успешно сохранён и отправлен на проверку.")).toBeInTheDocument();
  });

  it("renders term variants in API order and allows choosing a preference", async () => {
    const user = userEvent.setup();

    vi.spyOn(api.tasks, "detail").mockResolvedValueOnce({
      id: 22,
      type: "term",
      domain: "it",
      text_ru: "Компилятор",
      definition: "Программа, переводящая исходный код в машинный код.",
      own_contribution: null,
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

    const group = screen.getByRole("group", { name: "Ваш выбор термина" });
    expect(within(group).getByRole("radio", { name: "Компилятор" })).toBeInTheDocument();
    await user.click(within(group).getByRole("radio", { name: "Құрастырғыш" }));
    expect(prefSpy).toHaveBeenCalledWith(22, 202);
    expect(await screen.findByText("Ваш выбор сохранён")).toBeInTheDocument();
    expect(within(group).getByRole("radio", { name: "Құрастырғыш" })).toBeChecked();
  });

  it.each(["translation", "term"] as const)("hides the %s suggestion form after reload", async (type) => {
    vi.spyOn(api.tasks, "detail").mockResolvedValue({
      id: 10, type, domain: "it", text_ru: "Текст", definition: "",
      created_at: "2026-04-01T10:00:00Z", variants: [],
      own_contribution: { id: 50, status: "needs_edit", latest_version_number: 2 },
    });
    renderWithProviders(<TaskDetailPage />, { route: "/tasks/10", path: "/tasks/:id" });
    expect(await screen.findByRole("link", { name: "Мои переводы" })).toHaveAttribute("href", "/my");
    expect(screen.getByText("Нужна правка")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("keeps radio focus while serializing rapid changes of term preference", async () => {
    const user = userEvent.setup();
    vi.spyOn(api.tasks, "detail").mockResolvedValue({
      id: 22, type: "term", domain: "it", text_ru: "Термин", definition: "",
      created_at: "2026-04-01T10:00:00Z", own_contribution: null,
      variants: [1, 2].map((id) => ({ id, text_kk: `Вариант ${id}`, status: "submitted",
        public_name: "Автор", created_at: "2026-04-01T10:00:00Z" })),
    });
    let resolveFirst!: (value: { id: number; task_id: number; version_id: number; updated_at: string }) => void;
    const prefSpy = vi.spyOn(api.tasks, "setPreference")
      .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }))
      .mockResolvedValueOnce({ id: 1, task_id: 22, version_id: 2, updated_at: "2026-04-01T10:00:00Z" });
    renderWithProviders(<TaskDetailPage />, { route: "/tasks/22", path: "/tasks/:id" });
    const first = await screen.findByRole("radio", { name: "Вариант 1" });
    const second = screen.getByRole("radio", { name: "Вариант 2" });
    await user.click(first);
    expect(first).toHaveFocus();
    await user.click(second);
    expect(second).toHaveFocus();
    expect(prefSpy).toHaveBeenCalledTimes(1);
    resolveFirst({ id: 1, task_id: 22, version_id: 1, updated_at: "2026-04-01T10:00:00Z" });
    await screen.findByText("Ваш выбор сохранён");
    expect(prefSpy).toHaveBeenNthCalledWith(2, 22, 2);
    expect(second).toBeChecked();
    expect(second).toHaveFocus();
  });

  it("keeps the form hidden during a pending refetch and after a stale response", async () => {
    const user = userEvent.setup();
    const task = {
      id: 10, type: "translation" as const, domain: "it" as const,
      text_ru: "Текст", definition: "", created_at: "2026-04-01T10:00:00Z",
      variants: [], own_contribution: null,
    };
    let resolveRefetch!: (value: typeof task) => void;
    vi.spyOn(api.tasks, "detail").mockResolvedValueOnce(task)
      .mockImplementationOnce(() => new Promise((resolve) => { resolveRefetch = resolve; }));
    vi.spyOn(api.tasks, "submitContribution").mockResolvedValue({
      id: 50, task_id: 10, created_at: task.created_at, warnings: {},
      version: { id: 1, number: 1, text_kk: "text", status: "submitted", created_at: task.created_at },
    });
    renderWithProviders(<TaskDetailPage />, { route: "/tasks/10", path: "/tasks/:id" });
    await user.type(await screen.findByRole("textbox"), "text");
    await user.click(screen.getByRole("button", { name: "Отправить перевод" }));
    expect(await screen.findByRole("link", { name: "Мои переводы" })).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    resolveRefetch(task);
    expect(await screen.findByText("Пока нет других вариантов для этого задания.")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it.each([
    ["empty_text", "Введите текст на казахском языке."],
    ["text_too_long", "Текст не должен превышать 1000 символов."],
    ["future_error", "Future server message."],
  ])("shows API field error %s through i18n with a server fallback", async (code, message) => {
    vi.spyOn(api.tasks, "detail").mockResolvedValue({
      id: 10, type: "translation", domain: "it", text_ru: "Текст", definition: "",
      created_at: "2026-04-01T10:00:00Z", variants: [], own_contribution: null,
    });
    vi.spyOn(api.tasks, "submitContribution").mockRejectedValue(parseErrorPayload(400, {
      text_kk: ["Future server message."], codes: { text_kk: [code] },
      params: { text_kk: { max_length: 1000 } },
    }));
    const user = userEvent.setup();
    renderWithProviders(<TaskDetailPage />, { route: "/tasks/10", path: "/tasks/:id" });
    await user.click(await screen.findByRole("button", { name: "Отправить перевод" }));
    expect(await screen.findByText(message)).toBeInTheDocument();
    expect(screen.getByRole("textbox")).toHaveAccessibleDescription(message);
  });
});

