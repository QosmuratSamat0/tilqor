import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import { api } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { DictionaryDetailPage } from "../DictionaryDetailPage";

describe("DictionaryDetailPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders pending variants in a clearly separated section from accepted recommended and alternative variants", async () => {
    vi.spyOn(api.dictionary, "detail").mockResolvedValueOnce({
      id: 42,
      text_ru: "Сетевой экран",
      definition: "Система защиты компьютерной сети.",
      domain: "it",
      source: "Open Glossary",
      recommended: {
        id: 401,
        text_kk: "Желілік қалқан",
        public_name: "Tilqor team",
        reason: "Наиболее популярный принятый вариант.",
      },
      alternatives: [
        {
          id: 402,
          text_kk: "Брандмауэр",
          public_name: "Nurlan",
        },
      ],
      pending: [
        {
          id: 403,
          text_kk: "Қорғаныс экраны",
          public_name: "Aigerim",
          status: "in_review",
        },
      ],
    });

    renderWithProviders(<DictionaryDetailPage />, {
      route: "/dictionary/42",
      path: "/dictionary/:id",
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

    expect(await screen.findByText("Сетевой экран")).toBeInTheDocument();

    const recommendedSection = screen.getByRole("region", {
      name: /Рекомендуемый перевод/i,
    });
    expect(
      within(recommendedSection).getByText("Желілік қалқан")
    ).toBeInTheDocument();
    expect(
      within(recommendedSection).queryByText("Қорғаныс экраны")
    ).not.toBeInTheDocument();

    const alternativesSection = screen.getByRole("region", {
      name: /Альтернативные принятые варианты/i,
    });
    expect(
      within(alternativesSection).getByText("Брандмауэр")
    ).toBeInTheDocument();
    expect(
      within(alternativesSection).queryByText("Қорғаныс экраны")
    ).not.toBeInTheDocument();

    const pendingSection = screen.getByRole("region", {
      name: /На проверке \(ещё не приняты\)/i,
    });
    expect(
      within(pendingSection).getByText("Қорғаныс экраны")
    ).toBeInTheDocument();
    expect(within(pendingSection).getByText("На проверке")).toBeInTheDocument();
  });
});

