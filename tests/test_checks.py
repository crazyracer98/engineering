"""One seeded violation per integrity check (NFR-001); each must fail clearly."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from taxonomy.validate import CHECKS, Finding, run_checks

Edit = Callable[[str, Callable[[Any], None]], None]


def messages(root: Path, check: str) -> list[str]:
    return [f.message for f in run_checks(root) if f.check == check]


def rule(doc: Any, rid: str) -> Any:
    return next(r for r in doc if r["id"] == rid)


def test_real_dataset_is_clean(repo: Path) -> None:
    assert run_checks(repo) == []


def test_every_check_has_a_seeded_test() -> None:
    names = {
        "schema",
        "unique-ids",
        "related-targets",
        "id-references",
        "rule-in-domain",
        "source-used",
        "table-columns",
        "relation-contradictions",
        "primary-source",
        "counterexamples",
        "conflict-rules",
        "category-membership",
        "quick-view",
        "id-map",
        "citations",
        "registry-unique",
    }
    assert set(CHECKS) == names


def test_finding_str() -> None:
    assert str(Finding("x", "y")) == "[x] y"


def test_unique_ids(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        doc[1]["id"] = doc[0]["id"]

    edit("data/rules.yaml", seed)
    assert any("duplicate ID U1" in m for m in messages(repo, "unique-ids"))


def test_related_target_missing(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "U1")["related"]["strengthens"].append("U999"),
    )
    assert any(
        "U1 strengthens U999: no such rule" in m
        for m in messages(repo, "related-targets")
    )


def test_id_reference_missing(repo: Path, edit: Edit) -> None:
    edit("data/categories.yaml", lambda d: d[0]["rules"].append("U998"))
    assert any(
        "category A names unknown rule U998" in m
        for m in messages(repo, "id-references")
    )


def test_rule_in_no_domain(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        for d in doc["domains"]:
            if "U1" in d["rules"]:
                d["rules"].remove("U1")
                if not d["rules"]:
                    d["rules"].append("U2")

    edit("data/domains.yaml", seed)
    assert any("U1 appears in no domain" in m for m in messages(repo, "rule-in-domain"))


def test_unused_source(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        doc.append(
            {
                "slug": "orphan-source",
                "title": "Orphan",
                "url": "https://example.org/orphan",
                "kind": "primary",
                "paid": False,
            }
        )

    edit("data/sources.yaml", seed)
    assert any("orphan-source" in m for m in messages(repo, "source-used"))


def test_unused_paper_source(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        doc.append(
            {
                "slug": "orphan-paper",
                "title": "Orphan",
                "url": "https://example.org/orphan-paper",
                "kind": "primary",
                "paid": False,
            }
        )

    edit("paper/references-extra.yaml", seed)
    assert any("orphan-paper" in m for m in messages(repo, "source-used"))


def test_table_column_count(repo: Path, edit: Edit) -> None:
    edit("data/glossary.yaml", lambda d: d["error"].update(meaning="a | b"))
    assert any("column count" in m for m in messages(repo, "table-columns"))


def test_escaped_pipe_is_not_a_column(repo: Path, edit: Edit) -> None:
    edit("data/glossary.yaml", lambda d: d["error"].update(meaning="a \\| b"))
    assert messages(repo, "table-columns") == []


def test_relation_contradiction_conflict_vs_support(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "U2")["related"] = {"strengthens": ["U8"]}
        rule(doc, "U8")["related"] = {"conflicts_with": ["U2"]}

    edit("data/rules.yaml", seed)
    msgs = messages(repo, "relation-contradictions")
    assert any("U2 and U8 conflict and also support each other" in m for m in msgs)


def test_relation_contradiction_mutual_dependency(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "U2")["related"] = {"depends_on": ["U8"]}
        rule(doc, "U8")["related"] = {"depends_on": ["U2"]}

    edit("data/rules.yaml", seed)
    assert any(
        "U2 and U8 depend on each other" in m
        for m in messages(repo, "relation-contradictions")
    )


def test_relation_self_reference(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml", lambda d: rule(d, "U2")["related"].update(depends_on=["U2"])
    )
    assert any(
        "U2 lists itself" in m for m in messages(repo, "relation-contradictions")
    )


def test_missing_inverse_is_allowed(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "U2")["related"] = {"strengthens": ["U8"]}
        rule(doc, "U8")["related"] = {}

    edit("data/rules.yaml", seed)
    assert messages(repo, "relation-contradictions") == []


def test_primary_source_missing(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "U1")["sources"] = ["wikipedia-andon"]

    edit("data/rules.yaml", seed)
    assert any(
        "U1 has no primary source" in m for m in messages(repo, "primary-source")
    )


def test_known_exception_is_allowed(repo: Path, edit: Edit) -> None:
    edit("data/meta.yaml", lambda d: d["known_exceptions"].clear())
    assert any(
        "C15 has no primary source" in m for m in messages(repo, "primary-source")
    )


def test_c_rule_without_counterexample(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        del rule(doc, "C1")["counterexample"]

    edit("data/rules.yaml", seed)
    assert any(
        "C1 is a C-rule without a counterexample" in m
        for m in messages(repo, "counterexamples")
    )


def test_k_rule_names_too_few_rules(repo: Path, edit: Edit) -> None:
    edit("data/conflicts.yaml", lambda d: d[0].update(rules=["U7"]))
    assert any(
        "K1 names fewer than 2 rules" in m for m in messages(repo, "conflict-rules")
    )


def test_k_rule_names_unknown_rule(repo: Path, edit: Edit) -> None:
    edit("data/conflicts.yaml", lambda d: d[0].update(rules=["U7", "U777"]))
    assert any(
        "K1 names unknown rule U777" in m for m in messages(repo, "conflict-rules")
    )


def test_category_membership_mismatch(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "U1").update(category="B"))
    assert any(
        "U1 is listed in category A but has category B" in m
        for m in messages(repo, "category-membership")
    )


def test_quick_view_count(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        for key in ("A", "B", "C", "D", "E"):
            del doc["quick_view_questions"][key]

    edit("data/meta.yaml", seed)
    assert any("quick view has 4 questions" in m for m in messages(repo, "quick-view"))


def test_id_map_target_missing(repo: Path, edit: Edit) -> None:
    edit(
        "data/history.yaml",
        lambda d: d["id_map"].append({"old": "X1", "new": "U999", "edition": "1.0.0"}),
    )
    assert any("X1 -> U999" in m for m in messages(repo, "id-map"))


def test_unresolved_citation_in_data(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "U1").update(because="see [@no-such-source]"),
    )
    assert any(
        "[@no-such-source] does not resolve" in m for m in messages(repo, "citations")
    )


def test_unresolved_citation_in_docs(repo: Path) -> None:
    (repo / "docs" / "extra.md").write_text(
        "Claim [@missing-slug; @also-missing].\n", encoding="utf-8"
    )
    msgs = messages(repo, "citations")
    assert any("docs/extra.md" in m and "[@missing-slug]" in m for m in msgs)
    assert any("[@also-missing]" in m for m in msgs)


def test_unresolved_citation_in_paper(repo: Path) -> None:
    (repo / "paper" / "sections" / "x.md").write_text(
        "A [@nope, p. 3].\n", encoding="utf-8"
    )
    assert any("paper/sections/x.md" in m for m in messages(repo, "citations"))


def test_citation_in_code_is_ignored(repo: Path) -> None:
    text = "Use `[@slug]` inline.\n\n```\n[@fenced-slug]\n```\n"
    (repo / "docs" / "extra.md").write_text(text, encoding="utf-8")
    assert messages(repo, "citations") == []


def test_duplicate_slug_across_registries(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        doc.append(
            {
                "slug": "wikipedia-andon",
                "title": "Dup",
                "url": "https://example.org/other-url",
                "kind": "primary",
                "paid": False,
            }
        )

    edit("paper/references-extra.yaml", seed)
    assert any(
        "is in paper/references-extra.yaml and data/sources.yaml" in m
        for m in messages(repo, "registry-unique")
    )


def test_duplicate_url_across_registries(repo: Path, edit: Edit) -> None:
    url = "https://www.rfc-editor.org/rfc/rfc2119"

    def seed(doc: Any) -> None:
        doc.append(
            {
                "slug": "dup-url",
                "title": "Dup",
                "url": url,
                "kind": "primary",
                "paid": False,
            }
        )

    edit("paper/references-extra.yaml", seed)
    assert any("URL " + url in m for m in messages(repo, "registry-unique"))


def test_schema_violation(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "U1").update(strength="MAYBE"))
    assert any("data/rules.yaml at 0/strength" in m for m in messages(repo, "schema"))


def test_schema_format_checker_is_enforced(repo: Path, edit: Edit) -> None:
    edit("data/meta.yaml", lambda d: d.update(date="2026-13-45"))
    assert any("data/meta.yaml at date" in m for m in messages(repo, "schema"))


def test_schema_covers_extra_registries(repo: Path, edit: Edit) -> None:
    edit("paper/references-extra.yaml", lambda d: d[0].update(kind="tertiary"))
    assert any("paper/references-extra.yaml" in m for m in messages(repo, "schema"))
