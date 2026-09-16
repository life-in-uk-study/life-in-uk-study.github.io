import { useLanguage } from "../i18n/LanguageContext";
import { Typography } from "./Typography";

interface ExamStatusBarProps { title: string; current: number; total: number }

export function ExamStatusBar({ title, current, total }: ExamStatusBarProps) {
  const { t } = useLanguage();
  return (
    <section className="exam-status" aria-label={t("examStatus")}>
      <Typography as="span" variant="heading">{title}</Typography>
      <Typography as="span" variant="heading">{current} / {total}</Typography>
    </section>
  );
}
