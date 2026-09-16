export type QuestionType = "single" | "multiple";

export interface QuestionOption { id: string; text: string }
export interface LearningContent {
  why_correct_en: string;
  why_correct_zh: string;
  answer_summary_zh: string;
  keywords: string[];
}
export interface FilmConnection {
  title: string;
  year: number;
  relationship: "direct" | "background";
  poster_src: string;
  poster_alt_en: string;
  poster_alt_zh: string;
  fun_fact_en: string;
  fun_fact_zh: string;
  source_title: string;
  source_url: string;
  poster_provider: string;
  poster_provider_url: string;
  poster_credit_notice: string;
}
export interface QuestionVisual {
  src: string;
  kind: string;
  display_after_answer: boolean;
  alt_zh: string;
  fact_source_ids: string[];
  credit?: string;
  credit_url?: string;
}
export interface Question {
  id: string;
  number: number;
  exam_number: number;
  question: string;
  type: QuestionType;
  options: QuestionOption[];
  correct_option_ids: string[];
  correct_answers: string[];
  explanation: string;
  category_name: string;
  handbook_locator: string;
  learning: LearningContent;
  authoritative_source_ids: string[];
  visual: QuestionVisual;
  film_connection: FilmConnection | null;
}
export interface AuthoritySource {
  title: string;
  publisher: string;
  url: string;
  authority: string;
  note_zh: string;
  isbn?: string;
}
export interface QuestionBank {
  dataset: string;
  exam_number: number;
  question_count: number;
  authority_sources: Record<string, AuthoritySource>;
  questions: Question[];
}
export interface ExamSession {
  examNumber: number;
  currentIndex: number;
  answers: Record<string, string[]>;
  revealedQuestionIds: string[];
  completedAt: number | null;
}
