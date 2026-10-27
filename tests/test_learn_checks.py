"""Seeded violations for the learning-hub checks and the coverage report (FR-0001)."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from taxonomy import validate
from taxonomy.load import branch_slug, load_learn, load_registry
from taxonomy.validate import (
    CHECKS,
    LEARN_CHECKS,
    learn_coverage,
    make_context,
    run_checks,
)

Edit = Callable[[str, Callable[[Any], None]], None]

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "learn"


@pytest.fixture
def stub_repo(repo: Path) -> Path:
    """The repo copy with every learning file emptied, whatever content is live."""
    paths = sorted((repo / "data" / "learn").rglob("*.yaml"))
    assert paths, "no learn files found; the layout or the repo fixture changed"
    yaml = YAML(typ="safe")
    for path in paths:
        # Keep each file's top-level shape (all are lists today, per the schemas).
        empty = "{}\n" if isinstance(yaml.load(path), dict) else "[]\n"
        path.write_text(empty, encoding="utf-8")
    return repo


@pytest.fixture
def learn_repo(stub_repo: Path) -> Path:
    """The stub layout plus the small valid learning content of ``fixtures/learn``."""
    shutil.copytree(FIXTURES, stub_repo / "data" / "learn", dirs_exist_ok=True)
    return stub_repo


def messages(root: Path, check: str) -> list[str]:
    return [f.message for f in run_checks(root) if f.check == check]


def test_stub_dataset_is_clean(stub_repo: Path) -> None:
    assert run_checks(stub_repo) == []
    learn = load_learn(stub_repo)
    assert learn.rule_examples == [] and learn.cases == []
    assert learn.questions == [] and learn.domain_examples == []


def test_valid_fixture_is_clean(learn_repo: Path) -> None:
    assert run_checks(learn_repo) == []
    learn = load_learn(learn_repo)
    assert [e["rule"] for e in learn.rule_examples] == ["P1", "P5"]
    assert [d["domain"] for d in learn.domain_examples] == ["Structural and building"]
    assert [q["id"] for q in learn.questions] == ["q-a-01", "q-k-01"]
    assert [c["id"] for c in learn.cases] == ["case-demo"]
    assert "case-demo-report" in load_registry(learn_repo)


def test_every_learn_check_is_listed_in_the_nfr() -> None:
    nfr = (
        Path(__file__).resolve().parent.parent
        / "docs/nfrs/NFR-0001-dataset-integrity.md"
    ).read_text(encoding="utf-8")
    assert set(LEARN_CHECKS).isdisjoint(CHECKS)
    for name in LEARN_CHECKS:
        assert f"`{name}`" in nfr


def test_branch_slugs() -> None:
    assert branch_slug("Civil") == "civil"
    assert (
        branch_slug("Management: Portfolio, programme and project")
        == "management-portfolio-programme-and-project"
    )


def test_all_domain_branches_have_a_stub(repo: Path) -> None:
    # Deliberately the copied live repo: this pins the live data/learn/domains
    # files to the live domains.yaml, so a fixture repo would test nothing.
    domains = make_context(repo).ds.domains["domains"]
    slugs = {branch_slug(d["branch"]) for d in domains}
    files = {p.stem for p in (repo / "data/learn/domains").glob("*.yaml")}
    assert files == slugs


# -- layout -----------------------------------------------------------------------


def test_layout_unknown_file(learn_repo: Path) -> None:
    (learn_repo / "data/learn/rules/z.yaml").write_text("[]\n", encoding="utf-8")
    (learn_repo / "data/learn/extra").mkdir()
    msgs = messages(learn_repo, "learn-layout")
    assert any("rules/z.yaml: unknown file name 'z'" in m for m in msgs)
    assert any("data/learn/extra is not part of the layout" in m for m in msgs)


# -- schemas ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rel", "mutate", "expect"),
    [
        (
            "data/learn/rules/a.yaml",
            lambda d: d[0].pop("violating"),
            "'violating' is a required property",
        ),
        (
            "data/learn/domains/civil.yaml",
            lambda d: d[0].update(shows=[]),
            "should be non-empty",
        ),
        (
            "data/learn/quiz/a.yaml",
            lambda d: d[0]["options"].pop(),
            "is too short",
        ),
        (
            "data/learn/quiz/a.yaml",
            lambda d: d[0].update(id="q-z-01"),
            "does not match",
        ),
        (
            "data/learn/cases/1.yaml",
            lambda d: d[0].update(id="demo"),
            "does not match",
        ),
        (
            "data/learn/sources/1.yaml",
            lambda d: d[0].pop("author"),
            "'author' is a required property",
        ),
    ],
)
def test_schema_violations(
    learn_repo: Path,
    edit: Edit,
    rel: str,
    mutate: Callable[[Any], None],
    expect: str,
) -> None:
    edit(rel, mutate)
    msgs = messages(learn_repo, "schema")
    assert any(m.startswith(rel) and expect in m for m in msgs), msgs


def test_schema_question_with_seven_options(learn_repo: Path, edit: Edit) -> None:
    def add(d: Any) -> None:
        d[0]["options"].extend(dict(d[0]["options"][1]) for _ in range(3))

    edit("data/learn/quiz/a.yaml", add)
    msgs = messages(learn_repo, "schema")
    assert any("is too long" in m for m in msgs), msgs


# -- rule examples --------------------------------------------------------------


def test_rule_example_unknown_rule(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/rules/a.yaml", lambda d: d[1].update(rule="P999"))
    assert any(
        "unknown rule P999" in m for m in messages(learn_repo, "learn-rule-examples")
    )


def test_rule_example_duplicate(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/rules/a.yaml", lambda d: d[1].update(rule="P1"))
    msgs = messages(learn_repo, "learn-rule-examples")
    assert any("second example for P1" in m for m in msgs), msgs


def test_rule_example_in_wrong_category_file(learn_repo: Path) -> None:
    src = learn_repo / "data/learn/rules/a.yaml"
    (learn_repo / "data/learn/rules/b.yaml").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    msgs = messages(learn_repo, "learn-rule-examples")
    assert any("rules/b.yaml: P1 is in category A" in m for m in msgs), msgs


def test_rule_example_management_missing(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/rules/a.yaml", lambda d: d[0].pop("management"))
    msgs = messages(learn_repo, "learn-rule-examples")
    assert any("P1 has a management form; add `management`" in m for m in msgs), msgs


def test_rule_example_management_unexpected(learn_repo: Path, edit: Edit) -> None:
    edit(
        "data/learn/rules/a.yaml",
        lambda d: d[1].update(management=dict(d[0]["management"])),
    )
    msgs = messages(learn_repo, "learn-rule-examples")
    assert any("P5 has no management form; remove" in m for m in msgs), msgs


# -- domain examples ------------------------------------------------------------


def test_domain_example_unknown_row(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/domains/civil.yaml", lambda d: d[0].update(domain="Nope"))
    msgs = messages(learn_repo, "learn-domain-examples")
    assert any("no domains.yaml row for 'Civil' / 'Nope'" in m for m in msgs), msgs


def test_domain_example_rule_not_in_row(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/domains/civil.yaml", lambda d: d[0]["shows"][0].update(rule="P1"))
    msgs = messages(learn_repo, "learn-domain-examples")
    assert any("shows P1, which is not among the row's rules" in m for m in msgs), msgs


def test_domain_example_wrong_branch_file(learn_repo: Path) -> None:
    src = learn_repo / "data/learn/domains/civil.yaml"
    (learn_repo / "data/learn/domains/mining.yaml").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    msgs = messages(learn_repo, "learn-domain-examples")
    assert any("it belongs in domains/civil.yaml" in m for m in msgs), msgs
    assert any("second example for Civil" in m for m in msgs), msgs


# -- questions ------------------------------------------------------------------------


def test_question_duplicate_id(learn_repo: Path) -> None:
    src = learn_repo / "data/learn/quiz/a.yaml"
    (learn_repo / "data/learn/quiz/b.yaml").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    msgs = messages(learn_repo, "learn-questions")
    assert any("duplicate question ID q-a-01" in m for m in msgs), msgs
    assert any("has category 'a' but sits in the file for 'b'" in m for m in msgs), msgs


def test_question_category_must_match_file(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/quiz/conflicts.yaml", lambda d: d[0].update(id="q-a-02"))
    msgs = messages(learn_repo, "learn-questions")
    assert any(
        "q-a-02 has category 'a' but sits in the file for 'k'" in m for m in msgs
    )


def test_question_unknown_rule(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/quiz/a.yaml", lambda d: d[0].update(rules=["P1", "P999"]))
    msgs = messages(learn_repo, "learn-questions")
    assert any("q-a-01 names unknown rule P999" in m for m in msgs), msgs


def test_question_rules_must_fit_the_file(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/quiz/a.yaml", lambda d: d[0].update(rules=["P1", "K2"]))
    edit("data/learn/quiz/conflicts.yaml", lambda d: d[0].update(rules=["K2", "P1"]))
    msgs = messages(learn_repo, "learn-questions")
    assert any("q-a-01 names K2; category questions" in m for m in msgs), msgs
    assert any("q-k-01 names P1; conflicts questions" in m for m in msgs), msgs
    edit("data/learn/quiz/a.yaml", lambda d: d[0].update(rules=["P50"]))
    msgs = messages(learn_repo, "learn-questions")
    assert any("q-a-01 names no rule of category A" in m for m in msgs), msgs


def test_malformed_entries_do_not_crash_checks(learn_repo: Path) -> None:
    for kind in ("rules/a", "domains/civil", "quiz/a", "cases/1", "sources/1"):
        (learn_repo / f"data/learn/{kind}.yaml").write_text(
            "- foo\n- {rule: [x], id: 3, rules: oops, slug: 5, branch: {}}\n",
            encoding="utf-8",
        )
    findings = run_checks(learn_repo)
    assert not any("crashed" in f.message for f in findings), findings
    assert any(f.check == "schema" for f in findings)
    assert learn_coverage(make_context(learn_repo))  # no traceback


def test_layout_ignores_dotfiles(learn_repo: Path) -> None:
    (learn_repo / "data/learn/quiz/.gitkeep").write_text("", encoding="utf-8")
    assert messages(learn_repo, "learn-layout") == []


def test_question_without_correct_option(learn_repo: Path, edit: Edit) -> None:
    def mutate(d: Any) -> None:
        d[0]["options"][0]["correct"] = False

    edit("data/learn/quiz/a.yaml", mutate)
    assert any(
        "q-a-01 has no correct option" in m
        for m in messages(learn_repo, "learn-questions")
    )


def test_question_without_incorrect_option(learn_repo: Path, edit: Edit) -> None:
    def mutate(d: Any) -> None:
        for o in d[0]["options"]:
            o["correct"] = True

    edit("data/learn/quiz/a.yaml", mutate)
    msgs = messages(learn_repo, "learn-questions")
    assert any("q-a-01 has no incorrect option" in m for m in msgs), msgs


# -- cases and sources ------------------------------------------------------------


def test_case_unknown_source(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/cases/1.yaml", lambda d: d[0]["quotes"][0].update(source="nope"))
    msgs = messages(learn_repo, "learn-cases")
    assert any("quotes unknown source slug 'nope'" in m for m in msgs), msgs


def test_case_unknown_rule(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/cases/1.yaml", lambda d: d[0].update(rules=["P1", "P999"]))
    assert any("unknown rule P999" in m for m in messages(learn_repo, "learn-cases"))


def test_case_lesson_rule_must_be_in_case(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/cases/1.yaml", lambda d: d[0]["lessons"][0].update(rule="P2"))
    msgs = messages(learn_repo, "learn-cases")
    assert any("lesson for P2, not in its `rules`" in m for m in msgs), msgs


def test_case_second_case_for_a_rule(learn_repo: Path) -> None:
    text = (learn_repo / "data/learn/cases/1.yaml").read_text(encoding="utf-8")
    (learn_repo / "data/learn/cases/2.yaml").write_text(
        text.replace("case-demo", "case-other"), encoding="utf-8"
    )
    msgs = messages(learn_repo, "learn-cases")
    assert any(
        "case-other is a second case for P1 (see case-demo)" in m for m in msgs
    ), msgs


def test_case_duplicate_id(learn_repo: Path) -> None:
    text = (learn_repo / "data/learn/cases/1.yaml").read_text(encoding="utf-8")
    (learn_repo / "data/learn/cases/2.yaml").write_text(text, encoding="utf-8")
    msgs = messages(learn_repo, "learn-cases")
    assert any("duplicate case ID case-demo" in m for m in msgs), msgs


def test_case_source_slug_needs_prefix(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/sources/1.yaml", lambda d: d[0].update(slug="demo-report"))
    edit(
        "data/learn/cases/1.yaml",
        lambda d: d[0]["quotes"][0].update(source="demo-report"),
    )
    msgs = messages(learn_repo, "learn-sources")
    assert any("'demo-report' must start with 'case-'" in m for m in msgs), msgs


def test_case_source_unused(learn_repo: Path, edit: Edit) -> None:
    edit("data/learn/cases/1.yaml", lambda d: d[0].update(quotes=[]))
    msgs = messages(learn_repo, "source-used")
    assert any("case-demo-report (data/learn/sources/1.yaml)" in m for m in msgs), msgs


def test_case_source_duplicates_registry_entry(learn_repo: Path, edit: Edit) -> None:
    def mutate(d: Any) -> None:
        d[0]["url"] = make_context(learn_repo).ds.sources[0]["url"]

    edit("data/learn/sources/1.yaml", mutate)
    assert any("URL" in m for m in messages(learn_repo, "registry-unique"))
    with pytest.raises(ValueError, match="duplicate"):
        edit(
            "data/learn/sources/2.yaml",
            lambda d: d.append(
                {
                    "slug": "case-demo-report",
                    "title": "x",
                    "author": [{"literal": "x"}],
                    "url": "https://example.org/x",
                    "kind": "primary",
                    "paid": False,
                }
            ),
        )
        load_registry(learn_repo)


def test_unparsable_learn_file_is_a_finding(learn_repo: Path) -> None:
    (learn_repo / "data/learn/quiz/c.yaml").write_text(
        "- [unclosed\n", encoding="utf-8"
    )
    findings = run_checks(learn_repo)
    assert any("quiz/c.yaml" in f.message for f in findings)


# -- coverage ----------------------------------------------------------------------


def dump(path: Path, doc: Any) -> None:
    yaml = YAML()
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(doc, handle)


def question(qid: str, rule: str) -> dict[str, Any]:
    options = [
        {"text": f"o{i}", "correct": i == 0, "feedback": f"see {rule}"}
        for i in range(4)
    ]
    return {"id": qid, "rules": [rule], "stem": "Which?", "options": options}


def test_coverage_reports_every_gap_on_stubs(stub_repo: Path) -> None:
    ctx = make_context(stub_repo)
    gaps = learn_coverage(ctx)
    assert sum("has no rule example" in g for g in gaps) == 83
    assert sum("has no domain example" in g for g in gaps) == 130
    assert sum("question(s) in quiz/" in g for g in gaps) == 83
    assert sum("no question in quiz/conflicts.yaml" in g for g in gaps) == 8


def test_coverage_scopes(stub_repo: Path) -> None:
    ctx = make_context(stub_repo)
    gaps_i = learn_coverage(ctx, "i")
    assert len(gaps_i) == 8  # 4 rules: one example and one quiz line each
    assert all("rules/i.yaml" in g or "quiz/i.yaml" in g for g in gaps_i)
    assert len(learn_coverage(ctx, "k")) == 8
    assert len(learn_coverage(ctx, "conflicts")) == 8
    assert all("Mining" in g for g in learn_coverage(ctx, "mining"))
    with pytest.raises(ValueError, match="unknown scope"):
        learn_coverage(ctx, "zz")


def test_coverage_complete_scope_has_no_gaps(stub_repo: Path) -> None:
    ctx = make_context(stub_repo)
    cat = next(c for c in ctx.ds.categories if c["id"] == "I")
    rules = ctx.ds.rule_by_id()
    examples: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    for rid in cat["rules"]:
        ex: dict[str, Any] = {
            "rule": rid,
            "scenario": "s",
            "applying": "a",
            "violating": "v",
        }
        if rules[rid].get("management"):
            ex["management"] = {"scenario": "s", "applying": "a", "violating": "v"}
        examples.append(ex)
        questions += [question(f"q-i-{len(questions) + n:02d}", rid) for n in (1, 2)]
    dump(stub_repo / "data/learn/rules/i.yaml", examples)
    dump(stub_repo / "data/learn/quiz/i.yaml", questions)
    assert run_checks(stub_repo) == []
    assert learn_coverage(make_context(stub_repo), "i") == []
    # One question short for the last rule is a gap again.
    dump(stub_repo / "data/learn/quiz/i.yaml", questions[:-1])
    gaps = learn_coverage(make_context(stub_repo), "i")
    assert gaps == [
        f"{cat['rules'][-1]} has 1 question(s) in quiz/i.yaml; it needs at least 2"
    ]


def test_coverage_conflict_question_counts(learn_repo: Path) -> None:
    gaps = learn_coverage(make_context(learn_repo), "k")
    assert "K2 has no question in quiz/conflicts.yaml" not in gaps
    assert "K1 has no question in quiz/conflicts.yaml" in gaps


def test_coverage_cli(stub_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        validate.main(["--learn-coverage", "--scope", "i", "--root", str(stub_repo)])
        == 1
    )
    out = capsys.readouterr().out
    first = make_context(stub_repo).ds.category_by_id()["I"]["rules"][0]
    assert f"{first} has no rule example (data/learn/rules/i.yaml)" in out
    assert "learn coverage (scope i): 8 gap(s)" in out
    assert (
        validate.main(["--learn-coverage", "--scope", "zz", "--root", str(stub_repo)])
        == 2
    )
