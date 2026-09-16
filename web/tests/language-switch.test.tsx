// @vitest-environment jsdom

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../src/i18n/LanguageContext";
import { AppHeader } from "../src/ui/AppHeader";

describe("language switch", () => {
  it("moves the selected segment and updates pressed state", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <MemoryRouter>
        <LanguageProvider>
          <AppHeader />
        </LanguageProvider>
      </MemoryRouter>,
    );

    const chinese = screen.getByRole("button", { name: "中文" });
    const english = screen.getByRole("button", { name: "EN" });
    expect(chinese.getAttribute("aria-pressed")).toBe("true");
    expect(container.querySelector(".language-switch")?.getAttribute("data-language")).toBe("zh");

    await user.click(english);

    expect(english.getAttribute("aria-pressed")).toBe("true");
    expect(chinese.getAttribute("aria-pressed")).toBe("false");
    expect(container.querySelector(".language-switch")?.getAttribute("data-language")).toBe("en");
  });
});
