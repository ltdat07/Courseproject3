import "./helpers/typescript.mjs";
import assert from "node:assert/strict";
import { afterEach, beforeEach, test } from "node:test";
import { act, createElement } from "react";
import { createRoot } from "react-dom/client";
import { JSDOM } from "jsdom";
const { default: useCourse } = await import("../src/hooks/useCourse.ts");
const { default: LessonView } = await import("../src/components/LessonView.tsx");
const { default: TopicCatalog } = await import("../src/components/TopicCatalog.tsx");

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((ok, fail) => { resolve = ok; reject = fail; });
  return { promise, resolve, reject };
}

const topics = [1, 9].map((id, index) => ({
  id, title: `Topic ${id}`, quest_title: `Chapter ${id}`, description: "", level: index + 1, points: 20,
  theory: "Theory", achievement: null,
}));
const tasks = (id) => [0, 1].map((index) => ({
  id: id * 10 + index, topic_id: id, story: "Story", question: `Question ${id}.${index}`,
  type: "single_choice", options: [{ id: 1, text: "First" }, { id: 2, text: "Second" }],
}));
const result = {
  is_correct: true, message: "Correct", explanation: "Explanation", earned_points: 10,
  total_xp: 10, topic_completed: false, achievement_unlocked: null, unlocked_topic_id: null,
};
const json = (data) => new Response(JSON.stringify(data), { headers: { "Content-Type": "application/json" } });
let dom;
let root;
let course;
let pendingAnswer;
let pendingTopics;
let pendingTasks;
let pendingProgress;
let submitted;
let originalGlobals;

function request(url, options) {
  if (options?.method === "POST") {
    submitted.push(JSON.parse(options.body));
    return pendingAnswer.promise;
  }
  if (url === "/api/topics/") return Promise.resolve(json(topics));
  if (url === "/api/users/me/progress") return pendingProgress?.promise ?? Promise.resolve(json({
    total_xp: 0, unlocked_topic_ids: [1, 9], completed_topic_ids: [], achievements: [],
  }));
  const match = url.match(/^\/api\/topics\/(\d+)(\/tasks)?$/);
  assert.ok(match, `Unexpected URL: ${url}`);
  const id = Number(match[1]);
  if (match[2]) return pendingTasks.get(id)?.promise ?? Promise.resolve(json(tasks(id)));
  return pendingTopics.get(id)?.promise ?? Promise.resolve(json(topics.find((topic) => topic.id === id)));
}

function Harness() {
  course = useCourse(request);
  return course.selectedTopic ? createElement(LessonView, course) : createElement(TopicCatalog, course);
}

beforeEach(async () => {
  originalGlobals = Object.fromEntries(["window", "document", "IS_REACT_ACT_ENVIRONMENT"]
    .map((name) => [name, Object.getOwnPropertyDescriptor(globalThis, name)]));
  dom = new JSDOM("<!doctype html><div id='root'></div>", { url: "http://localhost" });
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  pendingAnswer = deferred();
  pendingTopics = new Map();
  pendingTasks = new Map();
  pendingProgress = null;
  submitted = [];
  root = createRoot(document.getElementById("root"));
  await act(async () => root.render(createElement(Harness)));
});

afterEach(async () => {
  await act(async () => root.unmount());
  dom.window.close();
  for (const [name, descriptor] of Object.entries(originalGlobals)) {
    if (descriptor) Object.defineProperty(globalThis, name, descriptor);
    else delete globalThis[name];
  }
});

async function startAnswer() {
  await act(async () => course.openTopic(1));
  await act(async () => course.setSelectedOptionId(1));
  let pending;
  await act(async () => { pending = course.checkAnswer(10); });
  return { pending };
}

