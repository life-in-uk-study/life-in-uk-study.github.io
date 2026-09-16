import type { QuestionBank } from "../types/questions";
import { publicAssetUrl } from "./publicAsset";

const questionBankPromises = new Map<number, Promise<QuestionBank>>();

export function loadQuestionBank(examNumber: number): Promise<QuestionBank> {
  const existingPromise = questionBankPromises.get(examNumber);
  if (existingPromise) return existingPromise;

  const filename = `exam-${String(examNumber).padStart(2, "0")}.json`;
  const request = fetch(publicAssetUrl(`/data/exams/${filename}`)).then(async (response) => {
    if (!response.ok) throw new Error("题库加载失败，请刷新页面重试。");
    const bank = (await response.json()) as QuestionBank;
    if (
      bank.exam_number !== examNumber
      || bank.question_count !== 24
      || bank.questions.length !== 24
      || bank.questions.some((question) => question.exam_number !== examNumber)
    ) {
      throw new Error("题库数据不完整，请刷新页面重试。");
    }
    return bank;
  });

  questionBankPromises.set(examNumber, request);
  request.catch(() => questionBankPromises.delete(examNumber));
  return request;
}
