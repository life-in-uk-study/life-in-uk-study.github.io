# 题库电影关联审计

审计范围：17 套 Exam、408 条题目记录。审计日期：2026-08-21。

## 判断标准

- **直接关联**：电影直接重现题目询问的事件。
- **背景关联**：电影讲述相关人物或运动，但不直接给出这道题所问的事实。
- 仅仅处于同一时代或同一国家，不算可靠关联。
- 商业电影不是考试答案的权威来源；网站仍用教材及公共机构资料解释答案。

## 已加入网站的高置信关联

| 题目记录 | 电影 | 关系 | 审计结论 |
| --- | --- | --- | --- |
| `exam-01-q03`、`exam-04-q11`、`exam-09-q07` | *Suffragette* (2015) | 背景 | 电影讲20世纪10年代初的妇女参政运动，不直接重现1928年男女同为21岁取得投票权的法案。 |
| `exam-12-q17` | *Dunkirk* (2017) | 直接 | 电影直接重现1940年敦刻尔克撤退及民用船只参与救援的背景。 |
| `exam-15-q10` | *The Imitation Game* (2014) | 背景 | 电影聚焦图灵的战时代码破译工作；题目问的是他在1930年代提出的理论图灵机。 |

这 5 条记录使用 3 张真实电影海报。海报显示在统一的答案图片区，电影背景说明接在答案解释之后，不再建立单独的“电影联想”板块。影片资料和海报归属信息默认折叠。

海报来自 TMDB 图片服务，仅用于当前非商业学习项目，并按其要求展示 TMDB 标志及声明：This product uses the TMDB API but is not endorsed or certified by TMDB。素材来源、原始地址、条款与下载日期记录在 `data/media_sources.json`。

## 已检查但未加入的弱关联

题库还包含 Churchill、Elizabeth I、Mary Queen of Scots、Shakespeare、Florence Nightingale、William Wilberforce、Battle of Hastings、Spanish Armada、两次世界大战等影视作品常见主题。它们中的多数题目询问的具体事实并非某一部电影的核心事件，或者电影改编会引入戏剧化内容，因此本轮未加入，避免把“同一历史背景”误写成“电影讲过这道题”。

## 主要核对来源

- [Suffragette (2015) — BFI](https://www.bfi.org.uk/film/7a9dc7f9-58d2-57a7-b70e-8b1b81d4566f/suffragette)
- [Dunkirk (2017) — BFI](https://www.bfi.org.uk/film/1ab19d70-c33f-510c-9612-8af2e27fa459/dunkirk)
- [The Imitation Game (2014) — BFI](https://www.bfi.org.uk/film/3186b089-c5f3-5572-b7f7-a119132a34c6/the-imitation-game)
- [TMDB API Terms of Use](https://www.themoviedb.org/api-terms-of-use)
- [TMDB attribution FAQ](https://developer.themoviedb.org/docs/faq)
- [Representation of the People (Equal Franchise) Act 1928 — UK Parliament](https://www.parliament.uk/globalassets/documents/works-of-art/women-in-parliament-catalogue.pdf)
