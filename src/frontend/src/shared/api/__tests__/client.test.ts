import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiRequest } from "../client";

describe("apiRequest client", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    document.cookie = "csrftoken=test-csrf-token-123";
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    fetchMock.mockReset();
    document.cookie = "csrftoken=; Max-Age=0";
  });

  it("does not send X-CSRFToken on GET requests", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );

    await apiRequest("/api/health/", { method: "GET" });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Record<string, string>;
    expect(headers["X-CSRFToken"]).toBeUndefined();
    expect(init.credentials).toBe("same-origin");
  });

  it.each(["POST", "PUT", "PATCH", "DELETE"] as const)(
    "sends X-CSRFToken header on unsafe %s requests",
    async (method) => {
      fetchMock.mockResolvedValueOnce(
        new Response(null, {
          status: 204,
        })
      );

      await apiRequest("/api/test/", { method, body: { a: 1 } });

      const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
      const headers = init.headers as Record<string, string>;
      expect(headers["X-CSRFToken"]).toBe("test-csrf-token-123");
      expect(init.credentials).toBe("same-origin");
    }
  );

  it("parses FieldErrors responses into ApiError.fieldErrors", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          username: ["This username is already taken."],
          password: ["This password is too short."],
        }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    await expect(
      apiRequest("/api/auth/register/", {
        method: "POST",
        body: { username: "taken" },
      })
    ).rejects.toMatchObject({
      name: "ApiError",
      status: 400,
      hasFieldErrors: true,
      fieldErrors: {
        username: ["This username is already taken."],
        password: ["This password is too short."],
      },
    });
  });

  it("parses DetailError responses into ApiError.detail", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          detail: "Authentication credentials were not provided.",
        }),
        {
          status: 403,
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    try {
      await apiRequest("/api/auth/me/", { method: "GET" });
      expect.fail("Expected apiRequest to throw ApiError");
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.status).toBe(403);
      expect(apiErr.detail).toBe(
        "Authentication credentials were not provided."
      );
      expect(apiErr.hasFieldErrors).toBe(false);
    }
  });
});

