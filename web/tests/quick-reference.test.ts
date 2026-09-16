import { afterEach, describe, expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { loadQuickReference } from "../src/services/quickReference";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("quick reference loading", () => {
  it("loads the precomputed summary without fetching all exam files", async () => {
    const payload = { dataset: "test", source_question_count: 408, group_count: 300, sections: [] };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => payload });
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadQuickReference()).resolves.toMatchObject({ source_question_count: 408 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith("/data/quick-reference.json");
  });

  it("uses the eight short title-one categories", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );

    expect(data.source_question_count).toBe(408);
    expect(data.sections.map((section: { title_zh: string }) => section.title_zh).sort()).toEqual(
      ["地理", "历史", "政治", "法律与生活", "宗教与节日", "文化与发明", "体育与休闲", "公民责任"].sort(),
    );
  });

  it("labels and chronologically orders every named history subsection", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const firstRows = new Map<string, { topic_period_sort?: number; topic_period_zh?: string }>();

    history.rows.forEach((row: { topic_id?: string; topic_period_sort?: number; topic_period_zh?: string }) => {
      if (row.topic_id && !firstRows.has(row.topic_id)) firstRows.set(row.topic_id, row);
    });

    const periods = [...firstRows.values()].map((row) => row.topic_period_sort as number);
    expect(firstRows.size).toBeGreaterThan(0);
    expect([...firstRows.values()].every((row) => Boolean(row.topic_period_zh))).toBe(true);
    expect(periods).toEqual([...periods].sort((a, b) => a - b));
  });

  it("merges the two first-coins questions into one canonical row", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const firstCoinsRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-06-q02", "exam-11-q21"].includes(id)),
    );

    expect(firstCoinsRows).toHaveLength(1);
    expect(firstCoinsRows[0]).toMatchObject({
      prompts: ["Who made the first coins to be minted in Britain?"],
      answers: ["The people of the Iron Age"],
      question_ids: expect.arrayContaining(["exam-06-q02", "exam-11-q21"]),
    });
  });

  it("merges the reversible Boudicca and Romans questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const boudiccaRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-04-q08", "exam-13-q03", "exam-14-q24"].includes(id)),
    );

    expect(boudiccaRows).toHaveLength(1);
    expect(boudiccaRows[0]).toMatchObject({
      prompts: ["Who was the tribal leader who fought against the Romans?"],
      answers: ["Boudicca"],
      question_ids: expect.arrayContaining(["exam-04-q08", "exam-13-q03", "exam-14-q24"]),
      topic_id: "roman-era",
    });
  });

  it("groups Hadrian's Wall and Boudicca under Roman Britain", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const romanQuestionIds = ["exam-02-q10", "exam-10-q22", "exam-15-q15", "exam-04-q08", "exam-13-q03", "exam-14-q24"];
    const romanRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => romanQuestionIds.includes(id)),
    );

    expect(romanRows).toHaveLength(4);
    expect(romanRows.every((row: { topic_id?: string }) => row.topic_id === "roman-era")).toBe(true);
  });

  it("merges the two Alfred and Vikings questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const alfredRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-02-q11", "exam-13-q07"].includes(id)),
    );

    expect(alfredRows).toHaveLength(1);
    expect(alfredRows[0]).toMatchObject({
      prompts: ["Under which king did the Anglo-Saxon kingdoms in England unite to defeat the Vikings?"],
      answers: ["King Alfred the Great"],
      question_ids: expect.arrayContaining(["exam-02-q11", "exam-13-q07"]),
      topic_id: "early-medieval-era",
    });
  });

  it("merges the two Mary, Queen of Scots execution questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const maryRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-08-q06", "exam-16-q03"].includes(id)),
    );

    expect(maryRows).toHaveLength(1);
    expect(maryRows[0]).toMatchObject({
      prompts: ["What happened to Mary, Queen of Scots, after 20 years in prison?"],
      answers: ["She was executed"],
      question_ids: expect.arrayContaining(["exam-08-q06", "exam-16-q03"]),
    });
  });

  it("merges the reversible Shakespeare birthplace questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const culture = data.sections.find((section: { id: string }) => section.id === "culture-inventions");
    const shakespeareRows = culture.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-06-q09", "exam-09-q06"].includes(id)),
    );

    expect(shakespeareRows).toHaveLength(1);
    expect(shakespeareRows[0]).toMatchObject({
      prompts: ["Where was William Shakespeare born?"],
      answers: ["Stratford-upon-Avon"],
      question_ids: expect.arrayContaining(["exam-06-q09", "exam-09-q06"]),
    });
  });

  it("places cross-chapter topics under the subject they actually test", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const sectionByQuestionId = new Map<string, string>();

    data.sections.forEach((section: { id: string; rows: Array<{ question_ids: string[] }> }) => {
      section.rows.forEach((row) => {
        row.question_ids.forEach((questionId) => sectionByQuestionId.set(questionId, section.id));
      });
    });

    expect(sectionByQuestionId.get("exam-15-q08")).toBe("sport-leisure"); // Mary Peters
    expect(sectionByQuestionId.get("exam-06-q09")).toBe("culture-inventions"); // Shakespeare
    expect(sectionByQuestionId.get("exam-08-q21")).toBe("culture-inventions"); // Swinging Sixties
    expect(sectionByQuestionId.get("exam-12-q02")).toBe("government"); // BBC independence
    expect(sectionByQuestionId.get("exam-04-q02")).toBe("geography"); // national flowers
    expect(sectionByQuestionId.get("exam-11-q24")).toBe("law-life"); // alcohol age
  });

  it("aggregates culture questions under concise subject headings", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const culture = data.sections.find((section: { id: string }) => section.id === "culture-inventions");
    const topicIds = [...new Set(culture.rows.map((row: { topic_id: string }) => row.topic_id))];

    expect(topicIds).toEqual([
      "film",
      "visual-art",
      "classical-music",
      "rock-music",
      "poetry",
      "literature",
      "inventions",
      "architecture",
      "science",
      "theatre",
      "food",
      "cultural-festivals",
    ]);
    expect(culture.rows.find((row: { question_ids: string[] }) => row.question_ids.includes("exam-15-q18"))).toMatchObject({
      topic_id: "rock-music",
      topic_zh: "摇滚音乐",
    });
  });

  it("includes the Turner Prize question under visual art", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const culture = data.sections.find((section: { id: string }) => section.id === "culture-inventions");
    const turnerPrize = culture.rows.find((row: { question_ids: string[] }) =>
      row.question_ids.includes("exam-08-q24"),
    );

    expect(turnerPrize).toMatchObject({
      prompts: ["What is the Turner Prize?"],
      answers: ["A contemporary art award"],
      topic_id: "visual-art",
      topic_zh: "美术",
    });
  });

  it("merges the reversible golf and Scotland questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const sport = data.sections.find((section: { id: string }) => section.id === "sport-leisure");
    const golfRows = sport.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-02-q21", "exam-05-q08"].includes(id)),
    );

    expect(golfRows).toHaveLength(1);
    expect(golfRows[0]).toMatchObject({
      prompts: ["Which sport can be traced to 15th-century Scotland?"],
      answers: ["Golf"],
      question_ids: expect.arrayContaining(["exam-02-q21", "exam-05-q08"]),
    });
    expect(golfRows.every((row: { topic_id?: string }) => row.topic_id === "ball-sports")).toBe(true);
  });

  it("aggregates politics questions under six civic-system headings", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const politics = data.sections.find((section: { id: string }) => section.id === "government");
    const topics = [...new Map(
      politics.rows.map((row: { topic_id: string; topic_zh: string }) => [row.topic_id, row.topic_zh]),
    ).entries()];

    expect(topics).toEqual([
      ["constitution-monarch", "宪法与君主"],
      ["parliament-mps", "议会与议员"],
      ["government-pm", "政府与首相"],
      ["elections-media", "选举与媒体"],
      ["central-local-government", "中央与地方"],
      ["international-organisations", "国际组织"],
    ]);
  });

  it("aggregates the remaining non-history sections under concise subject headings", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const expectedTopics: Record<string, string[]> = {
      geography: ["英国概况", "领土与属地", "自然与公园", "地点与名胜", "象征与货币"],
      "religion-holidays": ["守护神", "教会", "基督教节日", "其他宗教节日", "传统节日", "公共假日"],
      "law-life": ["法院与陪审团", "犯罪与保护", "警察投诉", "驾驶规则", "日常规定", "工作与证件"],
      "sport-leisure": ["奥运与田径", "球类运动", "赛马", "划船"],
      "civic-responsibility": ["公民价值与责任", "社区参与", "慈善与环保"],
    };

    Object.entries(expectedTopics).forEach(([sectionId, titles]) => {
      const section = data.sections.find((candidate: { id: string }) => candidate.id === sectionId);
      const actualTitles = [...new Set(
        section.rows.map((row: { topic_zh: string }) => row.topic_zh),
      )];
      expect(actualTitles).toEqual(titles);
    });
  });

  it("aggregates history into ten accurate chronological periods", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const topics = [...new Map(
      history.rows.map((row: { topic_id: string; topic_zh: string; topic_period_zh: string }) => [
        row.topic_id,
        [row.topic_zh, row.topic_period_zh],
      ]),
    ).entries()];

    expect(topics).toEqual([
      ["prehistoric-era", ["史前英国", "公元43年以前"]],
      ["roman-era", ["罗马入侵与统治", "公元前55年-公元410年"]],
      ["early-medieval-era", ["盎格鲁-撒克逊与维京", "410-1066年"]],
      ["medieval-era", ["中世纪", "1066-1485年"]],
      ["tudor-era", ["都铎时期", "1485-1603年"]],
      ["stuart-era", ["斯图亚特与内战", "1603-1714年"]],
      ["hanoverian-era", ["汉诺威时期", "1714-1837年"]],
      ["victorian-empire-era", ["维多利亚与帝国", "1837-1902年"]],
      ["democracy-ww1-era", ["民主改革与一战", "1903-1928年"]],
      ["ww2-era", ["二战前后", "1930-1949年"]],
    ]);
  });

  it("splits the four busiest history periods into consistent title-three groups", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const detailTitlesByPeriod = new Map<string, string[]>();

    history.rows.forEach((row: { topic_id: string; detail_topic_id?: string; detail_topic_zh?: string }) => {
      if (!row.detail_topic_id || !row.detail_topic_zh) return;
      const titles = detailTitlesByPeriod.get(row.topic_id) ?? [];
      if (!titles.includes(row.detail_topic_zh)) titles.push(row.detail_topic_zh);
      detailTitlesByPeriod.set(row.topic_id, titles);
    });

    expect([...detailTitlesByPeriod.keys()]).toEqual([
      "medieval-era",
      "tudor-era",
      "stuart-era",
      "hanoverian-era",
    ]);
    expect(detailTitlesByPeriod.get("medieval-era")).toEqual([
      "诺曼征服与英语",
      "Domesday Book",
      "社会与Magna Carta",
      "中世纪战争",
      "黑死病",
    ]);
    expect(detailTitlesByPeriod.get("tudor-era")).toEqual([
      "Henry VIII与宗教改革",
      "苏格兰女王Mary",
      "新教英国",
      "Elizabeth I与西班牙无敌舰队",
    ]);
  });

  it("merges the reversible Enlightenment name and definition questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const enlightenmentRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-05-q14", "exam-11-q05"].includes(id)),
    );

    expect(enlightenmentRows).toHaveLength(1);
    expect(enlightenmentRows[0]).toMatchObject({
      prompts: ["What is the Enlightenment?"],
      answers: ["A period when new ideas about politics, philosophy and science were developed"],
      question_ids: expect.arrayContaining(["exam-05-q14", "exam-11-q05"]),
    });
  });

  it("merges the Bonnie Prince Charlie and Highlands questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const bonniePrinceRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-03-q06", "exam-13-q10"].includes(id)),
    );

    expect(bonniePrinceRows).toHaveLength(1);
    expect(bonniePrinceRows[0]).toMatchObject({
      prompts: ["Who raised an army with support from clansmen of the Scottish Highlands in 1745?"],
      answers: ["Bonnie Prince Charlie"],
      question_ids: expect.arrayContaining(["exam-03-q06", "exam-13-q10"]),
    });
  });

  it("merges the two steam-power and industrial-development questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const steamPowerRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-09-q17", "exam-14-q23"].includes(id)),
    );

    expect(steamPowerRows).toHaveLength(1);
    expect(steamPowerRows[0]).toMatchObject({
      prompts: ["Which invention drove Britain's industrial development during the Industrial Revolution?"],
      answers: ["Steam power"],
      question_ids: expect.arrayContaining(["exam-09-q17", "exam-14-q23"]),
    });
  });

  it("merges the North American colonies and taxation questions", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const independenceRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-03-q18", "exam-15-q02"].includes(id)),
    );

    expect(independenceRows).toHaveLength(1);
    expect(independenceRows[0]).toMatchObject({
      prompts: ["Which colonies declared independence in 1776 after opposing British taxation without representation?"],
      answers: ["The North American colonies"],
      question_ids: expect.arrayContaining(["exam-03-q18", "exam-15-q02"]),
    });
  });

  it("merges the Emancipation Act date question and statement", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const history = data.sections.find((section: { id: string }) => section.id === "history");
    const emancipationRows = history.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => ["exam-07-q12", "exam-15-q21"].includes(id)),
    );

    expect(emancipationRows).toHaveLength(1);
    expect(emancipationRows[0]).toMatchObject({
      prompts: ["When did the Emancipation Act abolish slavery throughout the British Empire?"],
      answers: ["1833"],
      question_ids: expect.arrayContaining(["exam-07-q12", "exam-15-q21"]),
    });
  });

  it("merges three option-set variants of the core citizenship responsibilities", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const civic = data.sections.find((section: { id: string }) => section.id === "civic-responsibility");
    const questionIds = ["exam-01-q01", "exam-06-q01", "exam-07-q01"];
    const matchingRows = civic.rows.filter((row: { question_ids: string[] }) =>
      row.question_ids.some((id) => questionIds.includes(id)),
    );

    expect(matchingRows).toHaveLength(1);
    expect(matchingRows[0]).toMatchObject({
      prompts: ["What responsibilities will you have as a British citizen or permanent resident?"],
      answers: [
        "Respect and obey the law",
        "Look after yourself and your family",
        "Look after the area in which you live and the environment",
      ],
      question_ids: expect.arrayContaining(questionIds),
    });
  });

  it("keeps title-two headings concise", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const topicRows = data.sections.flatMap((section: { rows: Array<{ topic_id?: string; topic_en?: string; topic_zh?: string }> }) =>
      section.rows.filter((row) => row.topic_id),
    );
    const alfred = topicRows.find((row: { question_ids?: string[] }) => row.question_ids?.includes("exam-02-q11"));

    expect(alfred).toMatchObject({ topic_en: "Anglo-Saxons & Vikings", topic_zh: "盎格鲁-撒克逊与维京" });
    expect(topicRows.every((row: { topic_zh: string }) => row.topic_zh.length <= 14)).toBe(true);
    expect(topicRows.every((row: { topic_en: string }) => row.topic_en.length <= 28)).toBe(true);
  });

  it("uses ASCII punctuation in English prompts and answers", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const rows = data.sections.flatMap((section: { rows: Array<{ prompts: string[]; answers: string[] }> }) => section.rows);
    const englishText = rows.flatMap((row: { prompts: string[]; answers: string[] }) => [...row.prompts, ...row.answers]);

    expect(englishText.every((value: string) => !/[‘’“”–—]/.test(value))).toBe(true);
  });

  it("merges all 28 reviewed duplicate fact groups", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const rows = data.sections.flatMap((section: { rows: Array<{ question_ids: string[] }> }) => section.rows);
    const reviewedGroups = [
      ["exam-06-q18", "exam-17-q08"],
      ["exam-07-q19", "exam-09-q19", "exam-16-q22"],
      ["exam-01-q12", "exam-08-q18"],
      ["exam-10-q16", "exam-11-q11", "exam-13-q21"],
      ["exam-04-q01", "exam-09-q02"],
      ["exam-05-q21", "exam-09-q10"],
      ["exam-03-q20", "exam-11-q22"],
      ["exam-03-q13", "exam-05-q24", "exam-08-q01"],
      ["exam-06-q14", "exam-11-q07"],
      ["exam-09-q12", "exam-11-q16"],
      ["exam-02-q01", "exam-08-q04", "exam-15-q22"],
      ["exam-17-q03", "exam-17-q23"],
      ["exam-02-q13", "exam-04-q05", "exam-08-q08"],
      ["exam-03-q09", "exam-13-q09"],
      ["exam-03-q15", "exam-13-q02"],
      ["exam-01-q24", "exam-07-q23"],
      ["exam-03-q02", "exam-06-q05", "exam-10-q03"],
      ["exam-10-q06", "exam-13-q05"],
      ["exam-05-q09", "exam-12-q13"],
      ["exam-03-q07", "exam-16-q17"],
      ["exam-04-q20", "exam-13-q12"],
      ["exam-02-q21", "exam-05-q08"],
      ["exam-02-q22", "exam-13-q08"],
      ["exam-08-q07", "exam-16-q10"],
      ["exam-09-q05", "exam-12-q19"],
      ["exam-01-q22", "exam-11-q18"],
      ["exam-05-q19", "exam-11-q06"],
      ["exam-01-q01", "exam-06-q01", "exam-07-q01"],
    ];

    expect(data.group_count).toBe(353);
    reviewedGroups.forEach((questionIds) => {
      const matchingRows = rows.filter((row: { question_ids: string[] }) =>
        row.question_ids.some((id) => questionIds.includes(id)),
      );
      expect(matchingRows).toHaveLength(1);
      expect(matchingRows[0].question_ids).toEqual(expect.arrayContaining(questionIds));
    });
  });

  it("places every question under a named title-two topic", () => {
    const data = JSON.parse(
      readFileSync(new URL("../public/data/quick-reference.json", import.meta.url), "utf8"),
    );
    const rows = data.sections.flatMap((section: { rows: Array<{ topic_id?: string; topic_en?: string; topic_zh?: string; question_ids: string[] }> }) => section.rows);
    const questionIds = rows.flatMap((row: { question_ids: string[] }) => row.question_ids);

    expect(rows.every((row: { topic_id?: string; topic_en?: string; topic_zh?: string }) =>
      Boolean(row.topic_id && row.topic_en && row.topic_zh),
    )).toBe(true);
    expect(questionIds).toHaveLength(408);
    expect(new Set(questionIds).size).toBe(408);
  });
});
