import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../src/i18n/LanguageContext";
import { HomePage } from "../src/pages/HomePage";

describe("homepage exam results", () => {
  it("presents the quick reference separately from the mock exam grid", () => {
    const html = renderToStaticMarkup(
      <LanguageProvider>
        <MemoryRouter>
          <HomePage />
        </MemoryRouter>
      </LanguageProvider>,
    );

    expect(html).toContain("全部考点速记表");
    expect(html).not.toContain("408题 · 高频优先");
    expect(html).toContain("正式考试：每套 24 题 · 45 分钟 · 答对 18 题通过");
    expect(html).toContain('class="home-reference-section"');
    expect(html).toContain('class="home-reference-card"');
    expect(html).toContain('href="/quick-reference"');
    expect(html).toContain("随机模拟考");
    expect(html).toContain("从17套题中随机抽取24题");
    expect(html).toContain('href="/random-exam"');
    expect(html).toContain("模拟考试");
    expect((html.match(/<a class="exam-card(?: |")/g) ?? [])).toHaveLength(17);
  });

  it("shows completed exams as passed or failed with a non-colour status", () => {
    const html = renderToStaticMarkup(
      <LanguageProvider>
        <MemoryRouter>
          <HomePage examResults={{
            2: { score: 18, passed: true, answers: {} },
            3: { score: 17, passed: false, answers: {} },
          }} />
        </MemoryRouter>
      </LanguageProvider>,
    );

    expect(html).toContain("exam-card--passed");
    expect(html).toContain("通过 · 18 / 24");
    expect(html).toContain("exam-card--failed");
    expect(html).toContain("未通过 · 17 / 24");
  });
});
