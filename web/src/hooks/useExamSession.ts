import { useCallback, useEffect, useMemo, useState } from "react";
import type { ExamSession, Question } from "../types/questions";

function createExamSession(examNumber: number): ExamSession {
  return {
    examNumber,
    currentIndex: 0,
    answers: {},
    revealedQuestionIds: [],
    completedAt: null,
  };
}

export function useExamSession(examNumber: number, questions: Question[]) {
  const [session, setSession] = useState<ExamSession>(() => createExamSession(examNumber));

  useEffect(() => {
    setSession(createExamSession(examNumber));
  }, [examNumber]);

  const selectOption = useCallback((question: Question, optionId: string) => {
    setSession((current) => {
      if (current.revealedQuestionIds.includes(question.id) || current.completedAt !== null) return current;
      const selected = current.answers[question.id] ?? [];
      const nextSelected = question.type === "single"
        ? [optionId]
        : selected.includes(optionId) ? selected.filter((id) => id !== optionId) : [...selected, optionId];
      return { ...current, answers: { ...current.answers, [question.id]: nextSelected } };
    });
  }, []);

  const revealAnswer = useCallback((question: Question) => {
    setSession((current) => {
      const selected = current.answers[question.id] ?? [];
      if (selected.length === 0 || current.revealedQuestionIds.includes(question.id)) return current;
      return { ...current, revealedQuestionIds: [...current.revealedQuestionIds, question.id] };
    });
  }, []);

  const goToQuestion = useCallback((index: number) => {
    setSession((current) => ({ ...current, currentIndex: Math.min(Math.max(index, 0), questions.length - 1) }));
  }, [questions.length]);

  const completeExam = useCallback(() => {
    setSession((current) => ({ ...current, completedAt: Date.now() }));
  }, []);

  const resetExam = useCallback(() => {
    setSession(createExamSession(examNumber));
  }, [examNumber]);

  const revealedSet = useMemo(() => new Set(session.revealedQuestionIds), [session.revealedQuestionIds]);
  return { session, revealedSet, selectOption, revealAnswer, goToQuestion, completeExam, resetExam };
}
