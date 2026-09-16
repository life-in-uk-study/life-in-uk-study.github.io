import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AnswerOption } from "../src/ui/AnswerOption";

describe("AnswerOption", () => {
  it("renders English option text with ASCII punctuation", () => {
    const html = renderToStaticMarkup(
      <AnswerOption
        id="answer"
        text="A Midsummer Night’s dream – ‘comedy’"
        checked={false}
        disabled={false}
        multiple={false}
        state="idle"
        onChange={() => undefined}
      />,
    );

    expect(html).toContain("A Midsummer Night&#x27;s dream - &#x27;comedy&#x27;");
    expect(html).not.toMatch(/[‘’“”–—]/);
  });
});
