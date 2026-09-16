import { describe, expect, it } from "vitest";
import { getQuestionVisual } from "../src/services/questionVisual";
import type { Question } from "../src/types/questions";

const filmQuestion = {
  id: "exam-01-q03",
  question: "When were men and women given the right to vote at the age of 21?",
  visual: { src: "/images/questions/exam-01-q03.svg" },
  film_connection: {
    poster_src: "/images/media/suffragette-2015-poster.jpg",
    poster_alt_en: "The theatrical poster for Suffragette (2015).",
    poster_alt_zh: "电影《Suffragette》（2015）的正式海报。",
  },
} as Question;

describe("question visual selection", () => {
  it("uses the real film poster in the single answer-image slot", () => {
    expect(getQuestionVisual(filmQuestion, "zh")).toEqual({
      src: "/images/media/suffragette-2015-poster.jpg",
      alt: "电影《Suffragette》（2015）的正式海报。",
      kind: "poster",
    });
  });

  it("uses Rubens's Saint Andrew painting for the Saint Andrew question", () => {
    const saintAndrewQuestion = {
      ...filmQuestion,
      id: "exam-01-q05",
      question: "Who is the patron Saint of Scotland?",
      film_connection: null,
    } as Question;

    expect(getQuestionVisual(saintAndrewQuestion, "zh")).toEqual({
      src: "/images/featured/saint-andrew-rubens.jpg",
      alt: "彼得·保罗·鲁本斯约1610至1612年创作的《圣安德鲁》；画中的X形十字架象征圣安德鲁殉道。",
      kind: "portrait",
    });

    expect(getQuestionVisual(saintAndrewQuestion, "en")?.alt).toBe(
      "Peter Paul Rubens's Saint Andrew (c. 1610-1612), showing the apostle beside the X-shaped cross associated with his martyrdom.",
    );
  });

  it("uses an AI learning illustration instead of the answer-memory card when available", () => {
    const aiQuestion = {
      ...filmQuestion,
      id: "exam-01-q01",
      question: "What are two responsibilities that you will have as a British citizen or permanent resident of the UK?",
      visual: {
        src: "/images/ai/exam-01-q01.webp",
        kind: "ai_learning_illustration",
        alt_zh: "根据题目及正确答案生成的AI学习插图。",
      },
      film_connection: null,
    } as Question;

    expect(getQuestionVisual(aiQuestion, "zh")).toEqual({
      src: "/images/ai/exam-01-q01.webp",
      alt: "根据题目及正确答案生成的AI学习插图。",
      kind: "illustration",
    });
    expect(getQuestionVisual(aiQuestion, "en").alt).toBe(
      "AI-generated learning illustration for: What are two responsibilities that you will have as a British citizen or permanent resident of the UK?",
    );
  });
});
