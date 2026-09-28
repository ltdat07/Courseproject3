import type { AiFeedback, AiPractice } from "./types";

const STORAGE_KEY = "csharp-trainer:ai-draft:v1";

export type AiDraft = {
  practiceId: string;
  studentSolution: string;
  feedback: AiFeedback | null;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isFeedback(value: unknown): value is AiFeedback {
  return isRecord(value)
    && typeof value.verdict === "string"
    && ["correct", "partially_correct", "needs_revision"].includes(value.verdict)
    && typeof value.summary === "string"
    && typeof value.model === "string"
    && [value.strengths, value.issues, value.hints].every(
      (items) => Array.isArray(items) && items.every((item) => typeof item === "string"),
    )
    && (value.suggested_fragment == null || typeof value.suggested_fragment === "string");
}

export function loadAiDraft(userId: number): AiDraft | null {
  try {
    const raw = window.localStorage.getItem(`${STORAGE_KEY}:user:${userId}`)
      ?? (userId === 1 ? window.localStorage.getItem(STORAGE_KEY) : null);
    if (!raw || raw.length > 64_000) return null;
    const value: unknown = JSON.parse(raw);
    if (!isRecord(value) || value.version !== 1
      || typeof value.practiceId !== "string" || !value.practiceId
      || typeof value.studentSolution !== "string" || value.studentSolution.length > 8000) {
      return null;
    }
    return {
      practiceId: value.practiceId,
      studentSolution: value.studentSolution,
      feedback: isFeedback(value.feedback) ? value.feedback : null,
    };
  } catch {
    // Повреждённые данные или запрет хранилища не должны ломать тренажёр.
    return null;
  }
}

export function saveAiDraft(draft: AiDraft, userId: number): boolean {
  try {
    window.localStorage.setItem(`${STORAGE_KEY}:user:${userId}`, JSON.stringify({
      version: 1,
      practiceId: draft.practiceId,
      studentSolution: draft.studentSolution,
      feedback: draft.feedback,
    }));
    // Старый общий черновик относится только к первому профилю.
    if (userId === 1) window.localStorage.removeItem(STORAGE_KEY);
    return true;
  } catch {
    return false;
  }
}

export function restoreAiDraft(practices: AiPractice[], saved: AiDraft | null): AiDraft | null {
  if (saved && practices.some((practice) => practice.id === saved.practiceId)) return saved;
  const first = practices[0];
  return first ? { practiceId: first.id, studentSolution: first.starter_code, feedback: null } : null;
}
