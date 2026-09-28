import assert from "node:assert/strict";
import { beforeEach, afterEach, test } from "node:test";
import { loadAiDraft as readDraft, restoreAiDraft, saveAiDraft as writeDraft } from "../src/aiDraft.ts";
const loadAiDraft = () => readDraft(1);
const saveAiDraft = (draft) => writeDraft(draft, 1);

const key = "csharp-trainer:ai-draft:v1:user:1";
const values = new Map();
const previousWindow = Object.getOwnPropertyDescriptor(globalThis, "window");
beforeEach(() => {
  values.clear();
  Object.defineProperty(globalThis, "window", {
    configurable: true, value: { localStorage: {
      getItem: (name) => values.get(name) ?? null,
      setItem: (name, value) => values.set(name, value),
      removeItem: (name) => values.delete(name),
    }},
  });
});
afterEach(() => {
  if (previousWindow) Object.defineProperty(globalThis, "window", previousWindow);
  else delete globalThis.window;
});

const feedback = {
  verdict: "partially_correct", summary: "Нужен дробный операнд.",
  strengths: ["Есть return"], issues: ["Целочисленное деление"],
  hints: ["Используй double"], suggested_fragment: "(double)a / b", model: "test",
};
const draft = { practiceId: "second", studentSolution: "return a / b;", feedback };
const practices = [
  { id: "first", starter_code: "// первое задание" },
  { id: "second", starter_code: "// второе задание" },
];

test("restores the selected task, code and review after a fresh read", () => {
  assert.equal(saveAiDraft(draft), true);
  assert.deepEqual(restoreAiDraft(practices, loadAiDraft()), draft);
});
test("starts with the first task when no draft exists", () => {
  assert.equal(loadAiDraft(), null);
  assert.deepEqual(restoreAiDraft(practices, null), {
    practiceId: "first", studentSolution: "// первое задание", feedback: null,
  });
});
test("keeps an intentionally empty editor instead of replacing it with starter code", () => {
  const empty = { ...draft, studentSolution: "", feedback: null };
  saveAiDraft(empty);
  assert.deepEqual(restoreAiDraft(practices, loadAiDraft()), empty);
});
test("an edited solution does not restore the previous review", () => {
  saveAiDraft(draft);
  const edited = { ...draft, studentSolution: "return (double)a / b;", feedback: null };
  saveAiDraft(edited);
  assert.deepEqual(loadAiDraft(), edited);
});
test("switching tasks replaces only the single saved draft", () => {
  values.set("unrelated", "keep");
  saveAiDraft(draft);
  const next = restoreAiDraft(practices, null);
  saveAiDraft(next);
  assert.deepEqual(loadAiDraft(), next);
  assert.equal(values.get("unrelated"), "keep");
});
test("a removed task falls back to the current first task without its old review", () => {
  assert.deepEqual(
    restoreAiDraft(practices, { ...draft, practiceId: "removed" }),
    restoreAiDraft(practices, null),
  );
  assert.equal(restoreAiDraft([], draft), null);
});
test("ignores malformed JSON, unsupported versions and invalid drafts", () => {
  const invalid = [
    "{", "null", "[]", JSON.stringify({ ...draft, version: 2 }),
    JSON.stringify({ ...draft, version: 1, practiceId: 123 }),
    JSON.stringify({ ...draft, version: 1, studentSolution: "a".repeat(8001) }),
    JSON.stringify({ ...draft, version: 1, studentSolution: null }),
    " ".repeat(64001),
  ];
  for (const raw of invalid) {
    values.set(key, raw);
    assert.equal(loadAiDraft(), null);
  }
});
test("discards an invalid review but preserves the code", () => {
  for (const invalid of [
    { ...feedback, verdict: "unknown" }, { ...feedback, issues: "not an array" },
    { ...feedback, hints: [42] }, { ...feedback, summary: {} },
    { ...feedback, suggested_fragment: [] }, { ...feedback, model: null },
  ]) {
    values.set(key, JSON.stringify({ version: 1, ...draft, feedback: invalid }));
    assert.deepEqual(loadAiDraft(), { ...draft, feedback: null });
  }
});
test("stores no cloud consent, credentials, connection status or pending request", () => {
  saveAiDraft({
    ...draft, cloudReviewConsent: true, apiKey: "test-only",
    isAnalyzingSolution: true, aiStatus: { available: true },
  });
  assert.deepEqual(JSON.parse(values.get(key)), { version: 1, ...draft });
});
test("unavailable browser storage does not throw", () => {
  Object.defineProperty(window, "localStorage", {
    get() { throw new Error("Storage blocked"); },
  });
  assert.equal(loadAiDraft(), null);
  assert.equal(saveAiDraft(draft), false);
});
test("a full storage reports failure without crashing", () => {
  window.localStorage.setItem = () => { throw new Error("Quota exceeded"); };
  assert.equal(saveAiDraft(draft), false);
});
test("rendering without a browser does not throw", () => {
  delete globalThis.window;
  assert.equal(loadAiDraft(), null);
  assert.equal(saveAiDraft(draft), false);
});

test("accounts keep separate drafts and only the former owner reads the legacy draft", () => {
  values.set("csharp-trainer:ai-draft:v1", JSON.stringify({ version: 1, ...draft }));
  assert.equal(readDraft(2), null);
  assert.deepEqual(readDraft(1), draft);
  assert.equal(writeDraft(draft, 1), true);
  assert.equal(values.has("csharp-trainer:ai-draft:v1"), false);
  const second = { ...draft, studentSolution: "// another account", feedback: null };
  writeDraft(second, 2);
  assert.deepEqual(readDraft(1), draft);
  assert.deepEqual(readDraft(2), second);
});
