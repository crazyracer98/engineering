"""Render the learning hub (Learn and Quiz pages, ``quiz-bank.json``) for the site.

All text in ``data/learn/`` is plain text (the schemas do not allow Markdown),
so every value is HTML-escaped; rule IDs (``P12``, ``K3``) inside it become
links to the rule's entry in chapter 7 or 8. Every page is written at depth
two (``learn/a.md`` serves ``learn/a/``), so the same relative links work on
every page and in ``quiz-bank.json``. Pages render when the data is empty.
"""

from __future__ import annotations

import html
import re
from typing import Any

from taxonomy.load import branch_slug
from taxonomy.model import Category, Dataset, Learn, Question, RuleExample, Source

#: Where the quiz bank is published, relative to the site root.
BANK_PATH = "assets/quiz/quiz-bank.json"
#: ``data-bank`` of the mixed test, relative to ``quiz/mixed/``.
BANK_URL = "../../" + BANK_PATH
#: How many questions the mixed test draws.
MIXED_DRAW = 10
#: Illustrative-example label, shown on every example.
ILLUSTRATIVE = "Illustrative, not evidence."

_ID = re.compile(r"\b[PK][1-9][0-9]*\b")
_NONWORD = re.compile(r"[^a-z0-9]+")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def slug(text: str) -> str:
    return _NONWORD.sub("-", text.lower()).strip("-")


def rule_href(rule_id: str) -> str:
    """Link to a rule (``P12``, chapter 7) or a conflict rule (``K3``, chapter 8)."""
    chapter = "08-conflicts" if rule_id.startswith("K") else "07-rules"
    return f"../../{chapter}/#{rule_id.lower()}"


def linked(text: str, known: set[str]) -> str:
    """Escape ``text`` and turn every known rule ID in it into a link."""

    def link(match: re.Match[str]) -> str:
        found = match.group(0)
        if found not in known:
            return found
        return f'<a href="{rule_href(found)}">{found}</a>'

    return _ID.sub(link, esc(text))


def rule_links(ids: list[str], known: set[str]) -> str:
    return ", ".join(linked(i, known) for i in ids)


def category_page_name(cat: str) -> str:
    return f"learn/{cat.lower()}.md"


def branch_page_name(branch: str) -> str:
    return f"learn/branch-{branch_slug(branch)}.md"


def quiz_page_name(quiz: str) -> str:
    return f"quiz/{quiz}.md"


def quiz_ids(ds: Dataset) -> list[str]:
    """The quiz names in nav order: the categories (``a``..), then ``conflicts``."""
    return [c["id"].lower() for c in ds.categories] + ["conflicts"]


def branches(ds: Dataset) -> list[str]:
    """Branch headings of ``domains.yaml`` in file order."""
    out: list[str] = []
    for row in ds.domains["domains"]:
        if row["branch"] not in out:
            out.append(row["branch"])
    return out


def question_category(question: Question) -> str:
    """``a``..``i`` or ``k`` from a ``q-<cat>-NN`` ID."""
    return question["id"].split("-")[1]


# ---- quiz markup (the HTML contract of docs/plans/2026-10-learning-hub.md) ----


def question_html(q: Question, known: set[str]) -> str:
    """One question as a ``form.quiz-q``; no blank lines, so Markdown keeps it raw."""
    qid = esc(q["id"])
    parts = [
        f'<form class="quiz-q" data-qid="{qid}">',
        f"<fieldset><legend>{esc(q['stem'])}</legend>",
    ]
    for i, opt in enumerate(q["options"]):
        correct = ' data-correct="1"' if opt["correct"] else ""
        parts.append(
            f'<label><input type="checkbox" name="{qid}" value="{i}"{correct}> '
            f"{esc(opt['text'])}</label>"
        )
        parts.append(
            f'<p class="quiz-fb" data-for="{i}" hidden>'
            f"{linked(opt['feedback'], known)}</p>"
        )
    parts += [
        "</fieldset>",
        '<button type="submit">Check</button>',
        '<p class="quiz-result" aria-live="polite"></p>',
        '<details class="quiz-answer"><summary>Show answer</summary>',
        "<ul>",
    ]
    for opt in q["options"]:
        verdict = "Correct" if opt["correct"] else "Incorrect"
        parts.append(
            f"<li><strong>{verdict}:</strong> {esc(opt['text'])}. "
            f"{linked(opt['feedback'], known)}</li>"
        )
    parts += ["</ul>", "</details>", "</form>"]
    return "\n".join(parts)


def quiz_block(quiz: str, questions: list[Question], known: set[str]) -> str:
    body = [question_html(q, known) for q in questions]
    return "\n".join(
        [
            f'<div class="quiz" data-quiz="{esc(quiz)}">',
            *body,
            '<p class="quiz-score" aria-live="polite"></p>',
            '<button type="button" class="quiz-reset">Reset</button>',
            "</div>",
        ]
    )


