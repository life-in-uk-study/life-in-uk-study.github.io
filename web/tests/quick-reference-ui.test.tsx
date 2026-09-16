/** @vitest-environment jsdom */

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LanguageProvider } from "../src/i18n/LanguageContext";
import { QuickReferencePage } from "../src/pages/QuickReferencePage";

const quickReferenceData = {
  dataset: "test",
  source_question_count: 2,
  group_count: 2,
  sections: [
    {
      id: "history",
      title_en: "History",
      title_zh: "历史",
      question_count: 1,
      rows: [{
        topic_id: "roman-britain",
        topic_en: "Roman Britain",
        topic_zh: "罗马时期",
        detail_topic_id: "roman-invasion",
        detail_topic_en: "Roman invasion",
        detail_topic_zh: "罗马入侵",
        prompts: ["Who led the first invasion of Britain?"],
        answers: ["Julius Caesar"],
        frequency: 1,
        question_ids: ["exam-01-q01"],
      }],
    },
    {
      id: "politics",
      title_en: "Politics",
      title_zh: "政治",
      question_count: 1,
      rows: [{
        topic_id: "parliament",
        topic_en: "Parliament",
        topic_zh: "议会",
        prompts: ["Where does Parliament meet?"],
        answers: ["Westminster"],
        frequency: 1,
        question_ids: ["exam-01-q02"],
      }],
    },
  ],
};

describe("quick-reference chapter disclosures", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => quickReferenceData,
    }));
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("starts with every title-one chapter collapsed and toggles chapters independently", async () => {
    const user = userEvent.setup();
    render(<LanguageProvider><QuickReferencePage /></LanguageProvider>);

    const historyToggle = await screen.findByRole("button", { name: "展开历史" });
    const politicsToggle = screen.getByRole("button", { name: "展开政治" });
    expect(historyToggle.getAttribute("aria-expanded")).toBe("false");
    expect(politicsToggle.getAttribute("aria-expanded")).toBe("false");

    await user.click(historyToggle);
    await waitFor(() => expect(screen.getByRole("button", { name: "收起历史" }).getAttribute("aria-expanded")).toBe("true"));
    expect(screen.getByRole("heading", { name: /罗马时期/ })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /罗马入侵/ })).toBeTruthy();
    expect(politicsToggle.getAttribute("aria-expanded")).toBe("false");
  });
});
