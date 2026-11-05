import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { api } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { ReviewPage } from "../ReviewPage";

describe("ReviewPage", () => {
  const reviewerUser = {
    id: 2,
    username: "reviewer_dana",
    email: "dana@example.com",
    display_name: "Dana",
    role: "reviewer" as const,
    accepted_terms: true,
    accepted_terms_version: "1.0",
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(api.reviews, "queue").mockResolvedValue([
      {
        id: 301,
        number: 1,
        text_kk: "Жасанды интеллект жүйесі",
        task_type: "translation",
        domain: "it",
        text_ru: "Система искусственного интеллекта",
        definition: "",
      },
    ]);
    vi.spyOn(api.reviews, "myStats").mockResolvedValue({
      weight: "1.00",
      matched_votes: 8,
      finalized_votes: 10,
      match_share: "0.80000000",
    });
  });

  it("requires a reason code for reject/edit, and a linked comment for other", async () => {
    const user = userEvent.setup();
    const submitSpy = vi.spyOn(api.reviews, "submit");

    renderWithProviders(<ReviewPage />, {
      route: "/review",
      path: "/review",
      user: reviewerUser,
    });

    expect(
      await screen.findByText("Система искусственного интеллекта")
    ).toBeInTheDocument();

    // Choose "reject" without entering a reason
    await user.click(screen.getByRole("radio", { name: /Отклонить/i }));
    await user.click(
      screen.getByRole("button", { name: /Отправить решение/i })
    );

    expect(submitSpy).not.toHaveBeenCalled();
    expect(
      await screen.findByText(
        /Выберите причину для отклонения или запроса правки/i
      )
    ).toBeInTheDocument();

    // Switch to "edit" without entering a reason
    await user.click(screen.getByRole("radio", { name: /Нужна правка/i }));
    await user.click(
      screen.getByRole("button", { name: /Отправить решение/i })
    );

    expect(submitSpy).not.toHaveBeenCalled();
    expect(
      await screen.findByText(
        /Выберите причину для отклонения или запроса правки/i
      )
    ).toBeInTheDocument();

    const reasonGroup = screen.getByRole("group", { name: "Причина решения" });
    const other = within(reasonGroup).getByRole("radio", { name: "Другое" });
    expect(other).toHaveAccessibleDescription("Выберите причину для отклонения или запроса правки.");
    await user.click(other);
    await user.click(screen.getByRole("button", { name: /Отправить решение/i }));
    const comment = screen.getByRole("textbox", { name: "Комментарий" });
    expect(comment).toHaveAccessibleDescription(/Для причины «Другое» напишите комментарий/);
    expect(comment).toHaveAttribute("aria-invalid", "true");
    expect(submitSpy).not.toHaveBeenCalled();

    submitSpy.mockResolvedValueOnce({
      id: 900,
      version_id: 301,
      decision: "edit",
      reason_code: "other",
      reason: "Уточните порядок слов.",
      weight_snapshot: "1.00",
      created_at: "2026-04-01T11:00:00Z",
    });

    await user.type(
      comment,
      "Уточните порядок слов."
    );
    await user.click(
      screen.getByRole("button", { name: /Отправить решение/i })
    );

    expect(submitSpy).toHaveBeenCalledWith({
      version_id: 301,
      decision: "edit",
      reason_code: "other",
      reason: "Уточните порядок слов.",
    });
  });

  it("has exact visible radio names and sends a categorical reason without a comment", async () => {
    const user = userEvent.setup();
    const submitSpy = vi.spyOn(api.reviews, "submit").mockResolvedValue({
      id: 901, version_id: 301, decision: "reject", reason_code: "russian_connector",
      reason: "", weight_snapshot: "1.00", created_at: "2026-04-01T11:00:00Z",
    });
    renderWithProviders(<ReviewPage />, { user: reviewerUser });
    await screen.findByText("Система искусственного интеллекта");
    const decisions = screen.getByRole("group", { name: "Ваше решение" });
    for (const name of ["Принять", "Нужна правка", "Отклонить", "Не знаю / Пропустить"]) {
      expect(within(decisions).getByRole("radio", { name })).toBeInTheDocument();
    }
    await user.click(within(decisions).getByRole("radio", { name: "Отклонить" }));
    const reasons = screen.getByRole("group", { name: "Причина решения" });
    for (const name of ["Неверный термин", "Русская связка", "Грамматика", "Другое"]) {
      expect(within(reasons).getByRole("radio", { name })).toBeInTheDocument();
    }
    await user.click(within(reasons).getByRole("radio", { name: "Русская связка" }));
    await user.click(screen.getByRole("button", { name: "Отправить решение" }));
    expect(submitSpy).toHaveBeenCalledWith({
      version_id: 301, decision: "reject", reason_code: "russian_connector", reason: "",
    });
  });
});

