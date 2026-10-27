"""Tests for the learning-hub renderer (``taxonomy.render_learn``)."""

from __future__ import annotations

import html
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path

import pytest

from taxonomy import render_learn
from taxonomy.load import branch_slug, load_dataset, load_learn, load_registry
from taxonomy.model import Dataset, Learn, Source

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "learn"


@pytest.fixture(scope="module")
def ds() -> Dataset:
    return load_dataset(REPO)


@pytest.fixture
def learn(tmp_path: Path) -> Learn:
    shutil.copytree(FIXTURES, tmp_path / "data" / "learn")
    return load_learn(tmp_path)


@pytest.fixture
def registry(tmp_path: Path) -> dict[str, Source]:
    root = tmp_path / "reg"
    shutil.copytree(FIXTURES, root / "data" / "learn")
    for rel in ("data/sources.yaml", "paper/references-extra.yaml"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, root / rel)
    return load_registry(root)


class Collect(HTMLParser):
    """Tags with attributes, in document order."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))


def tags(fragment: str) -> list[tuple[str, dict[str, str | None]]]:
    parser = Collect()
    parser.feed(fragment)
    return parser.tags


def test_question_markup_follows_the_contract(ds: Dataset, learn: Learn) -> None:
    q = next(q for q in learn.questions if q["id"] == "q-a-01")
    out = render_learn.question_html(q, ds.all_ids())
    found = tags(out)
    names = [t for t, _ in found]
    assert names[:3] == ["form", "fieldset", "legend"]
    assert found[0][1] == {"class": "quiz-q", "data-qid": "q-a-01"}
    # Every question carries the same cue, tied to the fieldset for screen readers.
    assert found[1][1] == {"aria-describedby": "q-a-01-hint"}
    assert ("p", {"class": "quiz-hint", "id": "q-a-01-hint"}) in found
    assert '<p class="quiz-hint" id="q-a-01-hint">Select all that apply.</p>' in out
    boxes = [a for t, a in found if t == "input"]
    assert [b["value"] for b in boxes] == ["0", "1", "2", "3"]
    assert all(b["type"] == "checkbox" and b["name"] == "q-a-01" for b in boxes)
    assert [b.get("data-correct") for b in boxes] == ["1", None, None, None]
    fb = [a for t, a in found if t == "p" and a.get("class") == "quiz-fb"]
    assert [f["data-for"] for f in fb] == ["0", "1", "2", "3"]
    assert all("hidden" in f for f in fb)
    assert ("button", {"type": "submit"}) in found
    assert ("p", {"class": "quiz-result", "aria-live": "polite"}) in found
    assert any(t == "details" and a.get("class") == "quiz-answer" for t, a in found)
    # The no-JS answer shows every option's feedback and its verdict.
    answer = out.split('<details class="quiz-answer">')[1]
    assert answer.count("<li>") == 4 and "Correct:" in answer and "Incorrect:" in answer
    assert "\n\n" not in out  # a blank line would end the raw HTML block
    # Rule IDs in feedback link to the rule's entry.
    assert '<a href="../../07-rules/#p1">P1</a>' in out


def test_quiz_block_wraps_questions(ds: Dataset, learn: Learn) -> None:
    out = render_learn.quiz_block("a", learn.questions[:1], ds.all_ids())
    assert out.startswith('<div class="quiz" data-quiz="a">')
    assert '<p class="quiz-score" aria-live="polite"></p>' in out
    assert 'class="quiz-reset"' in out and out.endswith("</div>")


def test_mixed_block(ds: Dataset) -> None:
    page = render_learn.mixed_page(ds)
    assert (
        '<div class="quiz" data-quiz="mixed" '
        'data-bank="../../assets/quiz/quiz-bank.json" data-draw="10">' in page
    )
    noscript = re.search(r"<noscript>(.*?)</noscript>", page, re.S)
    assert noscript and 'href="../a/"' in noscript.group(1)
    assert 'href="../conflicts/"' in noscript.group(1)


def test_text_is_escaped(ds: Dataset, learn: Learn) -> None:
    q = learn.questions[0]
    q["stem"] = 'Is <b>x</b> & "y" true?'
    q["options"][0]["text"] = "<script>alert(1)</script>"
    q["options"][0]["feedback"] = "a <i>b</i> see P1 and P99999"
    out = render_learn.question_html(q, ds.all_ids())
    assert "<script>" not in out and "<b>" not in out and "<i>" not in out
    assert html.escape("<script>alert(1)</script>") in out
    assert "P99999</a>" not in out  # unknown IDs stay text


def test_longest_option_is_not_systematically_correct() -> None:
    """The live bank must not teach "pick the longest option".

    ``observed`` counts the questions whose single longest option (by characters;
    a tie is not a longest) is correct; ``expected`` is what a length-blind
    bank would give: the sum of correct options over options. The bound is
    10 percentage points of the bank.
    """
    questions = load_learn(REPO).questions
    assert questions
    observed = 0
    expected = 0.0
    for q in questions:
        options = q["options"]
        lengths = [len(o["text"]) for o in options]
        longest = [i for i, n in enumerate(lengths) if n == max(lengths)]
        if len(longest) == 1 and options[longest[0]]["correct"]:
            observed += 1
        expected += sum(o["correct"] for o in options) / len(options)
    assert observed <= expected + 0.10 * len(questions), (observed, expected)


def test_stems_do_not_hint_at_the_number_of_correct_answers() -> None:
    """The cue is the same on every question; stems neither repeat nor contradict it."""
    for q in load_learn(REPO).questions:
        assert "select all" not in q["stem"].lower(), q["id"]
        assert not re.search(r"\bWhich (?!of )\w", q["stem"].split(". ")[-1]), q["id"]


def test_js_cue_matches_the_static_cue() -> None:
    """The mixed test renders in JS; its cue and hint id must match the static form."""
    js = (REPO / "site-assets" / "quiz.js").read_text(encoding="utf-8")
    assert f'const HINT_TEXT = "{render_learn.SELECT_CUE}";' in js
    assert "const hintId = `${q.id}-hint`;" in js


def test_bank_lists_every_question_with_html_feedback(
    ds: Dataset, learn: Learn
) -> None:
    bank = render_learn.bank(learn, ds.all_ids())
    assert [b["id"] for b in bank] == ["q-a-01", "q-k-01"]
    assert [b["category"] for b in bank] == ["a", "k"]
    first = bank[0]
    assert set(first) == {"id", "category", "rules", "stem", "options"}
    assert first["options"][0]["correct"] is True
    assert "../../07-rules/#p1" in first["options"][0]["feedback_html"]
    assert "../../08-conflicts/#k2" in bank[1]["options"][0]["feedback_html"]


def test_category_page_has_anchors_example_and_case(
    ds: Dataset, learn: Learn, registry: dict[str, Source]
) -> None:
    cat = ds.category_by_id()["A"]
    page = render_learn.category_page(ds, learn, registry, cat)
    for rid in cat["rules"]:
        assert f"{{#{rid.lower()}}}" in page
    assert "Illustrative, not evidence." in page
    assert "Management variant" in page
    assert page.count("No example yet.") == len(cat["rules"]) - 2
    assert "Real case: A demo case (1999)" in page
    assert "The check was never run." in page
    assert "<blockquote><p>a made-up quote</p>" in page
    assert 'href="https://example.org/case-demo-report"' in page


def test_branch_page_has_an_anchor_per_domain_row(ds: Dataset, learn: Learn) -> None:
    page = render_learn.branch_page(ds, learn, "Civil")
    rows = [r for r in ds.domains["domains"] if r["branch"] == "Civil"]
    for row in rows:
        assert f"{{#{render_learn.slug(row['domain'])}}}" in page
    assert "A bridge design is reviewed." in page
    assert "An independent engineer checks the design." in page
    assert '<a href="../../07-rules/#p56">P56</a>' in page


def test_pages_render_with_empty_data(ds: Dataset) -> None:
    pages = render_learn.pages(ds, Learn(), {})
    assert len(pages) == 3 + 9 + 20 + 10
    assert "No questions yet." in pages["quiz/a.md"]
    assert "No questions yet." in pages["quiz/conflicts.md"]
    assert "No example yet." in pages["learn/a.md"]
    assert render_learn.branch_page_name("Cross-cutting") in pages
    assert render_learn.bank(Learn(), ds.all_ids()) == []


def test_branch_pages_match_slugs(ds: Dataset) -> None:
    names = {render_learn.branch_page_name(b) for b in render_learn.branches(ds)}
    assert len(names) == 20
    assert all(
        branch_slug(b) in render_learn.branch_page_name(b)
        for b in render_learn.branches(ds)
    )


def test_add_learn_links_only_for_rules_with_examples(
    ds: Dataset, learn: Learn
) -> None:
    chapter = (REPO / "publication" / "chapters" / "07-rules.md").read_text("utf-8")
    out = render_learn.add_learn_links(chapter, learn, ds)
    assert "Public safety first ([Learn](learn/a.md#p1)) |" in out
    assert "(learn/a.md#p5)" in out
    assert "(learn/a.md#p2)" not in out
    assert out.count("[Learn](") == 2
    assert render_learn.add_learn_links(chapter, Learn(), ds) == chapter
