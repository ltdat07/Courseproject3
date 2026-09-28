import type { AiPractice } from "./types";
import type { AiDraft } from "./aiDraft";

export function hasAiDraftChanges(draft: AiDraft | null, practice: AiPractice | null): boolean {
  if (!draft) return false;
  return draft.feedback !== null || draft.studentSolution !== (practice?.starter_code ?? "");
}

export function prepareAiPracticeChange(
  next: AiPractice,
  draft: AiDraft | null,
  current: AiPractice | null,
  confirmDiscard: () => boolean,
): AiDraft | null {
  if (next.id === draft?.practiceId) return null;
  if (hasAiDraftChanges(draft, current) && !confirmDiscard()) return null;
  return { practiceId: next.id, studentSolution: next.starter_code, feedback: null };
}
