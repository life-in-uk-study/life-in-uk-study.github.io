import { CaretDown } from "@phosphor-icons/react";
import type { Language } from "../i18n/translations";
import { normalizeEnglishPunctuation } from "../services/englishPunctuation";
import {
  buildQuickReferenceDetailGroups,
  buildQuickReferenceSubsections,
  countReferencedQuestions,
  type QuickReferenceDetailGroup,
  type QuickReferenceSection as QuickReferenceSectionData,
  type QuickReferenceSubsection,
} from "../services/quickReference";
import { useLanguage } from "../i18n/LanguageContext";
import { Typography } from "./Typography";

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
              <tr key={row.question_ids.join("-")}>
                <td>{normalizeEnglishPunctuation(row.prompts[0])}</td>
                <td className="quick-reference-answer">{normalizeEnglishPunctuation(row.answers.join(" · "))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
