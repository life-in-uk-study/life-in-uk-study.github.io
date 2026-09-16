import { CaretDown } from "@phosphor-icons/react";
import { useState } from "react";
import type { Language } from "../i18n/translations";
import { normalizeEnglishPunctuation } from "../services/englishPunctuation";
import {
  buildQuickReferenceDetailGroups,
  buildQuickReferenceSubsections,
  countReferencedQuestions,
  loadQuickReferenceExplanation,
  type QuickReferenceExplanation,
  type QuickReferenceDetailGroup,
  type QuickReferenceRow,
  type QuickReferenceSection as QuickReferenceSectionData,
  type QuickReferenceSubsection,
} from "../services/quickReference";
import { useLanguage } from "../i18n/LanguageContext";
import { Typography } from "./Typography";
import { QuestionVisual } from "./QuestionVisual";

interface QuickReferenceSectionProps {
  section: QuickReferenceSectionData;
  rank: number;
  language: Language;
  expanded: boolean;
  onToggle: () => void;
}

function localized(language: Language, english: string | undefined, chinese: string | undefined): string {
  return (language === "zh" ? chinese : english) ?? "";
}

export function QuickReferenceSection({ section, rank, language, expanded, onToggle }: QuickReferenceSectionProps) {
  const { t } = useLanguage();
  const title = localized(language, section.title_en, section.title_zh);
  const subsections = buildQuickReferenceSubsections(
    section,
    t("quickReferenceOtherEn"),
    t("quickReferenceOtherZh"),
  );

  return (
    <section className="quick-reference-section" aria-labelledby={`quick-reference-${section.id}`}>
      <div className="quick-reference-section__heading">
        <div>
          <Typography as="p" variant="utility" className="quick-reference-section__rank">
            {t("quickReferencePriority", { rank })}
          </Typography>
          <Typography as="h2" variant="title" id={`quick-reference-${section.id}`}>
            <button
              type="button"
              className="quick-reference-section__toggle"
              aria-expanded={expanded}
              aria-controls={`quick-reference-${section.id}-content`}
              aria-label={t(expanded ? "quickReferenceCollapseSection" : "quickReferenceExpandSection", { title })}
              onClick={onToggle}
            >
              <span>{title}</span>
              <CaretDown aria-hidden="true" />
            </button>
          </Typography>
        </div>
        <Typography as="span" variant="label" className="quick-reference-section__count">
          {t("quickReferenceQuestionCount", { count: section.question_count })}
        </Typography>
      </div>

      <div className="quick-reference-subsections" id={`quick-reference-${section.id}-content`} hidden={!expanded}>
        {subsections.map((subsection) => (
          <QuickReferenceSubsectionView
            key={subsection.id}
            sectionId={section.id}
            subsection={subsection}
            language={language}
          />
        ))}
      </div>
    </section>
  );
}

function QuickReferenceSubsectionView({ sectionId, subsection, language }: {
  sectionId: string;
  subsection: QuickReferenceSubsection;
  language: Language;
}) {
  const { t } = useLanguage();
  const period = localized(language, subsection.period_en, subsection.period_zh);
  return (
    <section className="quick-reference-subsection" id={`quick-reference-${sectionId}-${subsection.id}`}>
      <Typography as="h3" variant="heading" className="quick-reference-subsection__title">
        <span className="quick-reference-subsection__identity">
          <span>{localized(language, subsection.title_en, subsection.title_zh)}</span>
          {period ? <span className="quick-reference-subsection__period">{period}</span> : null}
        </span>
        <span className="quick-reference-subsection__frequency">
          {t("quickReferenceTopicFrequency", { count: countReferencedQuestions(subsection.rows) })}
        </span>
      </Typography>
      <div className="quick-reference-detail-groups">
        {buildQuickReferenceDetailGroups(subsection.rows).map((group, index) => (
          <QuickReferenceDetailGroupView key={group.id ?? index} group={group} language={language} />
        ))}
      </div>
    </section>
  );
}

