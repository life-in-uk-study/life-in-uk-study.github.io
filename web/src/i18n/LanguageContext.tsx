import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { translate, type Language, type TranslationKey } from "./translations";

interface LanguageContextValue {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: TranslationKey, values?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>("zh");

  useEffect(() => {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en-GB";
  }, [language]);

  const t = useCallback((key: TranslationKey, values: Record<string, string | number> = {}) => {
    return translate(language, key, values);
  }, [language]);

  const value = useMemo(() => ({ language, setLanguage, t }), [language, t]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used inside LanguageProvider");
  return context;
}
