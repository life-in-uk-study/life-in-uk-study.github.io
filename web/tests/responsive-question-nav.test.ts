import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const componentStyles = readFileSync(new URL("../src/design/components.css", import.meta.url), "utf8");
const pageStyles = readFileSync(new URL("../src/design/pages.css", import.meta.url), "utf8");

describe("responsive question navigation", () => {
  it("caps question-number circles instead of stretching them across the available width", () => {
    expect(componentStyles).toContain("--question-nav-item-size: minmax(2rem, 3rem)");
    expect(componentStyles).toContain("grid-template-columns: repeat(var(--question-nav-column-count), var(--question-nav-item-size))");
  });

  it("uses eight compact columns on phones and six on very narrow screens", () => {
    expect(pageStyles).toContain("--question-nav-column-count: 8");
    expect(pageStyles).toContain("--question-nav-item-size: 2.5rem");
    expect(pageStyles).toMatch(/@media \(max-width: 380px\)[\s\S]*--question-nav-column-count: 6/);
  });
});