function QuickReferenceDetailGroupView({ group, language }: {
  group: QuickReferenceDetailGroup;
  language: Language;
}) {
  const { t } = useLanguage();
  return (
    <section className="quick-reference-detail-group">
      {group.id ? (
        <Typography as="h4" variant="label" className="quick-reference-detail-group__title">
          <span className="quick-reference-detail-group__name">
            {localized(language, group.title_en, group.title_zh)}
          </span>
          <span className="quick-reference-detail-group__count">
            {t("quickReferenceTopicFrequency", { count: countReferencedQuestions(group.rows) })}
          </span>
        </Typography>
      ) : null}
      <div className="quick-reference-table-wrap">
        <table className="quick-reference-table">
          <thead><tr><th scope="col">{t("quickReferenceTopic")}</th><th scope="col">{t("quickReferenceAnswer")}</th></tr></thead>
          <tbody>
            {group.rows.map((row) => (
              <QuickReferenceRowView key={row.question_ids.join("-")} row={row} language={language} />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function QuickReferenceRowView({ row, language }: { row: QuickReferenceRow; language: Language }) {
  const { t } = useLanguage();
  const [expanded, setExpanded] = useState(false);
  const [detail, setDetail] = useState<QuickReferenceExplanation | null>(null);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);
  const question = normalizeEnglishPunctuation(row.prompts[0]);
  const answer = normalizeEnglishPunctuation(row.answers.join(" · "));
  const rowId = `quick-reference-row-${row.question_ids.join("-")}`;

  const toggleExplanation = async () => {
    if (expanded) {
      setExpanded(false);
      return;
    }

    setExpanded(true);
    if (detail || loading) return;

    setLoading(true);
    setFailed(false);
    try {
      setDetail(await loadQuickReferenceExplanation(row.question_ids[0]));
    } catch {
      setFailed(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <tr className="quick-reference-question-row">
        <td colSpan={2}>
          <button
            type="button"
            className="quick-reference-row-toggle"
            aria-expanded={expanded}
            aria-controls={`${rowId}-explanation`}
            aria-label={t(expanded ? "quickReferenceCollapseExplanation" : "quickReferenceExpandExplanation", { question })}
            onClick={toggleExplanation}
          >
            <span className="quick-reference-row-toggle__question">{question}</span>
            <span className="quick-reference-answer">{answer}</span>
            <CaretDown aria-hidden="true" />
          </button>
        </td>
      </tr>
      <tr className="quick-reference-explanation-row" hidden={!expanded}>
        <td colSpan={2} id={`${rowId}-explanation`}>
          <QuickReferenceExplanationView detail={detail} language={language} loading={loading} failed={failed} />
        </td>
      </tr>
    </>
  );
}

function QuickReferenceExplanationView({ detail, language, loading, failed }: {
  detail: QuickReferenceExplanation | null;
  language: Language;
  loading: boolean;
  failed: boolean;
}) {
  const { t } = useLanguage();
  if (loading) return <Typography as="p" variant="body">{t("quickReferenceExplanationLoading")}</Typography>;
  if (failed || !detail) return <Typography as="p" variant="body">{t("quickReferenceExplanationError")}</Typography>;

  const explanation = language === "zh"
    ? detail.question.learning.why_correct_zh
    : normalizeEnglishPunctuation(detail.question.learning.why_correct_en);

  return (
    <div className="quick-reference-explanation">
      <div className="quick-reference-explanation__text">
        <Typography as="p" variant="label">{t("quickReferenceExplanationTitle")}</Typography>
        <div className="quick-reference-explanation__copy">
          {explanation.split(/\n\n+/).map((paragraph) => (
            <Typography key={paragraph} as="p" variant="body">{paragraph}</Typography>
          ))}
        </div>
        {detail.sources.length > 0 ? (
          <div className="quick-reference-explanation__sources">
            <Typography as="p" variant="label">{t("authoritySources")}</Typography>
            {detail.sources.map((source) => (
              <a key={source.url} className="source-link" href={source.url} target="_blank" rel="noreferrer">
                <Typography as="span" variant="body">{source.title}</Typography>
                <Typography as="span" variant="utility">{source.publisher}</Typography>
              </a>
            ))}
          </div>
        ) : null}
      </div>
      <QuestionVisual question={detail.question} language={language} className="quick-reference-explanation__visual" />
    </div>
  );
}
