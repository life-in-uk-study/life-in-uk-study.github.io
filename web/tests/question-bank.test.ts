import { afterEach, describe, expect, it, vi } from "vitest";
import { loadQuestionBank, loadRandomQuestionBank, sampleRandomQuestionCoordinates } from "../src/services/questionBank";

function examPayload(examNumber: number) {
  return {
    dataset: "test",
    exam_number: examNumber,
    question_count: 24,
    authority_sources: {},
    questions: Array.from({ length: 24 }, () => ({ exam_number: examNumber })),
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("split exam question loading", () => {
  it("loads only the requested zero-padded exam file", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => examPayload(3),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadQuestionBank(3)).resolves.toMatchObject({ exam_number: 3 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith("/data/exams/exam-03.json");
  });

  it("caches each exam independently", async () => {
    const fetchMock = vi.fn().mockImplementation(async (url: string) => ({
      ok: true,
      json: async () => examPayload(url.includes("exam-12") ? 12 : 11),
    }));
    vi.stubGlobal("fetch", fetchMock);

    const first = loadQuestionBank(11);
    const repeated = loadQuestionBank(11);
    const otherExam = loadQuestionBank(12);

    expect(repeated).toBe(first);
    await Promise.all([first, repeated, otherExam]);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});

describe("random question selection", () => {
  it("draws 24 unique question coordinates from the 17 exam pool", () => {
    let value = 0;
    const selection = sampleRandomQuestionCoordinates(() => {
      value = (value + 0.173) % 1;
      return value;
    });
    const keys = selection.map(({ examNumber, questionIndex }) => `${examNumber}-${questionIndex}`);

    expect(selection).toHaveLength(24);
    expect(new Set(keys)).toHaveLength(24);
    expect(selection.every(({ examNumber }) => examNumber >= 1 && examNumber <= 17)).toBe(true);
    expect(selection.every(({ questionIndex }) => questionIndex >= 0 && questionIndex < 24)).toBe(true);
  });

  it("loads the selected exam data and returns a 24-question random bank", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => examPayload(1),
    });
    vi.stubGlobal("fetch", fetchMock);

    const bank = await loadRandomQuestionBank(() => 0);

    expect(bank.exam_number).toBe(0);
    expect(bank.question_count).toBe(24);
    expect(bank.questions).toHaveLength(24);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith("/data/exams/exam-01.json");
  });
});