def mixed_block(categories: list[tuple[str, str]]) -> str:
    """The mixed test; ``categories`` are (quiz name, label) for the no-JS pointer."""
    links = ", ".join(
        f'<a href="../{name}/">{esc(label)}</a>' for name, label in categories
    )
    return "\n".join(
        [
            f'<div class="quiz" data-quiz="mixed" data-bank="{BANK_URL}" '
            f'data-draw="{MIXED_DRAW}">',
            "<noscript><p>The mixed test needs JavaScript. Without it, take the "
            f"category quizzes: {links}.</p></noscript>",
            '<p class="quiz-score" aria-live="polite"></p>',
            '<button type="button" class="quiz-reset">Reset</button>',
            "</div>",
        ]
    )


def bank(learn: Learn, known: set[str]) -> list[dict[str, Any]]:
    """``quiz-bank.json``: the whole bank, feedback as HTML."""
    return [
        {
            "id": q["id"],
            "category": question_category(q),
            "rules": list(q["rules"]),
            "stem": q["stem"],
            "options": [
                {
                    "text": o["text"],
                    "correct": o["correct"],
                    "feedback_html": linked(o["feedback"], known),
                }
                for o in q["options"]
            ],
        }
        for q in learn.questions
    ]


# ---- Learn pages ----


def _p(label: str, text: str) -> str:
    return f"<p><strong>{label}</strong> {esc(text)}</p>"


def _example_html(ex: RuleExample | None) -> str:
    if ex is None:
        return "<p>No example yet.</p>"
    parts = [
        '<div class="learn-example">',
        f"<p><em>{ILLUSTRATIVE}</em></p>",
        _p("Scenario.", ex["scenario"]),
        _p("Applying the rule.", ex["applying"]),
        _p("Violating the rule.", ex["violating"]),
    ]
    mgmt = ex.get("management")
    if mgmt:
        parts += [
            '<div class="learn-management">',
            "<p><strong>Management variant.</strong></p>",
            _p("Scenario.", mgmt["scenario"]),
            _p("Applying the rule.", mgmt["applying"]),
            _p("Violating the rule.", mgmt["violating"]),
            "</div>",
        ]
    parts.append("</div>")
    return "\n".join(parts)


def _case_html(
    case: Any, rule_id: str, registry: dict[str, Source], known: set[str]
) -> str:
    parts = [
        '<div class="learn-case">',
        f"<p><strong>Real case: {esc(case['title'])} ({case['year']}).</strong></p>",
        f"<p>{esc(case['summary'])}</p>",
    ]
    for lesson in case["lessons"]:
        if lesson["rule"] == rule_id:
            parts.append(_p(f"What it shows for {rule_id}.", lesson["text"]))
    for quote in case["quotes"]:
        src = registry.get(quote["source"])
        if src:
            cite = f'<a href="{esc(src["url"])}">{esc(src["title"])}</a>'
        else:
            cite = esc(quote["source"])
        parts.append(
            f"<blockquote><p>{esc(quote['text'])}</p><p>Source: {cite}</p></blockquote>"
        )
    parts.append("</div>")
    return "\n".join(parts)


def category_page(
    ds: Dataset, learn: Learn, registry: dict[str, Source], cat: Category
) -> str:
    known = ds.all_ids()
    rules = ds.rule_by_id()
    examples = {e["rule"]: e for e in learn.rule_examples}
    lines = [
        f"# {cat['id']}. {esc(cat['name'])}",
        "",
        esc(cat["description"]),
        "",
        f'<p>Take the <a href="../../quiz/{cat["id"].lower()}/">{esc(cat["name"])} '
        "quiz</a> when you have read the examples.</p>",
        "",
    ]
    for rid in cat["rules"]:
        rule = rules[rid]
        lines += [
            f"## {rid}. {esc(rule['name'])} {{#{rid.lower()}}}",
            "",
            f'<p><a href="{rule_href(rid)}">The rule</a>: {esc(rule["then"])}</p>',
            "",
            _example_html(examples.get(rid)),
            "",
        ]
        for case in learn.cases:
            if rid in case["rules"]:
                lines += [_case_html(case, rid, registry, known), ""]
    return "\n".join(lines)


def branch_page(ds: Dataset, learn: Learn, branch: str) -> str:
    known = ds.all_ids()
    examples = {e["domain"]: e for e in learn.domain_examples if e["branch"] == branch}
    lines = [f"# {esc(branch)}", ""]
    for row in ds.domains["domains"]:
        if row["branch"] != branch:
            continue
        domain = row["domain"]
        lines += [
            f"## {esc(domain)} {{#{slug(domain)}}}",
            "",
            f"<p>Rules found in this domain: {rule_links(row['rules'], known)}.</p>",
            "",
        ]
        ex = examples.get(domain)
        if ex is None:
            lines += ["<p>No example yet.</p>", ""]
            continue
        parts = [
            '<div class="learn-example">',
            f"<p><em>{ILLUSTRATIVE}</em></p>",
            _p("Scenario.", ex["scenario"]),
            "<ul>",
        ]
        for shown in ex["shows"]:
            parts.append(
                f"<li><strong>{linked(shown['rule'], known)}:</strong> "
                f"{esc(shown['how'])}</li>"
            )
        parts += ["</ul>", "</div>"]
        lines += ["\n".join(parts), ""]
    return "\n".join(lines)


