import assert from "node:assert/strict";
import { afterEach, beforeEach, test } from "node:test";
import { apiFetch } from "../src/api.ts";

const originalFetch = globalThis.fetch;
const originalWindow = Object.getOwnPropertyDescriptor(globalThis, "window");
let calls;
let events;
let status;

beforeEach(() => {
  calls = [];
  events = [];
  status = 200;
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options });
    return new Response("{}", { status });
  };
  Object.defineProperty(globalThis, "window", {
    configurable: true, value: { dispatchEvent: (event) => events.push(event.type) },
  });
});
afterEach(() => {
  globalThis.fetch = originalFetch;
  if (originalWindow) Object.defineProperty(globalThis, "window", originalWindow);
  else delete globalThis.window;
});

test("writes carry CSRF and expected-account headers with same-origin cookies", async () => {
  await apiFetch("/api/topics/tasks/1/check", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: "{}",
  }, 7);
  const { options } = calls[0];
  assert.equal(options.headers.get("X-Trainer-Request"), "1");
  assert.equal(options.headers.get("X-Trainer-User"), "7");
  assert.equal(options.headers.get("Content-Type"), "application/json");
  assert.equal(options.credentials, "same-origin");
  assert.equal(options.cache, "no-store");
  assert.ok(options.signal instanceof AbortSignal);
});

test("reads keep account identity and do not override the longer AI timeout", async () => {
  const signal = new AbortController().signal;
  await apiFetch("/api/ai-feedback/status", { signal }, 4);
  assert.equal(calls[0].options.headers.get("X-Trainer-User"), "4");
  assert.equal(calls[0].options.headers.has("X-Trainer-Request"), false);
  assert.equal(calls[0].options.signal, signal);
});

test("expired sessions return to login but incorrect passwords stay in the login form", async () => {
  status = 401;
  assert.equal((await apiFetch("/api/users/me")).status, 401);
  assert.deepEqual(events, ["trainer:unauthorized"]);
  events.length = 0;
  await apiFetch("/api/auth/login", { method: "POST" });
  assert.deepEqual(events, []);
});
