import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { api, ApiError } from "../../../shared/api/client";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { RegisterPage } from "../RegisterPage";
import { AcceptTermsBanner } from "../AcceptTermsBanner";

describe("RegisterPage and AcceptTermsBanner", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("requires the accept_terms checkbox before submitting", async () => {
    const user = userEvent.setup();
    const registerSpy = vi.spyOn(api.auth, "register");

    renderWithProviders(<RegisterPage />, {
      route: "/register",
      path: "/register",
    });

    await user.type(
      screen.getByLabelText(/Имя пользователя/i),
      "new_participant"
    );
    await user.type(
      screen.getByLabelText(/Электронная почта/i),
      "new@example.com"
    );
    await user.type(screen.getByLabelText(/Пароль/i), "StrongPass123!");

    await user.click(
      screen.getByRole("button", { name: /Зарегистрироваться/i })
    );

    expect(registerSpy).not.toHaveBeenCalled();
    expect(
      await screen.findByText(/Необходимо принять условия публикации/i)
    ).toBeInTheDocument();
  });

  it("displays server field errors returned by POST /api/auth/register/", async () => {
    const user = userEvent.setup();
    vi.spyOn(api.auth, "csrf").mockResolvedValueOnce(undefined);
    vi.spyOn(api.auth, "register").mockRejectedValueOnce(
      new ApiError(400, "Validation failed", {
        fieldErrors: {
          username: ["Это имя пользователя уже занято."],
          email: ["Аккаунт с такой почтой уже существует."],
        },
      })
    );

    renderWithProviders(<RegisterPage />, {
      route: "/register",
      path: "/register",
    });

    await user.type(screen.getByLabelText(/Имя пользователя/i), "existing");
    await user.type(
      screen.getByLabelText(/Электронная почта/i),
      "existing@example.com"
    );
    await user.type(screen.getByLabelText(/Пароль/i), "StrongPass123!");
    await user.click(
      screen.getByRole("checkbox", { name: /Я принимаю условия публикации/i })
    );
    await user.click(
      screen.getByRole("button", { name: /Зарегистрироваться/i })
    );

    expect(
      await screen.findByText("Это имя пользователя уже занято.")
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Аккаунт с такой почтой уже существует.")
    ).toBeInTheDocument();
  });

  it("shows AcceptTermsBanner when user.accepted_terms is false and submits acceptTerms", async () => {
    const user = userEvent.setup();
    const acceptSpy = vi.spyOn(api.auth, "acceptTerms").mockResolvedValueOnce({
      id: 7,
      username: "legacy_user",
      email: "legacy@example.com",
      display_name: "Legacy",
      role: "participant",
      accepted_terms: true,
      accepted_terms_version: "1.0",
    });

    renderWithProviders(<AcceptTermsBanner />, {
      user: {
        id: 7,
        username: "legacy_user",
        email: "legacy@example.com",
        display_name: "Legacy",
        role: "participant",
        accepted_terms: false,
        accepted_terms_version: "",
      },
    });

    const button = screen.getByRole("button", {
      name: /Принять условия публикации/i,
    });
    expect(button).toBeInTheDocument();

    await user.click(button);
    expect(acceptSpy).toHaveBeenCalledTimes(1);
  });
});

