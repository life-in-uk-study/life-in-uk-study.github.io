import { ArrowRight, BookOpenText, CheckCircle, Circle, XCircle } from "@phosphor-icons/react";
import { Link } from "react-router-dom";
import { EXAM_CONFIG } from "../config/exam";
import { useLanguage } from "../i18n/LanguageContext";
import type { ExamResult } from "../services/exam";
import { publicAssetUrl } from "../services/publicAsset";
import { Typography } from "../ui/Typography";

export function HomePage({ examResults = {} }: { examResults?: Partial<Record<number, ExamResult>> }) {
  const { t } = useLanguage();
  return (
    <main className="page home-page">
      <section className="home-intro">
        <div className="home-intro__content">
          <Typography as="p" variant="label" className="eyebrow">{t("heroEyebrow")}</Typography>
          <Typography as="h1" variant="display">{t("heroTitle")}</Typography>
          <Typography as="p" variant="body" className="home-intro__copy">{t("heroCopy")}</Typography>
        </div>
        <figure className="home-intro__visual">
          <img src={publicAssetUrl("/images/featured/union-jack-homepage.png")} alt={t("flagAlt")} />
        </figure>
      </section>
      <section className="home-reference-section" aria-labelledby="quick-reference-home-title">
        <Link className="home-reference-card" to="/quick-reference">
          <span className="home-reference-card__icon" aria-hidden="true">
            <BookOpenText weight="regular" />
          </span>
          <div className="home-reference-card__copy">
            <Typography as="h2" variant="title" id="quick-reference-home-title">{t("quickReferenceTitle")}</Typography>
            <Typography as="p" variant="body" className="home-reference-card__description">{t("quickReferenceEntryCopy")}</Typography>
          </div>
          <span className="home-reference-card__action" aria-hidden="true">
            <ArrowRight />
          </span>
        </Link>
      </section>
      <section className="home-exams-section" aria-labelledby="exam-list-title">
        <div className="section-heading">
          <div>
            <Typography as="p" variant="label" className="eyebrow">{t("chooseSet")}</Typography>
            <Typography as="h2" variant="title" id="exam-list-title">{t("mockExams")}</Typography>
          </div>
          <Typography as="p" variant="label" className="exam-rules-note">
            {t("examRulesSummary", {
              total: EXAM_CONFIG.questionsPerExam,
              minutes: EXAM_CONFIG.officialDurationMinutes,
              score: EXAM_CONFIG.passingScore,
            })}
          </Typography>
        </div>
        <div className="exam-grid">
          {Array.from({ length: EXAM_CONFIG.examCount }, (_, index) => {
            const examNumber = index + 1;
            const result = examResults[examNumber];
            const resultClass = result ? result.passed ? "exam-card--passed" : "exam-card--failed" : "";
            const StatusIcon = result ? result.passed ? CheckCircle : XCircle : Circle;
            return (
              <Link className={`exam-card ${resultClass}`.trim()} to={`/exam/${examNumber}`} key={examNumber}>
                <StatusIcon className="exam-card__status-icon" weight="fill" aria-hidden="true" />
                <div className="exam-card__copy">
                  <Typography as="h3" variant="heading">Exam {examNumber}</Typography>
                  {result ? <Typography as="p" variant="utility" className="exam-card__result">{t(result.passed ? "examCardPassed" : "examCardFailed", { score: result.score, total: EXAM_CONFIG.questionsPerExam })}</Typography> : null}
                </div>
                <ArrowRight aria-hidden="true" />
              </Link>
            );
          })}
        </div>
      </section>
    </main>
  );
}
