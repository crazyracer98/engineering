// Thin DOM glue for the quizzes; the logic lives in quiz-core.js.
import { score, draw, loadProgress, saveProgress } from "./quiz-core.js";

function getStorage() {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function el(tag, attrs = {}, text) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

// Same markup as the static contract. Only feedback_html is trusted HTML.
function renderQuestion(q) {
  const form = el("form", { class: "quiz-q", "data-qid": q.id });
  const fs = el("fieldset");
  fs.append(el("legend", {}, q.stem));
  q.options.forEach((o, i) => {
    const input = el("input", { type: "checkbox", name: q.id, value: String(i) });
    if (o.correct) input.setAttribute("data-correct", "1");
    const label = el("label");
    label.append(input, document.createTextNode(" " + o.text));
    const fb = el("p", { class: "quiz-fb", "data-for": String(i) });
    fb.hidden = true;
    fb.innerHTML = o.feedback_html;
    fs.append(label, fb);
  });
  form.append(fs, el("button", { type: "submit" }, "Check"));
  form.append(el("p", { class: "quiz-result", "aria-live": "polite" }));
  const details = el("details", { class: "quiz-answer" });
  details.append(el("summary", {}, "Show answer"));
  const ul = el("ul");
  q.options.forEach((o) => {
    if (o.correct) ul.append(el("li", {}, o.text));
  });
  details.append(ul);
  form.append(details);
  return form;
}

function markOption(label, state) {
  // Text marker, not colour alone.
  let mark = label.querySelector(".quiz-mark");
  if (!mark) {
    mark = el("span", { class: "quiz-mark" });
    label.append(mark);
  }
  mark.textContent = state === "right" ? " (correct answer)" : state === "wrong" ? " (incorrect choice)" : "";
  label.classList.toggle("quiz-opt-right", state === "right");
  label.classList.toggle("quiz-opt-wrong", state === "wrong");
}

function clearQuestion(form) {
  form.classList.remove("quiz-right", "quiz-wrong");
  form.querySelectorAll("input[type=checkbox]").forEach((i) => {
    i.checked = false;
    markOption(i.closest("label"), "");
  });
  form.querySelectorAll(".quiz-fb").forEach((p) => (p.hidden = true));
  const r = form.querySelector(".quiz-result");
  if (r) r.textContent = "";
}

function setResult(form, ok, text) {
  form.classList.toggle("quiz-right", ok === true);
  form.classList.toggle("quiz-wrong", ok === false);
  const r = form.querySelector(".quiz-result");
  if (r) r.textContent = text;
  return r;
}

function initQuiz(root, storage) {
  const name = root.dataset.quiz || "quiz";
  const mixed = name === "mixed";
  let scoreEl = root.querySelector(".quiz-score");
  let resetBtn = root.querySelector(".quiz-reset");
  if (!scoreEl) {
    scoreEl = el("p", { class: "quiz-score", "aria-live": "polite" });
    root.append(scoreEl);
  }
  if (!resetBtn) {
    resetBtn = el("button", { class: "quiz-reset", type: "button" }, "Reset");
    root.append(resetBtn);
  }
  // Remember only what this page has run: progress storage is global per quiz.
  let progress = storage ? loadProgress(storage, name) : { answered: {} };
  if (!progress || !progress.answered) progress = { answered: {} };

  const forms = () => Array.from(root.querySelectorAll("form.quiz-q"));

  function updateScore() {
    const fs = forms();
    const done = fs.filter((f) => f.dataset.qid in progress.answered);
    const right = done.filter((f) => progress.answered[f.dataset.qid]).length;
    scoreEl.textContent = done.length
      ? `Score: ${right} of ${done.length} answered correctly (${fs.length} questions).`
      : "";
  }

  function restore() {
    for (const f of forms()) {
      const qid = f.dataset.qid;
      if (qid in progress.answered) {
        const ok = progress.answered[qid];
        setResult(f, ok, ok ? "Answered correctly earlier." : "Answered incorrectly earlier.");
      }
    }
    updateScore();
  }

  function bind(form) {
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const inputs = Array.from(form.querySelectorAll("input[type=checkbox]"));
      const selected = inputs.filter((i) => i.checked).map((i) => Number(i.value));
      const correct = inputs.filter((i) => i.hasAttribute("data-correct")).map((i) => Number(i.value));
      const ok = score(selected, correct);
      form.querySelectorAll(".quiz-fb").forEach((p) => (p.hidden = false));
      for (const i of inputs) {
        const isCorrect = i.hasAttribute("data-correct");
        markOption(i.closest("label"), isCorrect ? "right" : i.checked ? "wrong" : "");
      }
      const r = setResult(form, ok, ok ? "Correct." : "Not quite. Feedback for each option is shown below.");
      progress.answered[form.dataset.qid] = ok;
      if (storage) saveProgress(storage, name, progress);
      updateScore();
      if (r) {
        r.setAttribute("tabindex", "-1");
        r.focus({ preventScroll: false });
      }
    });
  }

  let run = 0; // sequence token: only the latest build() may touch the page
  async function build() {
    const mine = ++run;
    root.querySelectorAll(".quiz-error").forEach((e) => e.remove());
    if (!mixed) {
      forms().forEach(bind);
      restore();
      return;
    }
    const url = new URL(root.dataset.bank, document.baseURI);
    let bank;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(String(res.status));
      bank = await res.json();
    } catch {
      if (mine !== run) return;
      root.prepend(el("p", { class: "quiz-error", role: "alert" }, "The question bank could not be loaded."));
      return;
    }
    if (mine !== run) return;
    root.querySelectorAll("form.quiz-q").forEach((f) => f.remove());
    const n = Number(root.dataset.draw) || 10;
    for (const q of draw(bank, n, Math.random)) {
      const f = renderQuestion(q);
      bind(f);
      root.insertBefore(f, scoreEl);
    }
    restore();
  }

  resetBtn.addEventListener("click", () => {
    progress = { answered: {} };
    if (storage) saveProgress(storage, name, progress);
    if (mixed) {
      root.querySelectorAll("form.quiz-q").forEach((f) => f.remove());
      build().then(() => {
        const first = root.querySelector("form.quiz-q input");
        if (first) first.focus();
      });
    } else {
      forms().forEach(clearQuestion);
      updateScore();
      const first = root.querySelector("form.quiz-q input");
      if (first) first.focus();
    }
  });

  return build();
}

function initAll() {
  const storage = getStorage();
  document.querySelectorAll(".quiz").forEach((root) => {
    if (root.dataset.quizReady) return;
    root.dataset.quizReady = "1";
    initQuiz(root, storage);
  });
}

// Material instant navigation re-renders the page without a reload and
// exposes `document$`; otherwise run once the DOM is ready.
if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
  document$.subscribe(initAll);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAll);
} else {
  initAll();
}
