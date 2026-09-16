import { useLanguage } from "../i18n/LanguageContext";
import { Typography } from "./Typography";

interface QuestionNavigatorProps {
  total: number;
  currentIndex: number;
  correctIndexes: Set<number>;
  incorrectIndexes: Set<number>;
  onSelect: (index: number) => void;
}

export function QuestionNavigator({ total, currentIndex, correctIndexes, incorrectIndexes, onSelect }: QuestionNavigatorProps) {
  const { t } = useLanguage();
  return (
    <nav className="question-nav" aria-label={t("questionNavigation")}>
      {Array.from({ length: total }, (_, index) => {
        const questionNumber = index + 1;
        const isCurrent = index === currentIndex;
        const isCorrect = correctIndexes.has(index);
        const isIncorrect = incorrectIndexes.has(index);
        const status = isCorrect ? t("correctAnswerSuffix") : isIncorrect ? t("incorrectAnswerSuffix") : "";
        return (
          <button
            key={index}
            type="button"
            className={`question-nav__item${isCurrent ? " is-current" : ""}${isCorrect ? " is-correct" : ""}${isIncorrect ? " is-incorrect" : ""}`}
            onClick={() => onSelect(index)}
            aria-current={isCurrent ? "step" : undefined}
            aria-label={t("questionLabel", { number: questionNumber, answered: status })}
          >
            <Typography as="span" variant="utility">{questionNumber}</Typography>
          </button>
        );
      })}
    </nav>
  );
}
