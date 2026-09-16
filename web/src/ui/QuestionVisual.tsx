import type { Language } from "../i18n/translations";
import { getQuestionVisual } from "../services/questionVisual";
import type { Question } from "../types/questions";
import { Typography } from "./Typography";

interface QuestionVisualProps {
  question: Question;
  language: Language;
  className?: string;
}

export function QuestionVisual({ question, language, className = "" }: QuestionVisualProps) {
  const visual = getQuestionVisual(question, language);
  const classes = [`answer-visual`, `answer-visual--${visual.kind}`, className].filter(Boolean).join(" ");

  return (
    <figure className={classes}>
      <img src={visual.src} alt={visual.alt} loading="lazy" />
      {visual.credit && visual.creditUrl ? (
        <Typography as="figcaption" variant="utility" className="answer-visual__credit">
          <a href={visual.creditUrl} target="_blank" rel="noreferrer">{visual.credit}</a>
        </Typography>
      ) : null}
    </figure>
  );
}
