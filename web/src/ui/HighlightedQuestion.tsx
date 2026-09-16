import type { ReactNode } from "react";
import { normalizeEnglishPunctuation } from "../services/englishPunctuation";

interface HighlightedQuestionProps {
  text: string;
  keywords: string[];
}

export function HighlightedQuestion({ text, keywords = [] }: HighlightedQuestionProps) {
  const ranges = keywords
    .flatMap((keyword) => {
      const start = text.indexOf(keyword);
      return start >= 0 ? [{ start, end: start + keyword.length }] : [];
    })
    .sort((a, b) => a.start - b.start);
  const content: ReactNode[] = [];
  let cursor = 0;
  for (const range of ranges) {
    if (range.start < cursor) continue;
    content.push(normalizeEnglishPunctuation(text.slice(cursor, range.start)));
    content.push(<span className="question-keyword" key={`${range.start}-${range.end}`}>{normalizeEnglishPunctuation(text.slice(range.start, range.end))}</span>);
    cursor = range.end;
  }
  content.push(normalizeEnglishPunctuation(text.slice(cursor)));
  return <>{content}</>;
}
