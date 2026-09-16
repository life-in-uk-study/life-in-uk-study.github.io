import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const pageStyles = readFileSync(new URL("../src/design/pages.css", import.meta.url), "utf8");

describe("responsive page layout", () => {
  it("stacks the exam before a 10-inch tablet becomes cramped", () => {
    expect(pageStyles).toMatch(/@media \(max-width: 1100px\)[\s\S]*\.exam-page \{[^}]*grid-template-columns: 1fr/);
  });

  it("keeps the phone header compact on one row", () => {
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*--header-height: 4rem/);
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.app-header \{[^}]*flex-direction: row/);
  });

  it("does not let phone actions cover the final answer option", () => {
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.question-actions \{[^}]*position: static/);
  });

  it("keeps the answer status and heading separated without a fixed decorative rule", () => {
    expect(pageStyles).toMatch(/\.answer-explanation__heading \{[^}]*display: grid[^}]*gap: var\(--space-2\)/);
    expect(pageStyles).not.toMatch(/\.answer-explanation h2::after/);
  });

  it("keeps the quick-reference icon beside its copy on phones", () => {
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.quick-reference-intro \{[^}]*grid-template-columns: auto minmax\(0, 1fr\)/);
  });

  it("compresses the phone homepage above the exam grid", () => {
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.home-intro \{[^}]*width: 100%[^}]*min-height: 20rem/);
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.home-reference-section \{[^}]*margin-top: calc\(-1 \* var\(--space-4\)\)/);
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.home-exams-section \.section-heading \{[^}]*margin-bottom: var\(--space-4\)/);
    expect(pageStyles).toMatch(/@media \(max-width: 640px\)[\s\S]*\.exam-grid \{[^}]*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
  });
});
