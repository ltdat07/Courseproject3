import assert from "node:assert/strict";
import { test } from "node:test";
import { hasAiDraftChanges, prepareAiPracticeChange } from "../src/aiPracticeSelection.ts";

const practices = [
  { id: "first", starter_code: "// one" },
  { id: "second", starter_code: "// two" },
  { id: "third", starter_code: "// three" },
];

test("untouched starter code needs no discard warning", () => {
  assert.equal(hasAiDraftChanges(null, practices[0]), false);
  assert.equal(hasAiDraftChanges({
    practiceId: "first", studentSolution: "// one", feedback: null,
  }, practices[0]), false);
});

test("edits, an emptied editor and an existing review require a warning", () => {
  for (const studentSolution of ["return 42;", "", "// one "]) {
    assert.equal(hasAiDraftChanges({
      practiceId: "first", studentSolution, feedback: null,
    }, practices[0]), true);
  }
  assert.equal(hasAiDraftChanges({
    practiceId: "first", studentSolution: "// one", feedback: { summary: "review" },
  }, practices[0]), true);
});

test("cancelled replacement preserves the draft and review", () => {
  const draft = { practiceId: "first", studentSolution: "return 42;", feedback: { summary: "review" } };
  const before = structuredClone(draft);
  let confirmations = 0;
  const next = prepareAiPracticeChange(practices[1], draft, practices[0], () => {
    confirmations++;
    return false;
  });
  assert.equal(confirmations, 1);
  assert.equal(next, null);
  assert.deepEqual(draft, before);
});

test("confirmed replacement selects new starter code without the previous review", () => {
  const draft = { practiceId: "first", studentSolution: "return 42;", feedback: { summary: "review" } };
  assert.deepEqual(prepareAiPracticeChange(practices[1], draft, practices[0], () => true), {
    practiceId: "second", studentSolution: "// two", feedback: null,
  });
  assert.equal(prepareAiPracticeChange(practices[0], draft, practices[0], () => {
    assert.fail("The current practice must not prompt or reset the draft");
  }), null);
});
