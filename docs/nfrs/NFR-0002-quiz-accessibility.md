# NFR-0002. Quizzes are operable by keyboard and screen reader and degrade without JavaScript

## Status

Accepted

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

## Source

The learning hub plan (`../plans/2026-10-learning-hub.md`) and
[ADR 0008](../adrs/0008-learning-hub-in-the-dataset-repo.md), which chose
to build a small quiz engine of our own instead of a third-party plugin.

## Verification

- Automated, on every commit through the `js-tests` prek hook
  (`node --test`, `tests/js/quiz-core.test.js`): the pure core in
  `site-assets/quiz-core.js` (scoring, seeded drawing, and progress
  storage that never throws on a null, throwing or corrupt store).
- Manual, at the learning hub's G3 gate and after any change to
  `site-assets/` or the quiz markup: in a real browser, (1) complete a
  quiz with the keyboard only and check the focus order, the focus after
  "Check" and "Reset", and the visible focus ring; (2) turn JavaScript
  off and check that every question still offers "Show answer"; (3) check
  the correct and incorrect states with a greyscale or forced-colours
  view; (4) optionally listen with a screen reader for the result and
  score announcements.
