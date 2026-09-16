import { ArrowCounterClockwise, ArrowLeft, ArrowRight, BookOpenText, WarningCircle } from "@phosphor-icons/react";
import { useCallback, useEffect, useMemo } from "react";
import { Navigate, useParams } from "react-router-dom";
import { EXAM_CONFIG } from "../config/exam";
import { useExamSession } from "../hooks/useExamSession";
import { useQuestionBank } from "../hooks/useQuestionBank";
import { useLanguage } from "../i18n/LanguageContext";
import { answersMatch, createExamResult, createReviewNavigation, scoreExam, type ExamResult } from "../services/exam";
import { normalizeEnglishPunctuation } from "../services/englishPunctuation";
import type { Question, QuestionBank } from "../types/questions";
import { AnswerExplanation } from "../ui/AnswerExplanation";
import { AnswerOption } from "../ui/AnswerOption";
import { Button } from "../ui/Button";
import { ExamSummary } from "../ui/ExamSummary";
import { ExamStatusBar } from "../ui/ExamStatusBar";
import { HighlightedQuestion } from "../ui/HighlightedQuestion";
import { MessagePage } from "../ui/MessagePage";
import { QuestionNavigator } from "../ui/QuestionNavigator";
import { Typography } from "../ui/Typography";

interface ExamPageProps {
  examResults: Partial<Record<number, ExamResult>>;
  onExamCompleted: (examNumber: number, result: ExamResult) => void;
  onExamReset: (examNumber: number) => void;
}

export function ExamPage({ examResults, onExamCompleted, onExamReset }: ExamPageProps) {
  const { t } = useLanguage();
  const { examNumber: examParam } = useParams();
  const examNumber = Number(examParam);
  const handleExamCompleted = useCallback(
    (result: ExamResult) => onExamCompleted(examNumber, result),
    [examNumber, onExamCompleted],
  );
  const handleExamReset = useCallback(
    () => onExamReset(examNumber),
    [examNumber, onExamReset],
  );
  const validExamNumber = Number.isInteger(examNumber) && examNumber >= 1 && examNumber <= EXAM_CONFIG.examCount;
  const { bank, error } = useQuestionBank(validExamNumber ? examNumber : null);
  if (!validExamNumber) return <Navigate to="/" replace />;
  if (error) return <MessagePage icon={<WarningCircle />} title={t("questionBankError")} />;
  if (!bank) return <MessagePage title={t("loadingQuestions")} />;
  return <LoadedExam bank={bank} sessionId={examNumber} statusTitle={`Exam ${examNumber}`} questions={bank.questions} completedResult={examResults[examNumber]} onExamCompleted={handleExamCompleted} onExamReset={handleExamReset} />;
}

interface LoadedExamProps {
  bank: QuestionBank;
  sessionId: number;
  statusTitle: string;
  questions: Question[];
  completedResult?: ExamResult;
  restartLabel?: string;
  onExamCompleted?: (result: ExamResult) => void;
  onExamReset?: () => void;
  onQuestionSetReset?: () => void;
}

