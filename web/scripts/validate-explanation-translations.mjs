import { readFile } from "node:fs/promises";

const examNumbers = Array.from({ length: 17 }, (_, index) => index + 1);
const banks = await Promise.all(
  examNumbers.map(async (examNumber) => {
    const filename = `exam-${String(examNumber).padStart(2, "0")}.json`;
    const bank = JSON.parse(
      await readFile(new URL(`../public/data/exams/${filename}`, import.meta.url), "utf8"),
    );
    const translations = JSON.parse(
      await readFile(new URL(`../../data/explanations_zh/${filename}`, import.meta.url), "utf8"),
    );
    return { bank, translations };
  }),
);

const questions = banks.flatMap(({ bank }) => bank.questions);
const missing = questions.filter((question) => !question.learning.why_correct_zh?.trim());
const nonChinese = questions.filter(
  (question) => !/[\u3400-\u9fff]/u.test(question.learning.why_correct_zh ?? ""),
);
const outOfSync = banks.flatMap(({ bank, translations }) =>
  bank.questions.filter(
    (question) => translations[question.id] !== question.learning.why_correct_zh,
  ),
);

if (missing.length || nonChinese.length || outOfSync.length) {
  console.error(
    JSON.stringify(
      {
        missing: missing.map((question) => question.id),
        nonChinese: nonChinese.map((question) => question.id),
        outOfSync: outOfSync.map((question) => question.id),
      },
      null,
      2,
    ),
  );
  process.exitCode = 1;
} else {
  console.log("PASS: 17 split exams contain 408 synchronized Chinese explanations");
}
