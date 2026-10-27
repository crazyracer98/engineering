// Pure quiz logic: no DOM, no globals. Imported by quiz.js and by the node tests.

const KEY_PREFIX = "engineering-quiz:v1:";

/** True when `selected` and `correct` hold exactly the same indices (order and duplicates ignored). */
export function score(selected, correct) {
  const a = new Set(selected);
  const b = new Set(correct);
  if (a.size !== b.size) return false;
  for (const x of a) if (!b.has(x)) return false;
  return true;
}

/**
 * Draw `n` distinct items from `bank` without replacement (partial
 * Fisher-Yates on a copy). `rng` returns a number in [0, 1). When `n`
 * exceeds the bank, the whole bank comes back shuffled.
 */
export function draw(bank, n, rng = Math.random) {
  const pool = Array.from(bank);
  const k = Math.max(0, Math.min(Math.floor(Number(n)) || 0, pool.length));
  for (let i = 0; i < k; i++) {
    const j = i + Math.min(Math.floor(rng() * (pool.length - i)), pool.length - i - 1);
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, k);
}

export function progressKey(quiz) {
  return KEY_PREFIX + quiz;
}

function emptyProgress() {
  return { answered: {} };
}

/** Read saved progress; any failure yields `{answered: {}}`. Never throws. */
export function loadProgress(storage, quiz) {
  try {
    const raw = storage.getItem(progressKey(quiz));
    if (raw == null) return emptyProgress();
    const data = JSON.parse(raw);
    const src = data && data.answered;
    if (!src || typeof src !== "object" || Array.isArray(src)) return emptyProgress();
    const answered = {};
    for (const [qid, v] of Object.entries(src)) {
      if (typeof v === "boolean") answered[qid] = v;
    }
    return { answered };
  } catch {
    return emptyProgress();
  }
}

/** Save progress; returns true on success, false on any failure. Never throws. */
export function saveProgress(storage, quiz, progress) {
  try {
    storage.setItem(progressKey(quiz), JSON.stringify({ answered: progress.answered }));
    return true;
  } catch {
    return false;
  }
}

/** The mixed test is a fresh random draw each time, so it never touches progress storage. */
export function persistsProgress(quiz) {
  return quiz !== "mixed";
}

/**
 * Running score from stored progress, counting only question ids in `ids`
 * (stored ids no longer on the page are ignored). Never throws.
 */
export function scoreFromProgress(progress, ids) {
  const answered = progress && progress.answered && typeof progress.answered === "object" ? progress.answered : {};
  let done = 0;
  let right = 0;
  for (const id of ids) {
    if (Object.hasOwn(answered, id) && typeof answered[id] === "boolean") {
      done++;
      if (answered[id]) right++;
    }
  }
  return { right, done, total: ids.length };
}
