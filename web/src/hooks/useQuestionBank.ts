import { useEffect, useState } from "react";
import { loadQuestionBank } from "../services/questionBank";
import type { QuestionBank } from "../types/questions";

interface QuestionBankState { bank: QuestionBank | null; error: string | null }

export function useQuestionBank(examNumber: number | null): QuestionBankState {
  const [state, setState] = useState<QuestionBankState>({ bank: null, error: null });
  useEffect(() => {
    if (examNumber === null) return;
    let active = true;
    setState({ bank: null, error: null });
    loadQuestionBank(examNumber)
      .then((bank) => { if (active) setState({ bank, error: null }); })
      .catch((error: unknown) => {
        if (active) setState({ bank: null, error: error instanceof Error ? error.message : "题库加载失败。" });
    });
    return () => { active = false; };
  }, [examNumber]);
  return state;
}
