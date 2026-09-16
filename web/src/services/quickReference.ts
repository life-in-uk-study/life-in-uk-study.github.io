import { publicAssetUrl } from "./publicAsset";

export interface QuickReferenceRow {
  topic_id?: string;
  topic_en?: string;
  topic_zh?: string;
  topic_period_sort?: number;
  topic_period_en?: string;
  topic_period_zh?: string;
  detail_topic_sort?: number;
  detail_topic_id?: string;
  detail_topic_en?: string;
  detail_topic_zh?: string;
  prompts: string[];
  answers: string[];
  frequency: number;
  question_ids: string[];
}

export interface QuickReferenceSection {
  id: string;
  title_en: string;
  title_zh: string;
  question_count: number;
  rows: QuickReferenceRow[];
}

export interface QuickReferenceData {
  dataset: string;
  source_question_count: number;
  group_count: number;
  sections: QuickReferenceSection[];
}

export interface QuickReferenceSubsection {
  id: string;
  title_en: string;
  title_zh: string;
  period_en?: string;
  period_zh?: string;
  rows: QuickReferenceRow[];
}

export interface QuickReferenceDetailGroup {
  id?: string;
  title_en?: string;
  title_zh?: string;
  rows: QuickReferenceRow[];
}

export function countReferencedQuestions(rows: QuickReferenceRow[]): number {
  return rows.reduce((total, row) => total + row.question_ids.length, 0);
}

export function buildQuickReferenceDetailGroups(rows: QuickReferenceRow[]): QuickReferenceDetailGroup[] {
  if (!rows.some((row) => row.detail_topic_id)) return [{ rows }];

  const groups = new Map<string, QuickReferenceDetailGroup>();
  rows.forEach((row) => {
    const id = row.detail_topic_id ?? "other";
    const group = groups.get(id) ?? {
      id,
      title_en: row.detail_topic_en,
      title_zh: row.detail_topic_zh,
      rows: [],
    };
    group.rows.push(row);
    groups.set(id, group);
  });
  return [...groups.values()];
}

export function buildQuickReferenceSubsections(
  section: QuickReferenceSection,
  otherTitleEn: string,
  otherTitleZh: string,
): QuickReferenceSubsection[] {
  const topicSubsections = new Map<string, QuickReferenceSubsection>();
  const otherRows: QuickReferenceRow[] = [];

  section.rows.forEach((row) => {
    if (!row.topic_id || !row.topic_en || !row.topic_zh) {
      otherRows.push(row);
      return;
    }

    const subsection = topicSubsections.get(row.topic_id) ?? {
      id: row.topic_id,
      title_en: row.topic_en,
      title_zh: row.topic_zh,
      period_en: row.topic_period_en,
      period_zh: row.topic_period_zh,
      rows: [],
    };
    subsection.rows.push(row);
    topicSubsections.set(row.topic_id, subsection);
  });

  const subsections = [...topicSubsections.values()];
  if (otherRows.length > 0) {
    const isHistory = section.id === "history";
    subsections.push({
      id: "other-key-points",
      title_en: otherTitleEn,
      title_zh: otherTitleZh,
      period_en: isHistory ? "Across periods" : undefined,
      period_zh: isHistory ? "跨时期" : undefined,
      rows: otherRows,
    });
  }
  return subsections;
}

let cachedRequest: Promise<QuickReferenceData> | null = null;

export function loadQuickReference(): Promise<QuickReferenceData> {
  if (!cachedRequest) {
    cachedRequest = fetch(publicAssetUrl("/data/quick-reference.json")).then((response) => {
      if (!response.ok) throw new Error(`Unable to load quick reference (${response.status})`);
      return response.json() as Promise<QuickReferenceData>;
    });
  }
  return cachedRequest;
}
