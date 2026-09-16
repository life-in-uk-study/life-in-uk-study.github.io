import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/noto-sans-sc";
import "@fontsource-variable/newsreader";
import { App } from "./App";
import { LanguageProvider } from "./i18n/LanguageContext";
import "./design/tokens.css";
import "./design/global.css";
import "./design/components.css";
import "./design/pages.css";

createRoot(document.getElementById("root")!).render(<React.StrictMode><LanguageProvider><App /></LanguageProvider></React.StrictMode>);