def learn_index(ds: Dataset) -> str:
    lines = [
        "# Learn",
        "",
        "Worked examples for every rule and every domain row. The examples are "
        "illustrative, not evidence; a real case is marked as such and cites its "
        "source. Test yourself in the [quizzes](../quiz/index.md).",
        "",
        "## Rules by category",
        "",
    ]
    lines += [
        f"- [{c['id']}. {esc(c['name'])}]({c['id'].lower()}.md)" for c in ds.categories
    ]
    lines += ["", "## Domains by branch", ""]
    lines += [f"- [{esc(b)}](branch-{branch_slug(b)}.md)" for b in branches(ds)]
    lines.append("")
    return "\n".join(lines)


def quiz_index(ds: Dataset) -> str:
    lines = [
        "# Quiz",
        "",
        "Every question is select-all-that-apply: it counts as correct only "
        "when you select exactly the right options. Each option has its own "
        "feedback after you check. Your progress stays in this browser.",
        "",
        "- [Mixed test](mixed.md): 10 random questions from all quizzes",
        "- [Conflict rules (K1 to K8)](conflicts.md)",
    ]
    lines += [
        f"- [{c['id']}. {esc(c['name'])}]({c['id'].lower()}.md)" for c in ds.categories
    ]
    lines.append("")
    return "\n".join(lines)


def quiz_page(ds: Dataset, learn: Learn, quiz: str, questions: list[Question]) -> str:
    known = ds.all_ids()
    if quiz == "conflicts":
        title = "Conflict rules quiz"
        intro = (
            '<p>Rules K1 to K8 in the <a href="../../08-conflicts/">'
            "conflict chapter</a>.</p>"
        )
    else:
        cat = ds.category_by_id()[quiz.upper()]
        title = f"{cat['id']}. {esc(cat['name'])} quiz"
        intro = f'<p>Read the <a href="../../learn/{quiz}/">examples</a> first.</p>'
    lines = [f"# {title}", "", intro, ""]
    if questions:
        lines.append(quiz_block(quiz, questions, known))
    else:
        lines.append("<p>No questions yet.</p>")
    lines.append("")
    return "\n".join(lines)


def mixed_page(ds: Dataset) -> str:
    cats = [(c["id"].lower(), f"{c['id']}. {c['name']}") for c in ds.categories]
    cats.append(("conflicts", "Conflict rules"))
    return "\n".join(
        [
            "# Mixed test",
            "",
            f"{MIXED_DRAW} random questions from the whole bank. "
            "Reset draws a new set.",
            "",
            mixed_block(cats),
            "",
        ]
    )


def pages(ds: Dataset, learn: Learn, registry: dict[str, Source]) -> dict[str, str]:
    """Every Learn and Quiz page, by path relative to the site sources."""
    out: dict[str, str] = {
        "learn/index.md": learn_index(ds),
        "quiz/index.md": quiz_index(ds),
        "quiz/mixed.md": mixed_page(ds),
    }
    for cat in ds.categories:
        out[category_page_name(cat["id"])] = category_page(ds, learn, registry, cat)
    for b in branches(ds):
        out[branch_page_name(b)] = branch_page(ds, learn, b)
    for quiz in quiz_ids(ds):
        key = "k" if quiz == "conflicts" else quiz
        qs = [q for q in learn.questions if question_category(q) == key]
        out[quiz_page_name(quiz)] = quiz_page(ds, learn, quiz, qs)
    return out


# ---- chapter 7 ----

_RULE_ROW = re.compile(
    r'^(\| <a id="(p[1-9][0-9]*)"></a>P[1-9][0-9]* \| )((?:\\\||[^|])*?)( \|)',
    re.MULTILINE,
)


def add_learn_links(chapter: str, learn: Learn, ds: Dataset) -> str:
    """Add ``([Learn](learn/<cat>.md#pN))`` to each rule name that has an example."""
    have = {e["rule"].lower() for e in learn.rule_examples}
    cat_of = {r["id"].lower(): r["category"].lower() for r in ds.rules}

    def add(match: re.Match[str]) -> str:
        rid = match.group(2)
        if rid not in have or rid not in cat_of:
            return match.group(0)
        link = f" ([Learn](learn/{cat_of[rid]}.md#{rid}))"
        return f"{match.group(1)}{match.group(3)}{link}{match.group(4)}"

    return _RULE_ROW.sub(add, chapter)
