import { useLanguage } from "../i18n/LanguageContext";
import { Typography } from "./Typography";

interface ExamStatusBarProps { examNumber: number; current: number; total: number }

export function ExamStatusBar({ examNumber, current, total }: ExamStatusBarProps) {
  const { t } = useLanguage();
  return (
    <section className="exam-status" aria-label={t("examStatus")}>
      <Typography as="span" variant="heading">Exam {examNumber}</Typography>
      <Typography as="span" variant="heading">{current} / {total}</Typography>
    </section>
  );
}
