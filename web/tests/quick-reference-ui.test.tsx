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

const examData = {
  dataset: "test",
  exam_number: 1,
  question_count: 24,
  authority_sources: {
    handbook: {
      title: "Life in the United Kingdom: A Guide for New Residents",
      publisher: "Home Office",
      url: "https://www.gov.uk/government/publications/life-in-the-united-kingdom-a-guide-for-new-residents",
      authority: "official",
      note_zh: "官方考试手册",
    },
  },
  questions: Array.from({ length: 24 }, (_, index) => ({
    id: `exam-01-q${String(index + 1).padStart(2, "0")}`,
    number: index + 1,
    exam_number: 1,
    question: index === 0 ? "Who led the first invasion of Britain?" : `Question ${index + 1}`,
    type: "single",
    options: [{ id: "a", text: "Julius Caesar" }],
    correct_option_ids: ["a"],
    correct_answers: ["Julius Caesar"],
    explanation: "Julius Caesar led the first Roman invasion.",
    category_name: "History",
    handbook_locator: "History",
    learning: {
      why_correct_en: "Julius Caesar led Roman expeditions to Britain in 55 and 54 BC.",
      why_correct_zh: "Julius Caesar在公元前55年和54年率领罗马军队远征不列颠。",
      answer_summary_zh: "Julius Caesar",
      keywords: ["Julius Caesar"],
    },
    authoritative_source_ids: ["handbook"],
    visual: { src: "", kind: "illustration", display_after_answer: true, alt_zh: "", fact_source_ids: [] },
    film_connection: null,
  })),
};

describe("quick-reference chapter disclosures", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockImplementation((url: string) => Promise.resolve({
      ok: true,
      json: async () => url.includes("/data/exams/") ? examData : quickReferenceData,
    })));
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

    const explanationToggle = screen.getByRole("button", { name: /展开答案解析：Who led the first invasion of Britain/ });
    await user.click(explanationToggle);
    expect(await screen.findByText("Julius Caesar在公元前55年和54年率领罗马军队远征不列颠。")).toBeTruthy();
    expect(screen.getByRole("link", { name: /Life in the United Kingdom/ })).toBeTruthy();
    expect(fetch).toHaveBeenCalledWith("/data/exams/exam-01.json");
    expect(screen.getByRole("button", { name: /收起答案解析：Who led the first invasion of Britain/ }).getAttribute("aria-expanded")).toBe("true");
  });
});
