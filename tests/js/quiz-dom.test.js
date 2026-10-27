// DOM tests for site-assets/quiz.js (NFR-0002), run in jsdom.
import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";

const CUE = "Select all that apply.";
let loads = 0;

function staticForm(qid) {
  return `<form class="quiz-q" data-qid="${qid}" autocomplete="off">
<fieldset aria-describedby="${qid}-hint"><legend>Stem ${qid}</legend>
<p class="quiz-hint" id="${qid}-hint">${CUE}</p>
<label><input type="checkbox" name="${qid}" value="0" data-correct="1"> Right</label>
<p class="quiz-fb" data-for="0" hidden>fb0</p>
<label><input type="checkbox" name="${qid}" value="1"> Wrong</label>
<p class="quiz-fb" data-for="1" hidden>fb1</p>
</fieldset>
<button type="submit">Check</button>
<p class="quiz-result" aria-live="polite"></p>
<details class="quiz-answer"><summary>Show answer</summary><ul><li>Right</li></ul></details>
</form>`;
}

const CATEGORY_PAGE = `<div class="quiz" data-quiz="a">${staticForm("q-a-01")}${staticForm("q-a-02")}
<p class="quiz-score" aria-live="polite"></p><button type="button" class="quiz-reset">Reset</button></div>`;

const MIXED_PAGE = `<div class="quiz" data-quiz="mixed" data-bank="../../assets/quiz/quiz-bank.json" data-draw="2" data-cue="${CUE}">
<p class="quiz-score" aria-live="polite"></p><button type="button" class="quiz-reset">Reset</button></div>`;

const BANK = [1, 2, 3].map((n) => ({
  id: `q-a-0${n}`,
  category: "a",
  rules: ["P1"],
  stem: `Bank stem ${n}`,
  options: [
    { text: "Right", correct: true, feedback_html: "<em>fb0</em>" },
    { text: "Wrong", correct: false, feedback_html: "fb1" },
  ],
}));

// Load quiz.js into a fresh jsdom page. The module reads the globals at import
// time, so each load installs new ones and imports a distinct module instance.
async function load(body, { storage } = {}) {
  const dom = new JSDOM(`<!doctype html><body>${body}</body>`, {
    url: "https://example.test/quiz/a/",
    pretendToBeVisual: true,
  });
  const { window } = dom;
  if (storage) {
    Object.defineProperty(window, "localStorage", { value: storage, configurable: true });
  }
  await new Promise((resolve) => {
    if (window.document.readyState === "complete") resolve();
    else window.addEventListener("load", resolve);
  });
  globalThis.window = window;
  globalThis.document = window.document;
  globalThis.fetch = async () => ({ ok: true, json: async () => BANK });
  await import(`../../site-assets/quiz.js?load=${++loads}`);
  await new Promise((resolve) => setTimeout(resolve, 0)); // let build() settle
  return window;
}

function recordingStorage() {
  const m = new Map();
  const calls = { get: 0, set: 0 };
  return {
    calls,
    getItem: (k) => (calls.get++, m.has(k) ? m.get(k) : null),
    setItem: (k, v) => (calls.set++, void m.set(k, String(v))),
  };
}

function submit(window, form) {
  form.dispatchEvent(new window.Event("submit", { cancelable: true, bubbles: true }));
}

function tick(form, ...values) {
  for (const v of values) form.querySelector(`input[value="${v}"]`).checked = true;
}

test("build: a category quiz binds its forms and starts with an empty score", async () => {
  const window = await load(CATEGORY_PAGE);
  const forms = window.document.querySelectorAll("form.quiz-q");
  assert.equal(forms.length, 2);
  assert.equal(window.document.querySelector(".quiz-score").textContent, "");
  for (const f of forms) assert.equal(f.getAttribute("autocomplete"), "off");
});

test("init does not uncheck ticks made before the module ran", async () => {
  // Static forms carry autocomplete=off, so the script leaves ticks alone.
  const page = CATEGORY_PAGE.replace('value="1"> Wrong', 'value="1" checked> Wrong');
  const window = await load(page);
  assert.equal(window.document.querySelector('input[value="1"]').checked, true);
});

test("check and score: exact match is correct, otherwise feedback and markers show", async () => {
  const window = await load(CATEGORY_PAGE);
  const [first, second] = window.document.querySelectorAll("form.quiz-q");

  tick(first, 0);
  submit(window, first);
  assert.equal(first.querySelector(".quiz-result").textContent, "Correct.");
  assert.ok(first.classList.contains("quiz-right"));
  assert.ok([...first.querySelectorAll(".quiz-fb")].every((p) => !p.hidden));
  assert.equal(window.document.activeElement, first.querySelector(".quiz-result"));

  tick(second, 0, 1);
  submit(window, second);
  assert.ok(second.classList.contains("quiz-wrong"));
  const marks = [...second.querySelectorAll(".quiz-mark")].map((m) => m.textContent);
  assert.deepEqual(marks, [" (correct answer)", " (incorrect choice)"]);
  assert.equal(
    window.document.querySelector(".quiz-score").textContent,
    "Score: 1 of 2 answered correctly (2 questions).",
  );
});

