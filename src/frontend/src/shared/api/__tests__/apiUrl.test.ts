import { afterEach, describe, expect, it, vi } from "vitest";
import { apiUrl } from "../apiUrl";

afterEach(() => vi.unstubAllEnvs());

describe("apiUrl", () => {
  it.each([undefined, ""])("keeps relative paths when the base is %s", (base) => {
    vi.stubEnv("VITE_API_BASE_URL", base);
    expect(apiUrl("/api/tasks/")).toBe("/api/tasks/");
  });

  it.each(["https://api.example.test", "https://api.example.test/"])(
    "prefixes API paths with %s",
    (base) => {
      vi.stubEnv("VITE_API_BASE_URL", base);
      expect(apiUrl("/api/exports/dataset.csv")).toBe(
        "https://api.example.test/api/exports/dataset.csv"
      );
    }
  );
});
