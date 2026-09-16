export const EXAM_CONFIG = {
  examCount: 17,
  questionsPerExam: 24,
  officialDurationMinutes: 45,
  passingScore: 18,
} as const;

export const ROUTES = {
  home: "/",
  mockExam: "/exam/1",
  quickReference: "/quick-reference",
} as const;
