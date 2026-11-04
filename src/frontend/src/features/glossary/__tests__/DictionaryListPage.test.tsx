import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { api } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { DictionaryListPage } from "../DictionaryListPage";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

describe("DictionaryListPage export links", () => {
  it.each(["", "https://api.example.test"])(
    "uses the API base '%s' for both dataset downloads",
    async (base) => {
      vi.stubEnv("VITE_API_BASE_URL", base);
      vi.spyOn(api.dictionary, "list").mockResolvedValue({
        count: 0, next: null, previous: null, results: [],
      });

      renderWithProviders(<DictionaryListPage />, { route: "/dictionary" });
      await screen.findByRole("link", { name: /CSV/i });

      expect(screen.getByRole("link", { name: /CSV/i })).toHaveAttribute(
        "href", `${base}/api/exports/dataset.csv`
      );
      expect(screen.getByRole("link", { name: /JSON/i })).toHaveAttribute(
        "href", `${base}/api/exports/dataset.json`
      );
    }
  );
});
