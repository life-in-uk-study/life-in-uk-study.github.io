import type { Question } from "../types/questions";
import { EXAM_CONFIG } from "../config/exam";

export interface ExamResult {
  score: number;
  passed: boolean;
  answers: Record<string, string[]>;
}

export function createExamResult(score: number, answers: Record<string, string[]>): ExamResult {
  return {
    score,
    passed: score >= EXAM_CONFIG.passingScore,
    answers: Object.fromEntries(
      Object.entries(answers).map(([questionId, selected]) => [questionId, [...selected]]),
    ),
  };
}

export function answersMatch(selected: string[], correct: string[]): boolean {
  if (selected.length !== correct.length) return false;
  const selectedSet = new Set(selected);
  return correct.every((answerId) => selectedSet.has(answerId));
}

export function scoreExam(questions: Question[], answers: Record<string, string[]>): number {
  return questions.reduce(
    (score, question) => score + (answersMatch(answers[question.id] ?? [], question.correct_option_ids) ? 1 : 0),
    0,
  );
}

export interface ReviewNavigation {
  correctIndexes: Set<number>;
  incorrectIndexes: Set<number>;
  firstIncorrectIndex: number;
}

export function createReviewNavigation(
  questions: Question[],
  answers: Record<string, string[]>,
): ReviewNavigation {
  const correctIndexes = new Set<number>();
  const incorrectIndexes = new Set<number>();

  questions.forEach((question, index) => {
    const target = answersMatch(answers[question.id] ?? [], question.correct_option_ids)
      ? correctIndexes
      : incorrectIndexes;
    target.add(index);
  });

  return {
    correctIndexes,
    incorrectIndexes,
    firstIncorrectIndex: incorrectIndexes.values().next().value ?? 0,
  };
}