test("a delayed answer updates XP without replacing the result of another chapter", async () => {
  const { pending } = await startAnswer();
  await act(async () => course.goBackToTopics());
  await act(async () => course.openTopic(9));
  await act(async () => {
    pendingAnswer.resolve(json({
      ...result, topic_completed: true, achievement_unlocked: "Chapter complete", unlocked_topic_id: 2,
    }));
    await pending;
  });
  assert.equal(course.selectedTopic.id, 9);
  assert.equal(course.answerResult, null);
  assert.equal(course.totalXp, 10);
  assert.deepEqual(course.completedTopicIds, [1]);
  assert.deepEqual(course.achievements, ["Chapter complete"]);
  assert.ok(course.unlockedTopicIds.includes(2));
  assert.equal(course.isCheckingAnswer, false);
  assert.equal(document.querySelector(".result"), null);
});

test("reopening the same chapter does not restore an old answer", async () => {
  const { pending } = await startAnswer();
  await act(async () => course.goBackToTopics());
  await act(async () => course.openTopic(1));
  await act(async () => { pendingAnswer.resolve(json(result)); await pending; });
  assert.equal(course.answerResult, null);
});

test("answer options stay fixed while a request is pending", async () => {
  const { pending } = await startAnswer();
  const buttons = [...document.querySelectorAll(".option")];
  assert.ok(buttons.every((button) => button.disabled));
  await act(async () => { buttons[1].click(); course.setSelectedOptionId(2); });
  assert.equal(course.selectedOptionId, 1);
  assert.deepEqual(submitted, [{ selected_option_id: 1 }]);
  await act(async () => { pendingAnswer.resolve(json(result)); await pending; });
});

test("two clicks before rendering send only one answer", async () => {
  await act(async () => course.openTopic(1));
  await act(async () => course.setSelectedOptionId(1));
  let responses;
  await act(async () => { responses = [course.checkAnswer(10), course.checkAnswer(10)]; });
  assert.equal(submitted.length, 1);
  await act(async () => { pendingAnswer.resolve(json(result)); await Promise.all(responses); });
});

test("the last selected chapter wins when loading responses arrive out of order", async () => {
  const first = deferred();
  pendingTopics.set(1, first);
  let opening;
  await act(async () => { opening = course.openTopic(1); });
  await act(async () => course.openTopic(9));
  await act(async () => { first.resolve(json(topics[0])); await opening; });
  assert.equal(course.selectedTopic.id, 9);
  assert.equal(course.currentTask.topic_id, 9);
});

test("leaving a loading chapter prevents it from opening later", async () => {
  const first = deferred();
  pendingTopics.set(1, first);
  let opening;
  await act(async () => { opening = course.openTopic(1); });
  await act(async () => course.goBackToTopics());
  assert.equal(course.loadingTopicId, null);
  await act(async () => { first.resolve(json(topics[0])); await opening; });
  assert.equal(course.selectedTopic, null);
  assert.equal(course.loadingTopicId, null);
});

test("chapter loading stays visible until both theory and tasks arrive", async () => {
  const theory = deferred();
  const practice = deferred();
  pendingTopics.set(1, theory);
  pendingTasks.set(1, practice);
  let opening;
  await act(async () => { opening = course.openTopic(1); });
  assert.equal(course.loadingTopicId, 1);
  assert.match(document.querySelector('[role="status"]').textContent, /Загрузка главы/);
  assert.equal(document.querySelector('.topic-card[aria-busy="true"]').getAttribute("aria-disabled"), "true");
  await act(async () => theory.resolve(json(topics[0])));
  assert.equal(course.loadingTopicId, 1);
  assert.equal(course.selectedTopic, null);
  await act(async () => { practice.resolve(json(tasks(1))); await opening; });
  assert.equal(course.loadingTopicId, null);
  assert.equal(course.selectedTopic.id, 1);
  assert.equal(document.querySelector('[role="status"]'), null);
});