test("reset clears the page, closes open answers and drops the focus tabindex", async () => {
  const window = await load(CATEGORY_PAGE);
  const form = window.document.querySelector("form.quiz-q");
  tick(form, 0);
  submit(window, form);
  const result = form.querySelector(".quiz-result");
  assert.equal(result.getAttribute("tabindex"), "-1");
  form.querySelector("details.quiz-answer").open = true;

  window.document.querySelector(".quiz-reset").click();

  assert.equal(form.querySelector("details.quiz-answer").open, false);
  assert.equal(result.hasAttribute("tabindex"), false);
  assert.equal(result.textContent, "");
  assert.ok(!form.classList.contains("quiz-right"));
  assert.ok([...form.querySelectorAll("input")].every((i) => !i.checked));
  assert.ok([...form.querySelectorAll(".quiz-fb")].every((p) => p.hidden));
  assert.equal(form.querySelectorAll(".quiz-mark:not(:empty)").length, 0);
  assert.equal(window.document.querySelector(".quiz-score").textContent, "");
  assert.equal(window.document.activeElement, form.querySelector("input"));
});

test("pageshow with persisted clears every form; a normal pageshow does not", async () => {
  const window = await load(CATEGORY_PAGE);
  const form = window.document.querySelector("form.quiz-q");
  tick(form, 0);
  submit(window, form);
  form.querySelector("details.quiz-answer").open = true;

  window.dispatchEvent(new window.PageTransitionEvent("pageshow", { persisted: false }));
  assert.ok(form.classList.contains("quiz-right"));

  window.dispatchEvent(new window.PageTransitionEvent("pageshow", { persisted: true }));
  assert.ok(!form.classList.contains("quiz-right"));
  assert.equal(form.querySelector("details.quiz-answer").open, false);
  assert.equal(form.querySelector(".quiz-result").hasAttribute("tabindex"), false);
  assert.ok([...form.querySelectorAll("input")].every((i) => !i.checked));
  assert.ok([...form.querySelectorAll(".quiz-fb")].every((p) => p.hidden));
});

test("a category quiz stores its score; the score returns on reload, the ticks do not", async () => {
  const storage = recordingStorage();
  const first = await load(CATEGORY_PAGE, { storage });
  const form = first.document.querySelector("form.quiz-q");
  tick(form, 0);
  submit(first, form);
  assert.ok(storage.calls.set > 0);

  const again = await load(CATEGORY_PAGE, { storage });
  assert.equal(
    again.document.querySelector(".quiz-score").textContent,
    "Score: 1 of 1 answered correctly (2 questions).",
  );
  assert.ok([...again.document.querySelectorAll("input")].every((i) => !i.checked));
});

test("mixed quiz: JS-built questions match the static markup and use the data-cue", async () => {
  const window = await load(MIXED_PAGE);
  const forms = [...window.document.querySelectorAll("form.quiz-q")];
  assert.equal(forms.length, 2);
  for (const f of forms) {
    const qid = f.dataset.qid;
    assert.equal(f.getAttribute("autocomplete"), "off");
    const fs = f.querySelector("fieldset");
    assert.equal(fs.getAttribute("aria-describedby"), `${qid}-hint`);
    const hint = f.querySelector(`p.quiz-hint#${qid}-hint`);
    assert.equal(hint.textContent, CUE);
    assert.equal(fs.querySelector("legend").textContent, `Bank stem ${qid.at(-1)}`);
    const boxes = [...f.querySelectorAll("input[type=checkbox]")];
    assert.deepEqual(boxes.map((b) => [b.name, b.value]), [[qid, "0"], [qid, "1"]]);
    assert.deepEqual(boxes.map((b) => b.hasAttribute("data-correct")), [true, false]);
    assert.ok([...f.querySelectorAll(".quiz-fb")].every((p) => p.hidden));
    assert.equal(f.querySelector(".quiz-fb").innerHTML, "<em>fb0</em>");
    assert.ok(f.querySelector("button[type=submit]"));
    assert.equal(f.querySelector(".quiz-result").getAttribute("aria-live"), "polite");
    assert.ok(f.querySelector("details.quiz-answer summary"));
  }
});

test("mixed quiz: stores nothing and reads nothing, even after Check and Reset", async () => {
  const storage = recordingStorage();
  const window = await load(MIXED_PAGE, { storage });
  const form = window.document.querySelector("form.quiz-q");
  tick(form, 0);
  submit(window, form);
  assert.equal(form.querySelector(".quiz-result").textContent, "Correct.");
  window.document.querySelector(".quiz-reset").click();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(window.document.querySelectorAll("form.quiz-q").length, 2);
  assert.deepEqual(storage.calls, { get: 0, set: 0 });
});
