import assert from "node:assert/strict";
import { test } from "node:test";
import { formatAttemptDate } from "../src/labels.ts";

test("attempt dates are converted from UTC to the local timezone", () => {
  const previous = process.env.TZ;
  try {
    process.env.TZ = "Europe/Moscow";
    assert.match(formatAttemptDate("2026-09-28T12:30:00Z"), /15:30/);
    assert.equal(
      formatAttemptDate("2026-09-28T12:30:00Z"),
      formatAttemptDate("2026-09-28T15:30:00+03:00"),
    );
    process.env.TZ = "UTC";
    assert.match(formatAttemptDate("2026-09-28T12:30:00Z"), /12:30/);
  } finally {
    if (previous === undefined) delete process.env.TZ;
    else process.env.TZ = previous;
  }
});
