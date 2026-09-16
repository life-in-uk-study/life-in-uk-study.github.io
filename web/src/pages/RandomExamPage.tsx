import { WarningCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { useRandomQuestionBank } from "../hooks/useRandomQuestionBank";
import { useLanguage } from "../i18n/LanguageContext";
import { LoadedExam } from "./ExamPage";
import { MessagePage } from "../ui/MessagePage";

export function RandomExamPage() {
  const { t } = useLanguage();
  const [generation, setGeneration] = useState(0);
  const { bank, error } = useRandomQuestionBank(generation);

  if (error) return <MessagePage icon={<WarningCircle />} title={t("randomMockExamError")} />;
  if (!bank) return <MessagePage title={t("randomMockExamLoading")} />;

  return (
    <LoadedExam
      key={generation}
      bank={bank}
      sessionId={-(generation + 1)}
      statusTitle={t("randomMockExamTitle")}
      questions={bank.questions}
      restartLabel={t("randomMockExamRestart")}
      onQuestionSetReset={() => setGeneration((current) => current + 1)}
    />
  );
}
