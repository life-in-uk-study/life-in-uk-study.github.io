import type { QuestionBank } from "../types/questions";
import { EXAM_CONFIG } from "../config/exam";
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

export interface RandomQuestionCoordinate {
  examNumber: number;
  questionIndex: number;
}

export function sampleRandomQuestionCoordinates(
  random: () => number = Math.random,
): RandomQuestionCoordinate[] {
  const totalQuestions = EXAM_CONFIG.examCount * EXAM_CONFIG.questionsPerExam;
  const indexes = Array.from({ length: totalQuestions }, (_, index) => index);

  for (let index = 0; index < EXAM_CONFIG.questionsPerExam; index += 1) {
    const remaining = totalQuestions - index;
    const offset = Math.min(Math.floor(random() * remaining), remaining - 1);
    const swapIndex = index + offset;
    [indexes[index], indexes[swapIndex]] = [indexes[swapIndex], indexes[index]];
  }

  return indexes.slice(0, EXAM_CONFIG.questionsPerExam).map((index) => ({
    examNumber: Math.floor(index / EXAM_CONFIG.questionsPerExam) + 1,
    questionIndex: index % EXAM_CONFIG.questionsPerExam,
  }));
}

export async function loadRandomQuestionBank(
  random: () => number = Math.random,
): Promise<QuestionBank> {
  const coordinates = sampleRandomQuestionCoordinates(random);
  const examNumbers = [...new Set(coordinates.map(({ examNumber }) => examNumber))];
  const banks = await Promise.all(examNumbers.map(loadQuestionBank));
  const bankByExam = new Map(banks.map((bank) => [bank.exam_number, bank]));

  return {
    dataset: "random-selection",
    exam_number: 0,
    question_count: EXAM_CONFIG.questionsPerExam,
    authority_sources: Object.assign({}, ...banks.map((bank) => bank.authority_sources)),
    questions: coordinates.map(({ examNumber, questionIndex }) => {
      const question = bankByExam.get(examNumber)?.questions[questionIndex];
      if (!question) throw new Error("随机题目加载失败，请重新抽题。");
      return question;
    }),
  };
}
