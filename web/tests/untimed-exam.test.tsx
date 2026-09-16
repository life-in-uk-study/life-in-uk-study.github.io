// @vitest-environment jsdom

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../src/i18n/LanguageContext";
import { ExamStatusBar } from "../src/ui/ExamStatusBar";

describe("untimed exam status", () => {
  it("shows progress without a countdown", () => {
    render(
      <LanguageProvider>
        <ExamStatusBar title="Exam 3" current={7} total={24} />
      </LanguageProvider>,
    );

    expect(screen.getByText("Exam 3")).toBeTruthy();
    expect(screen.getByText("7 / 24")).toBeTruthy();
    expect(screen.queryByText("剩余时间")).toBeNull();
    expect(screen.queryByRole("timer")).toBeNull();
  });
});
