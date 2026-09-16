import { describe, expect, it } from "vitest";
import { answersMatch, createExamResult, createReviewNavigation } from "../src/services/exam";
import type { Question } from "../src/types/questions";

describe("exam helpers", () => {
  it("matches multi-select answers regardless of order", () => { expect(answersMatch(["r1", "r0"], ["r0", "r1"])).toBe(true); });
  it("rejects incomplete multi-select answers", () => { expect(answersMatch(["r0"], ["r0", "r1"])).toBe(false); });
  it("passes at 18 out of 24 and fails below the boundary", () => {
    expect(createExamResult(18, { q1: ["a"] })).toEqual({ score: 18, passed: true, answers: { q1: ["a"] } });
    expect(createExamResult(17, { q1: ["b"] })).toEqual({ score: 17, passed: false, answers: { q1: ["b"] } });
  });
  it("keeps every question in review navigation and marks only incorrect answers red", () => {
    const questions = [
      { id: "q1", correct_option_ids: ["a"] },
      { id: "q2", correct_option_ids: ["b", "c"] },
      { id: "q3", correct_option_ids: ["d"] },
    ] as Question[];

    const review = createReviewNavigation(questions, {
      q1: ["a"],
      q2: ["b"],
      q3: ["d"],
    });

    expect([...review.correctIndexes]).toEqual([0, 2]);
    expect([...review.incorrectIndexes]).toEqual([1]);
    expect(review.firstIncorrectIndex).toBe(1);
  });
});
