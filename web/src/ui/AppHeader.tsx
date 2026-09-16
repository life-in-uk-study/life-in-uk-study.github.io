import { NavLink } from "react-router-dom";
import { ROUTES } from "../config/exam";
import { useLanguage } from "../i18n/LanguageContext";
import type { TranslationKey } from "../i18n/translations";
import { Typography } from "./Typography";

const NAV_ITEMS = [
  { labelKey: "home", to: ROUTES.home },
] as const satisfies ReadonlyArray<{ labelKey: TranslationKey; to: string }>;

export function AppHeader() {
  const { language, setLanguage, t } = useLanguage();
  return (
    <header className="app-header">
      <NavLink className="brand-link" to={ROUTES.home} aria-label={t("brandHomeLabel")}>
        <Typography as="span" variant="brand">{t("brand")}</Typography>
      </NavLink>
      <div className="header-actions">
        <nav className="primary-nav" aria-label={t("mainNavigation")}>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} className={({ isActive }) => `nav-link${isActive ? " nav-link--active" : ""}`} to={item.to}>
              <Typography as="span" variant="label">{t(item.labelKey)}</Typography>
            </NavLink>
          ))}
        </nav>
        <div className="language-switch" role="group" aria-label="Language / 语言" data-language={language}>
          <button type="button" className={language === "zh" ? "is-active" : ""} aria-pressed={language === "zh"} onClick={() => setLanguage("zh")}>中文</button>
          <button type="button" className={language === "en" ? "is-active" : ""} aria-pressed={language === "en"} onClick={() => setLanguage("en")}>EN</button>
        </div>
      </div>
    </header>
  );
}
