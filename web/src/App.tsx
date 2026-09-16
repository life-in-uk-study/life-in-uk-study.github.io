import { useCallback, useState } from "react";
import { BrowserRouter, HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { ExamPage } from "./pages/ExamPage";
import { HomePage } from "./pages/HomePage";
import { QuickReferencePage } from "./pages/QuickReferencePage";
import { RandomExamPage } from "./pages/RandomExamPage";
import type { ExamResult } from "./services/exam";
import { AppHeader } from "./ui/AppHeader";

const AppRouter = import.meta.env.VITE_ROUTER_MODE === "hash" ? HashRouter : BrowserRouter;

export function App() {
  const [examResults, setExamResults] = useState<Partial<Record<number, ExamResult>>>({});
  const recordExamResult = useCallback((examNumber: number, result: ExamResult) => {
    setExamResults((current) => ({ ...current, [examNumber]: result }));
  }, []);
  const resetExamResult = useCallback((examNumber: number) => {
    setExamResults((current) => {
      if (!current[examNumber]) return current;
      const next = { ...current };
      delete next[examNumber];
      return next;
    });
  }, []);

  return (
    <AppRouter>
      <div className="app-shell">
        <AppHeader />
        <Routes>
          <Route path="/" element={<HomePage examResults={examResults} />} />
          <Route path="/quick-reference" element={<QuickReferencePage />} />
          <Route path="/random-exam" element={<RandomExamPage />} />
          <Route path="/exam" element={<Navigate to="/exam/1" replace />} />
          <Route
            path="/exam/:examNumber"
            element={(
              <ExamPage
                examResults={examResults}
                onExamCompleted={recordExamResult}
                onExamReset={resetExamResult}
              />
            )}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </AppRouter>
  );
}
