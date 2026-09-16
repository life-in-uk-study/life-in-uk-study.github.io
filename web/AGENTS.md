# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

## Approved product direction

- Use the mature “Memory Notebook” visual direction recorded in `design/approved-exam-layout.png`.
- Primary navigation shows only 首页. The homepage links to the exam sets and the answer-only quick-reference page.
- The quick-reference page covers all 408 questions, orders chapters by frequency, and groups matching answers within related chapters. It displays only the test point, correct answer and occurrence count—never the longer explanation or fun facts.
- Quick-reference title-one headings are eight short learner-facing categories: 地理、历史、政治、法律与生活、宗教与节日、文化与发明、体育与休闲、公民责任. Keep detailed people, events, institutions, and rules in title-two subsections.
- Classify quick-reference topics by the fact being tested, not merely by the source handbook chapter: for example, Mary Peters belongs under 体育与休闲, Shakespeare under 文化与发明, and prime-minister questions under 政治.
- Within 文化与发明, aggregate individual people and works under subject headings: 电影、美术、古典音乐、摇滚音乐、诗歌、文学、发明、建筑、科学、戏剧、食物、文化节. Keep each test question on its own table row.
- Within 政治, aggregate detailed topics under six title-two headings: 宪法与君主、议会与议员、政府与首相、选举与媒体、中央与地方、国际组织. Keep each test question on its own table row.
- Aggregate the other non-history quick-reference sections into short subject headings: 地理 uses 英国概况、领土与属地、自然与公园、地点与名胜、象征与货币; 宗教与节日 uses 守护神、教会、基督教节日、其他宗教节日、传统节日、公共假日; 法律与生活 uses 法院与陪审团、犯罪与保护、警察投诉、驾驶规则、日常规定、工作与证件; 体育与休闲 uses 奥运与田径、球类运动、赛马、划船; 公民责任 uses 公民价值与责任、社区参与、慈善与环保.
- Within every quick-reference title-two table, keep rows from the same underlying person, event, institution, work, or rule adjacent. Within that cluster, order the core identity or definition first, then causes/actions, dates, locations, and true/false detail.
- Under the 历史 title-one section, every title-two body heading shows a concise period label and the headings are ordered chronologically from earliest to latest; the cross-period fallback stays last. Keep period labels out of the compact navigation and PDF contents list.
- Quick-reference title-three headings are real nested groups beneath crowded history title-two periods, not restyled title-two headings. Use them for 中世纪、都铎时期、斯图亚特与内战、汉诺威时期, with one consistent compact heading pattern above each table.
- Keep quick-reference title-two and title-three styling quiet and notebook-like: no leading bullet, full-width filled bar or decorative underline. Title three follows the same plain typographic treatment as title two at a smaller scale, with a muted question count aligned opposite it.
- Aggregate 历史 into ten chronological title-two periods: 史前英国、罗马入侵与统治、盎格鲁-撒克逊与维京、中世纪、都铎时期、斯图亚特与内战、汉诺威时期、维多利亚与帝国、民主改革与一战、二战前后. Use qualified date ranges: Roman contact begins in 55 BC while rule begins in AD 43, Hanoverian is 1714-1837, the Victorian-and-Empire study group includes the Boer War through 1902, and the suffrage group continues through equal voting rights in 1928.
- On the quick-reference page, differently worded true/false or yes/no questions that test the same reversible fact may share one canonical row. Keep every original question and stable ID in the exam data, and attach all represented IDs to that row.
- The quick-reference page has no separate chapter index or sidebar. Title-one sections are collapsed by default, and each title-one heading stays pinned below the app header while its content scrolls so the learner can collapse it at any time.
- While a quick-reference chapter is expanded, title-two and title-three headings also remain pinned in a nested stack below title one. Calculate offsets from the rendered header heights so the stack does not overlap when the mobile app header wraps.
- The first version has no wrong-answer book and does not persist exam progress in browser storage or a cloud service. Exam state lives only in memory for the current page session.
- After an exam finishes, keep its latest result in application memory for the current SPA session. On the homepage, the corresponding exam card is solid green for a pass or solid red for a fail and includes a visible translated status with the score; refreshing the site clears these results.
- The homepage hero places a real Union Jack image to the right of the introduction. Exam entries are compact links with no progress, “继续练习”, or “尚未开始” labels.
- On the homepage, present the complete quick-reference entry and the 17 mock exams as two separate sections. The quick-reference entry is one wide study card, while mock exams remain in their own compact grid; the duration note belongs only to the mock-exam section.
- The interface supports Chinese and English. Questions and answer options always remain in their authorized English source text; every other UI string and the answer explanation follows the selected interface language.
- Present the Chinese/English control as a compact pill-shaped segmented switch with an animated selection thumb, equal-width labels and clear pressed/focus states across phone, tablet and desktop widths.
- Chinese answer explanations live in `../data/explanations_zh/exam-XX.json`, keyed by stable question ID, and are merged into `public/data/exams/exam-XX.json` by the enrichment generator. Run `npm run test:translations` after changing the question bank or translations.
- Per-exam English explanations and question-level source mappings live in `../data/learning_overrides/exam-XX.json`; prefer this split source for newly reviewed exams instead of expanding the generator's legacy inline override table.
- Exam runtime data is split into 17 files under `public/data/exams/`. Entering `/exam/N` loads only `exam-NN.json`; the homepage must not fetch question data.
- Authority sources are collapsed by default and expand only after user action. Do not repeat the correct answer as text beneath the answer visual.
- After answer confirmation, render each correct option as a full green block and each selected incorrect option as a full red block. A selected option must retain the filled-dot circle after reveal; an unselected correct option keeps an empty circle. Never place check or cross icons inside the circle. Preserve a non-color status label for screen readers.
- In question navigation, a revealed correct answer is green and a revealed incorrect answer is red. The current-question outline always takes visual precedence, so a current question is never shown as a filled status circle; its correct/incorrect status returns when the user navigates away.
- Keep question-number navigation compact rather than stretching circles to fill the question column: cap desktop circles at 3rem, use eight 2.5rem columns on common phone widths, and fall back to six columns below 381px.
- Desktop exam pages use two columns: question on the left and answer/image/explanation/sources on the right.
- Mock exams are untimed. The left column starts with the exam number, current-question count and 24-question navigation.
- The homepage mock-exam heading states the official format—24 questions, 45 minutes and 18 correct answers to pass—while the practice interface itself remains untimed.
- Mobile stacks the same content in this order: exam status and navigation, question, answer explanation.
- Typography must be centralized. Font families and font-size values may only be declared in `src/design/tokens.css`; product components must consume typography variants or CSS variables.
- Exam question headings use the dedicated `question` typography variant and must remain visibly smaller than homepage and exam-summary display headings.
- Exam question headings use a compact 24–32 px responsive token. Each question must provide one to three exact-source learning keywords; render those words with the shared gold underline treatment without changing the authorized question text.
- Question headings have no fixed decorative underline beneath the whole title. Only the selected learning keywords receive the gold underline treatment.
- Render questions and answer options with English ASCII punctuation: use straight apostrophes/quotation marks and a hyphen instead of typographic curly quotes or long dashes. Preserve semantic symbols such as `£`.
- The answer column has one media slot followed by one explanation area. Do not create a separate film-association card: a relevant film poster occupies the normal media slot and its bilingual context follows the answer explanation.
- Choose factual media by subject: licensed real photographs or documented historical portraits for people, an actual licensed character/mascot image for mascots, and a map for geography. Film connections use real theatrical posters with recorded provider terms and attribution. All media and film sources remain collapsed until requested.
- For historical people who predate photography, use a documented museum portrait and state clearly that it is a historical artwork rather than a photograph; expose the artwork credit and licence in the collapsed sources.
- Keep vertical answer media compact: film posters and historical portraits share the centralized vertical-media height token and must not dominate the explanation column.
- Questions without a licensed real photo, portrait, map, mascot image, or film poster use a question-and-answer-specific AI learning illustration. These images contain no text, appear only after answer submission, and are stored as compressed WebP assets under `public/images/ai/`; exact duplicate questions reuse one canonical image.
- Exam 1 question 5 uses Peter Paul Rubens's `Saint Andrew` from the Museo del Prado. Preserve the Prado/Commons credit and keep the explanation explicit about the distinction between traditional legends and the documented 1320 Declaration of Arbroath.
- Reuse abstract UI elements for typography, buttons, options, status, and question navigation. Do not place raw font-family or literal font-size values in business components.
- Keep repository content free of personal identifiers, local absolute paths, credentials and temporary screenshots. Personal publishing drafts must remain local and git-ignored.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.
