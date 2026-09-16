import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { HighlightedQuestion } from "../src/ui/HighlightedQuestion";

describe("HighlightedQuestion", () => {
  it("underlines exact keywords without changing the question text", () => {
    const text = "What are two responsibilities that you will have?";
    const html = renderToStaticMarkup(<HighlightedQuestion text={text} keywords={["two"]} />);
    expect(html).toContain('<span class="question-keyword">two</span>');
    expect(html.replace(/<[^>]+>/g, "")).toBe(text);
  });

  it("renders multiple source spans in question order", () => {
    const text = "When were men and women given the right to vote at the age of 21?";
    const html = renderToStaticMarkup(<HighlightedQuestion text={text} keywords={["age of 21", "men and women"]} />);
    expect(html.indexOf("men and women")).toBeLessThan(html.indexOf("age of 21"));
  });

  it("renders English questions with ASCII punctuation", () => {
    const html = renderToStaticMarkup(
      <HighlightedQuestion text="When is St George’s day – and why is it called ‘St George’s Day’?" keywords={["St George’s"]} />,
    );

    expect(html.replace(/<[^>]+>/g, "")).toBe("When is St George&#x27;s day - and why is it called &#x27;St George&#x27;s Day&#x27;?");
    expect(html).toContain('<span class="question-keyword">St George&#x27;s</span>');
    expect(html).not.toMatch(/[‘’“”–—]/);
  });
});
