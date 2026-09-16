# Life in the UK 学习网站

面向中文母语学习者的双语 Life in the UK Test 练习网站，包含17套模拟练习、答题后解析、配图、权威来源和答案速记表。

## 项目边界

- 本项目不是英国政府或官方考试机构的网站，也不保证覆盖真实考试或保证通过。
- 授权题干和选项保持英文原文；中文内容用于学习解释。
- 题库来源、授权范围和覆盖限制见 [EXAM_SOURCE_AND_COVERAGE.md](EXAM_SOURCE_AND_COVERAGE.md)。
- 图片与外部资料的来源记录见数据文件及相关审计文档。

## 隐私与安全

- 纯静态前端，不含账户、数据库、分析 SDK 或广告追踪。
- 不使用 Cookie、`localStorage` 或 `sessionStorage` 保存个人资料、答案或错题。
- 答题状态和最近一次考试结果只保留在当前页面内存中，刷新后清除。
- HTML入口配置了内容安全策略和 Referrer Policy；支持自定义响应头的平台还会启用禁止嵌入及浏览器权限限制。GitHub Pages不应用仓库中的自定义响应头文件。
- 发现安全问题时，请优先使用 GitHub 的 Private vulnerability reporting，避免在公开 Issue 中披露敏感细节。

## 本地开发

```bash
cd web
npm ci
npm run dev
```

## 发布前验证

```bash
cd web
npm run typecheck
npm test
npm run test:translations
npm run build
npm run test:sites
npm audit

cd ..
python3 scripts/validate_question_data.py
python3 scripts/validate_enriched_content.py
git diff --check
```

## 发布到 GitHub Pages

仓库包含 `.github/workflows/deploy-pages.yml`。它会在代码推送到 `main` 后完成测试、按实际 Pages路径构建网站，并自动发布。GitHub Pages版本使用 Hash路由，因此刷新考试页不会出现 SPA 404。

首次发布需要在 GitHub仓库中打开：

1. `Settings` → `Pages`。
2. 在 `Build and deployment` 中将 `Source` 设为 `GitHub Actions`。
3. 将代码推送到 `main`，然后在 `Actions` 页面查看部署结果。

项目同时支持 `https://用户名.github.io/仓库名/`、用户主页仓库和自定义域名，不需要手工填写仓库名。

## 许可证

仓库目前没有开放源代码许可证。公开仓库允许他人查看代码，但不会自动授予复制、修改或再发布代码及内容的权利。正式开放协作前，请由项目所有者为代码和已授权内容分别确认合适的许可证。
