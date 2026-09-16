import { afterEach, describe, expect, it, vi } from "vitest";
import { loadQuestionBank } from "../src/services/questionBank";

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