export function LoadedExam({ bank, sessionId, statusTitle, questions, completedResult, restartLabel, onExamCompleted, onExamReset, onQuestionSetReset }: LoadedExamProps) {
  const { t } = useLanguage();
  const reviewNavigation = useMemo(
    () => completedResult && !completedResult.passed
      ? createReviewNavigation(questions, completedResult.answers)
      : null,
    [completedResult, questions],
  );
  const exam = useExamSession(sessionId, questions);
  const isComplete = exam.session.completedAt !== null;
  const isReviewMode = !isComplete && Boolean(completedResult && !completedResult.passed);
  const activeIndex = exam.session.currentIndex;
  const currentQuestion = questions[activeIndex];
  const selectedAnswers = isReviewMode ? completedResult?.answers : exam.session.answers;
  const selected = currentQuestion ? selectedAnswers?.[currentQuestion.id] ?? [] : [];
  const isRevealed = isReviewMode || (currentQuestion ? exam.revealedSet.has(currentQuestion.id) : false);
  const finalScore = useMemo(() => isComplete ? scoreExam(questions, exam.session.answers) : null, [exam.session.answers, isComplete, questions]);
  useEffect(() => {
    if (finalScore === null) return;
    onExamCompleted?.(createExamResult(finalScore, exam.session.answers));
  }, [exam.session.answers, finalScore, onExamCompleted]);
  useEffect(() => {
    if (!isReviewMode || !reviewNavigation) return;
    exam.goToQuestion(reviewNavigation.firstIncorrectIndex);
  }, [exam.goToQuestion, isReviewMode, reviewNavigation]);
  const { correctIndexes, incorrectIndexes } = useMemo(() => {
    if (isReviewMode && reviewNavigation) return reviewNavigation;
    const correct = new Set<number>();
    const incorrect = new Set<number>();
    questions.forEach((question, index) => {
      if (!exam.session.revealedQuestionIds.includes(question.id)) return;
      const destination = answersMatch(exam.session.answers[question.id] ?? [], question.correct_option_ids) ? correct : incorrect;
      destination.add(index);
    });
    return { correctIndexes: correct, incorrectIndexes: incorrect };
  }, [exam.session.answers, exam.session.revealedQuestionIds, isReviewMode, questions, reviewNavigation]);
  const sources = currentQuestion?.authoritative_source_ids.map((sourceId) => bank.authority_sources[sourceId]).filter(Boolean) ?? [];

  const restartExam = () => {
    onExamReset?.();
    if (onQuestionSetReset) {
      onQuestionSetReset();
      return;
    }
    exam.resetExam();
  };

  const goNext = () => {
    if (!currentQuestion) return;
    if (!isRevealed) return exam.revealAnswer(currentQuestion);
    if (activeIndex === questions.length - 1) {
      if (!isReviewMode) exam.completeExam();
      return;
    }
    exam.goToQuestion(activeIndex + 1);
  };

  if (!currentQuestion) return <MessagePage title={t("questionBankError")} />;

  return (
    <main className="exam-page">
      <section className="exam-column exam-column--question" aria-label={t("examQuestionRegion")}>
        <ExamStatusBar title={statusTitle} current={activeIndex + 1} total={questions.length} />
        {isReviewMode ? (
          <div className="review-toolbar">
            <div>
              <Typography as="p" variant="heading">{t("reviewIncorrectAnswers")}</Typography>
              <Typography as="p" variant="utility">{t("reviewIncorrectCount", { count: incorrectIndexes.size })}</Typography>
            </div>
            <Button tone="secondary" onClick={restartExam}><ArrowCounterClockwise aria-hidden="true" />{restartLabel ?? t("restartExam")}</Button>
          </div>
        ) : null}
        <QuestionNavigator total={questions.length} currentIndex={activeIndex} correctIndexes={correctIndexes} incorrectIndexes={incorrectIndexes} onSelect={exam.goToQuestion} />
        {isComplete ? <ExamSummary score={finalScore ?? 0} onRestart={restartExam} restartLabel={restartLabel} /> : (
          <>
            <div className="question-heading">
              <Typography as="p" variant="label" className="eyebrow">{currentQuestion.type === "multiple" ? t("chooseMultiple", { count: currentQuestion.correct_option_ids.length }) : t("chooseOne")}</Typography>
              <Typography as="h1" variant="question"><HighlightedQuestion text={currentQuestion.question} keywords={currentQuestion.learning.keywords} /></Typography>
            </div>
            <fieldset className="answer-list" aria-label={t("answerOptions")}>
              <legend className="visually-hidden">{normalizeEnglishPunctuation(currentQuestion.question)}</legend>
              {currentQuestion.options.map((option) => {
                const checked = selected.includes(option.id);
                const isCorrectOption = currentQuestion.correct_option_ids.includes(option.id);
                const state = isRevealed ? isCorrectOption ? "correct" : checked ? "wrong" : "idle" : "idle";
                const stateLabel = state === "correct" ? t("correctOption") : state === "wrong" ? t("incorrectOption") : undefined;
                return <AnswerOption key={option.id} id={option.id} text={option.text} checked={checked} disabled={isRevealed} multiple={currentQuestion.type === "multiple"} state={state} stateLabel={stateLabel} onChange={() => exam.selectOption(currentQuestion, option.id)} />;
              })}
            </fieldset>
            <div className="question-actions">
              <Button tone="secondary" onClick={() => exam.goToQuestion(activeIndex - 1)} disabled={activeIndex === 0}><ArrowLeft aria-hidden="true" /> {t("previous")}</Button>
              <Button onClick={goNext} disabled={(isReviewMode && activeIndex === questions.length - 1) || (!isRevealed && selected.length === 0)}>
                {isReviewMode ? t("next") : isRevealed ? activeIndex === questions.length - 1 ? t("complete") : t("next") : t("confirm")}<ArrowRight aria-hidden="true" />
              </Button>
            </div>
          </>
        )}
      </section>
      <aside className="exam-column exam-column--answer" aria-live="polite">
        {isRevealed ? <AnswerExplanation question={currentQuestion} selected={selected} sources={sources} /> : (
          <div className="answer-placeholder"><BookOpenText aria-hidden="true" /><Typography as="h2" variant="title">{t("answerPlaceholderTitle")}</Typography><Typography as="p" variant="body">{t("answerPlaceholderBody")}</Typography></div>
        )}
      </aside>
    </main>
  );
}