test("finishing an older chapter request does not clear the current loading indicator", async () => {
  const first = deferred();
  const second = deferred();
  pendingTopics.set(1, first);
  pendingTopics.set(9, second);
  let openingFirst;
  let openingSecond;
  await act(async () => { openingFirst = course.openTopic(1); });
  await act(async () => { openingSecond = course.openTopic(9); });
  await act(async () => { first.reject(new Error("offline")); await openingFirst; });
  assert.equal(course.loadingTopicId, 9);
  assert.equal(course.courseError, null);
  assert.ok(document.querySelector('[role="status"]'));
  await act(async () => { second.resolve(json(topics[1])); await openingSecond; });
  assert.equal(course.loadingTopicId, null);
  assert.equal(course.selectedTopic.id, 9);
});

test("a chapter load failure clears loading and allows retrying", async () => {
  const practice = deferred();
  pendingTasks.set(1, practice);
  let opening;
  await act(async () => { opening = course.openTopic(1); });
  await act(async () => { practice.reject(new Error("offline")); await opening; });
  assert.equal(course.loadingTopicId, null);
  assert.equal(course.selectedTopic, null);
  assert.ok(course.courseError);
  assert.equal(document.querySelector('[role="status"]'), null);
  assert.equal(document.querySelector(".topic-card").getAttribute("aria-disabled"), "false");
  pendingTasks.delete(1);
  await act(async () => course.openTopic(1));
  assert.equal(course.selectedTopic.id, 1);
  assert.equal(course.courseError, null);
});

test("clicking or pressing Enter on a loading chapter does not restart its request", async () => {
  const theory = deferred();
  pendingTopics.set(1, theory);
  let opening;
  await act(async () => { opening = course.openTopic(1); });
  const card = document.querySelector(".topic-card");
  let repeated = 0;
  pendingTopics.set(1, { get promise() { repeated += 1; return theory.promise; } });
  await act(async () => {
    card.click();
    card.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
  });
  assert.equal(repeated, 0);
  await act(async () => { theory.resolve(json(topics[0])); await opening; });
  assert.equal(course.selectedTopic.id, 1);
});

test("failed answers allow retrying and do not show errors in another chapter", async () => {
  const { pending } = await startAnswer();
  await act(async () => { pendingAnswer.reject(new Error("offline")); await pending; });
  assert.equal(course.isCheckingAnswer, false);
  assert.ok(course.courseError);
  assert.ok([...document.querySelectorAll(".option")].every((button) => !button.disabled));
  pendingAnswer = deferred();
  let retry;
  await act(async () => { retry = course.checkAnswer(10); });
  await act(async () => course.openTopic(9));
  await act(async () => { pendingAnswer.reject(new Error("offline")); await retry; });
  assert.equal(course.courseError, null);
  assert.equal(course.isCheckingAnswer, false);
});

test("a correct answer advances to the next task and clears its selection", async () => {
  const { pending } = await startAnswer();
  await act(async () => { pendingAnswer.resolve(json(result)); await pending; });
  assert.equal(course.answerResult.is_correct, true);
  await act(async () => course.goToNextTask());
  assert.equal(course.currentTask.id, 11);
  assert.equal(course.answerResult, null);
  assert.equal(course.selectedOptionId, null);
});

test("a late initial progress response does not erase a newly earned reward", async () => {
  pendingProgress = deferred();
  await act(async () => root.render(createElement(Harness, { key: "late-progress" })));
  const { pending } = await startAnswer();
  await act(async () => {
    pendingAnswer.resolve(json({
      ...result, topic_completed: true, achievement_unlocked: "Chapter complete", unlocked_topic_id: 9,
    }));
    await pending;
  });
  await act(async () => pendingProgress.resolve(json({
    total_xp: 0, unlocked_topic_ids: [1], completed_topic_ids: [], achievements: [],
  })));
  assert.equal(course.totalXp, 10);
  assert.deepEqual(course.completedTopicIds, [1]);
  assert.deepEqual(course.achievements, ["Chapter complete"]);
  assert.ok(course.unlockedTopicIds.includes(9));
});
