import { test } from "node:test";
import assert from "node:assert/strict";
import { score, draw, loadProgress, saveProgress, progressKey } from "../../site-assets/quiz-core.js";

// Deterministic LCG in [0, 1).
function seeded(seed) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 2 ** 32;
  };
}

function memStorage() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => void m.set(k, String(v)),
  };
}

test("score: exact set match, order-insensitive", () => {
  assert.equal(score([0, 2], [2, 0]), true);
  assert.equal(score([0], [0, 2]), false);
  assert.equal(score([0, 1, 2], [0, 2]), false);
  assert.equal(score([1], [0]), false);
  assert.equal(score([], []), true);
  assert.equal(score([], [0]), false);
});

test("draw: n distinct items, no mutation, deterministic with a seed", () => {
  const bank = Array.from({ length: 20 }, (_, i) => ({ id: i }));
  const copy = bank.slice();
  const a = draw(bank, 7, seeded(42));
  const b = draw(bank, 7, seeded(42));
  assert.deepEqual(a, b);
  assert.equal(a.length, 7);
  assert.equal(new Set(a.map((x) => x.id)).size, 7);
  assert.deepEqual(bank, copy);
  assert.notDeepEqual(a, draw(bank, 7, seeded(43)));
});

test("draw: n above the bank size returns the whole bank shuffled", () => {
  const bank = [1, 2, 3, 4, 5];
  const out = draw(bank, 99, seeded(1));
  assert.deepEqual([...out].sort(), bank);
  assert.equal(draw(bank, 0, seeded(1)).length, 0);
  assert.deepEqual(draw([], 3, seeded(1)), []);
});

test("draw: survives an rng that returns values at the edges", () => {
  const bank = [1, 2, 3];
  assert.equal(draw(bank, 3, () => 0).length, 3);
  assert.equal(new Set(draw(bank, 3, () => 0.9999999)).size, 3);
});

test("progress round-trips under the versioned key", () => {
  const st = memStorage();
  assert.deepEqual(loadProgress(st, "a"), { answered: {} });
  assert.equal(saveProgress(st, "a", { answered: { "q-a-01": true, "q-a-02": false } }), true);
  assert.equal(progressKey("a"), "engineering-quiz:v1:a");
  assert.ok(st.getItem("engineering-quiz:v1:a"));
  assert.deepEqual(loadProgress(st, "a"), { answered: { "q-a-01": true, "q-a-02": false } });
  assert.deepEqual(loadProgress(st, "b"), { answered: {} });
});

test("storage functions never throw", () => {
  const dflt = { answered: {} };
  assert.deepEqual(loadProgress(null, "a"), dflt);
  assert.deepEqual(loadProgress(undefined, "a"), dflt);
  assert.equal(saveProgress(null, "a", dflt), false);
  const throwing = {
    getItem() {
      throw new Error("denied");
    },
    setItem() {
      throw new Error("quota");
    },
  };
  assert.deepEqual(loadProgress(throwing, "a"), dflt);
  assert.equal(saveProgress(throwing, "a", dflt), false);
  for (const raw of ["{not json", "null", "42", '"s"', "[]", '{"answered":[]}', '{"answered":null}']) {
    assert.deepEqual(loadProgress({ getItem: () => raw }, "a"), dflt, raw);
  }
  assert.deepEqual(loadProgress({ getItem: () => '{"answered":{"q":true,"r":"x"}}' }, "a"), {
    answered: { q: true },
  });
});
