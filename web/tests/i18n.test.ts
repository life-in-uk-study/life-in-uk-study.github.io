import { describe, expect, it } from "vitest";
import { translate } from "../src/i18n/translations";

describe("interface translations", () => {
  it("switches interface copy between Chinese and English", () => {
    expect(translate("zh", "home")).toBe("首页");
    expect(translate("en", "home")).toBe("Home");
    expect(translate("zh", "heroTitle")).toBe("Life in the UK 考试准备");
    expect(translate("en", "heroTitle")).toBe("Life in the UK Test preparation");
    expect(translate("zh", "heroCopy")).not.toContain("45");
    expect(translate("en", "heroCopy")).not.toContain("45");
  });

  it("interpolates question counts without changing question content", () => {
    expect(translate("zh", "chooseMultiple", { count: 2 })).toBe("请选择 2 项");
    expect(translate("en", "chooseMultiple", { count: 2 })).toBe("Choose 2 answers");
  });
});
