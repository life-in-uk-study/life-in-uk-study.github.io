import { CaretDown } from "@phosphor-icons/react";
import { useState } from "react";
import { useLanguage } from "../i18n/LanguageContext";
import { normalizeEnglishPunctuation } from "../services/englishPunctuation";
import { answersMatch } from "../services/exam";
import { publicAssetUrl } from "../services/publicAsset";
import type { AuthoritySource, Question } from "../types/questions";
import { QuestionVisual } from "./QuestionVisual";
import { Typography } from "./Typography";

interface AnswerExplanationProps {
  question: Question;
  selected: string[];
  sources: AuthoritySource[];
}

export function AnswerExplanation({ question, selected, sources }: AnswerExplanationProps) {
  const { language, t } = useLanguage();
  const explanation = language === "zh"
    ? question.learning.why_correct_zh
    : normalizeEnglishPunctuation(question.learning.why_correct_en);

  return (
    <article className="answer-explanation">
      <header className="answer-explanation__heading">
        <Typography as="p" variant="label" className="eyebrow">
          {answersMatch(selected, question.correct_option_ids) ? t("correct") : t("incorrect")}
        </Typography>
        <Typography as="h2" variant="title">{t("whyAnswer")}</Typography>
      </header>
      <QuestionVisual question={question} language={language} />
      <section className="answer-copy">
        {explanation.split(/\n\n+/).map((paragraph) => (
          <Typography key={paragraph} as="p" variant="body">{paragraph}</Typography>
        ))}
        {question.film_connection ? (
          <Typography as="p" variant="body">
            {language === "zh"
              ? question.film_connection.fun_fact_zh
              : normalizeEnglishPunctuation(question.film_connection.fun_fact_en)}
          </Typography>
        ) : null}
      </section>
      <SourceDisclosure key={question.id} sources={sources} film={question.film_connection} />
    </article>
  );
}

function SourceDisclosure({ sources, film }: {
  sources: AuthoritySource[];
  film: Question["film_connection"];
}) {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useLanguage();
  return (
    <section className="source-disclosure">
      <button type="button" className="source-disclosure__toggle" aria-expanded={isOpen} onClick={() => setIsOpen((current) => !current)}>
        <Typography as="span" variant="label">{isOpen ? t("hideSources") : t("showSources")}</Typography>
        <CaretDown aria-hidden="true" className={isOpen ? "is-open" : ""} />
      </button>
      {isOpen ? (
        <div className="source-list">
          <Typography as="h3" variant="label">{t("authoritySources")}</Typography>
          {sources.map((source) => (
            <a key={source.url} className="source-link" href={source.url} target="_blank" rel="noreferrer">
              <Typography as="span" variant="body">{source.title}</Typography>
              <Typography as="span" variant="utility">{source.publisher}</Typography>
            </a>
          ))}
          {film ? <FilmSources film={film} /> : null}
        </div>
      ) : null}
    </section>
  );
}

function FilmSources({ film }: { film: NonNullable<Question["film_connection"]> }) {
  return (
    <>
      <a className="source-link" href={film.source_url} target="_blank" rel="noreferrer">
        <Typography as="span" variant="body">{film.source_title}</Typography>
        <Typography as="span" variant="utility">BFI</Typography>
      </a>
      <a className="source-link source-link--media" href={film.poster_provider_url} target="_blank" rel="noreferrer">
        <img src={publicAssetUrl("/images/media/tmdb-logo.svg")} alt="TMDB" />
        <Typography as="span" variant="utility">{film.poster_credit_notice}</Typography>
      </a>
    </>
  );
}
