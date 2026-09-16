import { EXAM_CONFIG } from "../config/exam";
import { useLanguage } from "../i18n/LanguageContext";
import { Button } from "./Button";
import { Typography } from "./Typography";

export function ExamSummary({ score, onRestart }: { score: number; onRestart: () => void }) {
  const { t } = useLanguage();
  const passed = score >= EXAM_CONFIG.passingScore;
  return (
    <section className="exam-summary">
      <Typography as="p" variant="label" className="eyebrow">{t("examFinished")}</Typography>
      <Typography as="h1" variant="display">{score} / {EXAM_CONFIG.questionsPerExam}</Typography>
      <Typography as="p" variant="heading">{passed ? t("passed") : t("notPassed")}</Typography>
      <Typography as="p" variant="body">
        {t("passingStandard", { score: EXAM_CONFIG.passingScore, total: EXAM_CONFIG.questionsPerExam })}
      </Typography>
      <Button onClick={onRestart}>{t("restartExam")}</Button>
    </section>
  );
}
