import { useEffect, useState } from "react";
import { loadRandomQuestionBank } from "../services/questionBank";
import type { QuestionBank } from "../types/questions";

interface RandomQuestionBankState {
  bank: QuestionBank | null;
  error: string | null;
}

export function useRandomQuestionBank(generation: number): RandomQuestionBankState {
  const [state, setState] = useState<RandomQuestionBankState>({ bank: null, error: null });

  useEffect(() => {
    let active = true;
    setState({ bank: null, error: null });
    loadRandomQuestionBank()
      .then((bank) => { if (active) setState({ bank, error: null }); })
      .catch((error: unknown) => {
        if (active) setState({ bank: null, error: error instanceof Error ? error.message : "随机题目加载失败。" });
      });
    return () => { active = false; };
  }, [generation]);

  return state;
}
