import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../src/i18n/LanguageContext";
import { QuestionNavigator } from "../src/ui/QuestionNavigator";

function renderNavigator(currentIndex: number) {
  return renderToStaticMarkup(
    <LanguageProvider>
      <QuestionNavigator
        total={4}
        currentIndex={currentIndex}
        correctIndexes={new Set([0])}
        incorrectIndexes={new Set([1, 2])}
        onSelect={() => undefined}
      />
    </LanguageProvider>,
  );
}

describe("QuestionNavigator", () => {
  it("shows correct and incorrect answered questions with distinct status classes", () => {
    const html = renderNavigator(3);
    expect(html).toContain('class="question-nav__item is-correct"');
    expect(html).toContain('class="question-nav__item is-incorrect"');
    expect(html).toContain('aria-label="第 2 题，回答错误"');
  });

  it("keeps the current-question class when the current answer is incorrect", () => {
    const html = renderNavigator(2);
    expect(html).toContain('class="question-nav__item is-current is-incorrect"');
    expect(html).toContain('aria-current="step"');
  });

});
