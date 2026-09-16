import type { Question } from "../types/questions";
import type { Language } from "../i18n/translations";
import { publicAssetUrl } from "./publicAsset";

type VisualKind = "poster" | "photo" | "portrait" | "illustration" | "study-card";

type VisualOverride = {
  src: string;
  alt: Record<Language, string>;
  kind: VisualKind;
  credit?: string;
  creditUrl?: string;
};

const VISUAL_OVERRIDES: Record<string, VisualOverride> = {
  "exam-01-q02": {
    src: "/images/featured/big-ben-palace-of-westminster.png",
    kind: "photo",
    alt: {
      zh: "从泰晤士河对岸看到的英国议会大厦和伊丽莎白塔。",
      en: "The Palace of Westminster and Elizabeth Tower seen across the River Thames.",
    },
  },
  "exam-01-q05": {
    src: "/images/featured/saint-andrew-rubens.jpg",
    kind: "portrait",
    alt: {
      zh: "彼得·保罗·鲁本斯约1610至1612年创作的《圣安德鲁》；画中的X形十字架象征圣安德鲁殉道。",
      en: "Peter Paul Rubens's Saint Andrew (c. 1610-1612), showing the apostle beside the X-shaped cross associated with his martyrdom.",
    },
  },
  "exam-01-q08": {
    src: "/images/featured/the-cenotaph-whitehall.jpg",
    kind: "photo",
    alt: {
      zh: "伦敦白厅道路中央的The Cenotaph实景照片，碑前摆放着纪念花圈。",
      en: "The Cenotaph standing in the middle of Whitehall, London, with remembrance wreaths at its base.",
    },
    credit: "Photo: Paul the Archivist / Wikimedia Commons (CC BY-SA 4.0)",
    creditUrl: "https://commons.wikimedia.org/wiki/File:The_Cenotaph,_Whitehall,_London.jpg",
  },
  ...Object.fromEntries(
    ["exam-01-q09", "exam-11-q08", "exam-17-q05"].map((questionId) => [questionId, {
      src: "/images/featured/margaret-thatcher-1983.jpg",
      kind: "portrait" as const,
      alt: {
        zh: "玛格丽特·撒切尔1983年的黑白肖像照片。",
        en: "A black-and-white portrait of Margaret Thatcher taken in 1983.",
      },
      credit: "Photo: Rob Bogaerts / Anefo / Nationaal Archief (CC0)",
      creditUrl: "https://commons.wikimedia.org/wiki/File:Margaret_Thatcher_(1983).jpg",
    }]),
  ),
};

export type QuestionVisualPresentation = {
  src: string;
  alt: string;
  kind: VisualKind;
  credit?: string;
  creditUrl?: string;
};

export function getQuestionVisual(question: Question, language: Language = "zh"): QuestionVisualPresentation {
  if (question.film_connection) {
    return {
      src: publicAssetUrl(question.film_connection.poster_src),
      alt: language === "zh" ? question.film_connection.poster_alt_zh : question.film_connection.poster_alt_en,
      kind: "poster",
    };
  }
  const override = VISUAL_OVERRIDES[question.id];
  if (override) return {
    src: publicAssetUrl(override.src),
    alt: override.alt[language],
    kind: override.kind,
    credit: override.credit,
    creditUrl: override.creditUrl,
  };
  return {
    src: publicAssetUrl(question.visual.src),
    alt: question.visual.kind === "ai_learning_illustration"
      ? language === "zh"
        ? question.visual.alt_zh
        : `AI-generated learning illustration for: ${question.question}`
      : language === "zh"
        ? `题目相关的答案记忆图：${question.question}`
        : `Answer memory image for: ${question.question}`,
    kind: question.visual.kind === "ai_learning_illustration" ? "illustration" : "study-card",
  };
}
