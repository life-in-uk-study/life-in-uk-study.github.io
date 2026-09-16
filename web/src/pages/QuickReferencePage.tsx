import { BookOpenText } from "@phosphor-icons/react";
import { useRef, useState } from "react";
import { useQuickReference } from "../hooks/useQuickReference";
import { useStickyQuickReferenceOffsets } from "../hooks/useStickyQuickReferenceOffsets";
import { useLanguage } from "../i18n/LanguageContext";
import { QuickReferenceSection } from "../ui/QuickReferenceSection";
import { Typography } from "../ui/Typography";

export function QuickReferencePage() {
  const { language, t } = useLanguage();
  const pageRef = useRef<HTMLElement>(null);
  const { data, error } = useQuickReference();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(() => new Set());
  const stickyRefreshKey = `${language}:${data?.group_count ?? 0}:${[...expandedSections].join(",")}`;

  useStickyQuickReferenceOffsets(pageRef, stickyRefreshKey);

  const toggleSection = (sectionId: string) => {
    setExpandedSections((current) => {
      const next = new Set(current);
      if (next.has(sectionId)) next.delete(sectionId);
      else next.add(sectionId);
      return next;
    });
  };

  if (error) return <QuickReferenceMessage text={t("quickReferenceError")} />;
  if (!data) return <QuickReferenceMessage text={t("quickReferenceLoading")} />;

  return (
    <main className="page quick-reference-page" ref={pageRef}>
      <header className="quick-reference-intro">
        <BookOpenText aria-hidden="true" />
        <div>
          <Typography as="p" variant="label" className="eyebrow">{t("quickReferenceEyebrow")}</Typography>
          <Typography as="h1" variant="display">{t("quickReferenceTitle")}</Typography>
          <Typography as="p" variant="body" className="quick-reference-intro__copy">
            {t("quickReferenceCopy", { questions: data.source_question_count, groups: data.group_count })}
          </Typography>
        </div>
      </header>

      <div className="quick-reference-sections">
        {data.sections.map((section, index) => (
          <QuickReferenceSection
            key={section.id}
            section={section}
            rank={index + 1}
            language={language}
            expanded={expandedSections.has(section.id)}
            onToggle={() => toggleSection(section.id)}
          />
        ))}
      </div>
    </main>
  );
}

function QuickReferenceMessage({ text }: { text: string }) {
  return <main className="page message-page"><Typography variant="body">{text}</Typography></main>;
}
