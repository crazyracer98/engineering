# NFR-0002. Quizzes are operable by keyboard and screen reader and degrade without JavaScript

## Status

Accepted. Implemented in v1.1.0 (2026-10-27); see "Outcome" below.

## Attribute

Usability (accessibility).

## Description

Every quiz on the site meets these constraints:

- Each question is a `<form>` with a `<fieldset>` and a `<legend>` holding
  the stem. Options are native checkboxes inside `<label>`s, so assistive
  technology announces them as a group of checkable choices.
- All of it works from the keyboard alone: Tab and Shift+Tab move between
  options and buttons, Space toggles a checkbox, Enter or Space on "Check"
  submits, and "Reset" is a real `<button>`. After "Check", focus moves to
  the result paragraph; after "Reset", it moves to the first option.
- The per-question result (`.quiz-result`) and the running score
  (`.quiz-score`) are `aria-live="polite"` regions, so a screen reader
  announces them without moving focus away from the question.
- Correct and incorrect states are never conveyed by colour alone. Each
  carries a text marker ("Correct.", "(correct answer)", "(incorrect
  choice)"), a symbol and a different border style or text decoration.
- Without JavaScript the quiz stays usable: the feedback is hidden only
  by the `hidden` attribute that the script removes, and each question has
  a `<details class="quiz-answer">` ("Show answer") that works with no
  script. The mixed quiz, which needs the script to draw questions, shows
  a no-script notice that points to the per-category quizzes.
- If `localStorage` is unavailable or holds corrupt data, the quiz still
  works; it just does not remember progress. The storage functions never
  throw.
- On reload a category quiz restores only its running score
  (`.quiz-score`), counted over the questions on the page; options,
  feedback and per-question status stay cleared. The mixed quiz is a fresh
  random draw each time and never reads or writes storage.
- Every quiz form carries `autocomplete="off"`, so the browser does not
  restore ticks that show no feedback. Restoring a page from the
  back/forward cache clears each question like a fresh load: options,
  feedback, result, the focus `tabindex` on the result and the open
  "Show answer" panel (as "Reset" does).

## Source

The learning hub plan (`../plans/2026-10-learning-hub.md`) and
[ADR 0008](../adrs/0008-learning-hub-in-the-dataset-repo.md), which chose
to build a small quiz engine of our own instead of a third-party plugin.

## Verification

- Automated, on every commit through the `js-tests` prek hook
  (`node --test`, `tests/js/quiz-core.test.js`): the pure core in
  `site-assets/quiz-core.js` (scoring, seeded drawing, progress
  storage that never throws on a null, throwing or corrupt store, the score
  restored from stored progress, and the mixed quiz's no-storage rule).
  The DOM glue in `site-assets/quiz.js` is covered by
  `tests/js/quiz-dom.test.js` in jsdom (build, check and score, "Reset"
  closing answers, bfcache `pageshow` clearing, the JS-built mixed
  questions matching the static markup, and the mixed quiz storing
  nothing). jsdom is a pinned devDependency in `tests/js/package.json`;
  the `js-deps` prek hook installs it from the lockfile
  (`npm ci --prefix tests/js --ignore-scripts`) before `js-tests` runs.
- Manual, at the learning hub's G3 gate and after any change to
  `site-assets/` or the quiz markup: in a real browser, (1) complete a
  quiz with the keyboard only and check the focus order, the focus after
  "Check" and "Reset", and the visible focus ring; (2) turn JavaScript
  off and check that every question still offers "Show answer"; (3) check
  the correct and incorrect states with a greyscale or forced-colours
  view; (4) optionally listen with a screen reader for the result and
  score announcements.

## Outcome

Implemented in v1.1.0. Decisions made while building it:

- **Uniform multiple-response cue.** Every question carries the same
  "Select all that apply." instruction, rendered by both the static form and
  the JS-built mixed form and linked to the fieldset with `aria-describedby`.
  It gives no count of correct answers, and stems are worded neutrally so
  they do not imply one either. `test_js_cue_matches_the_static_cue` keeps
  the two renderings identical.
- **No length cue.** The longest option is no more likely to be correct than
  chance. `test_longest_option_is_not_systematically_correct` (in
  `tests/test_render_learn.py`) fails when the share of questions whose
  single longest option is correct exceeds the expected share (the sum of
  correct options over options) by more than 10 percentage points of the
  bank. At release the count was 82 against an expected 87.97 and a bound
  of 107.27.
- **Storage.** The mixed quiz stores nothing. A category quiz restores only
  its score on reload, and Reset clears that quiz's stored results.
- **Firefox soft reload.** Firefox, and back/forward restores from the
  bfcache, can bring back ticked checkboxes with no feedback. Inputs are now
  cleared on build, a `pageshow` listener (`persisted`) clears each question
  again, and the mixed forms set `autocomplete="off"`.
- **Manual checks stay manual.** There is no browser in the devcontainer, so
  the DOM flow, the mixed wiring and the screen-reader announcements are
  covered only by the manual checks above.

Open follow-ups: #29, #30, #32 and #34.
