"""One seeded violation per integrity check (NFR-0001); each must fail clearly."""

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
        "domain-count",
        "source-used",
        "table-columns",
        "relation-contradictions",
        "inverse-complete",
        "conflicts-symmetric",
        "related-order",
        "override-agreement",
        "sources-primary-first",
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


def test_missing_inverse_is_not_a_contradiction(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "U2")["related"] = {"strengthens": ["U8"]}
        rule(doc, "U8")["related"] = {}

    edit("data/rules.yaml", seed)
    assert messages(repo, "relation-contradictions") == []


def test_missing_inverse_strengthened_by(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "U8")["related"].pop("strengthened_by"))
    msgs = messages(repo, "inverse-complete")
    assert "U2 strengthens U8, but U8 does not list U2 under strengthened_by" in msgs


def test_missing_inverse_strengthens(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "R2")["related"].pop("strengthens"))
    msgs = messages(repo, "inverse-complete")
    assert "R1 strengthened_by R2, but R2 does not list R1 under strengthens" in msgs


def test_missing_inverse_checked_by(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "U35")["related"].pop("checked_by"))
    msgs = messages(repo, "inverse-complete")
    assert "U13 checks U35, but U35 does not list U13 under checked_by" in msgs


def test_conflicts_one_sided(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "U35")["related"].pop("conflicts_with"))
    msgs = messages(repo, "conflicts-symmetric")
    assert msgs == [
        "U23 conflicts_with U35, but U35 does not list U23 under conflicts_with"
    ]


def test_related_key_order(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        r = rule(doc, "U23")
        r["related"] = {"conflicts_with": ["U35"], "depends_on": ["U22"]}

    edit("data/rules.yaml", seed)
    assert any(
        "U23 related keys ['conflicts_with', 'depends_on'] are not in "
        "relation_types order" in m
        for m in messages(repo, "related-order")
    )


def test_related_id_order(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "R1")["related"].update(
            strengthened_by=["R2", "C13", "U6", "U34"]
        ),
    )
    assert any(
        "R1 strengthened_by ['R2', 'C13', 'U6', 'U34'] is not in ID order "
        "['U6', 'U34', 'R2', 'C13']" in m
        for m in messages(repo, "related-order")
    )


def test_override_disagrees_with_related(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "U47").update(
            related_text="strengthens U10, U18, U20; conflicts with accountability"
        ),
    )
    msgs = messages(repo, "override-agreement")
    assert any("U47 related_text names" in m and "'U57'" in m for m in msgs)


def test_override_ignores_non_rule_text(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "U49").update(
            related_text="depends on U2; conflicts with U32, U33, C10 (see K6, K7)"
        ),
    )
    assert messages(repo, "override-agreement") == []


def test_secondary_source_before_primary(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "U18")["sources"].reverse())
    assert messages(repo, "sources-primary-first") == [
        "U18 sources lists a secondary source before a primary one"
    ]


def test_management_secondary_source_before_primary(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "R4")["management"]["sources"].reverse())
    assert messages(repo, "sources-primary-first") == [
        "R4 management.sources lists a secondary source before a primary one"
    ]


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


def test_domain_count_mismatch(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        sec = next(s for s in doc["sections"] if s["key"] == "domain_index")
        sec["intro"] = sec["intro"].replace("130 domains", "131 domains")

    edit("data/meta.yaml", seed)
    msgs = messages(repo, "domain-count")
    assert any("states 131 domains" in m and "has 130 domains" in m for m in msgs)


def test_contradiction_found_when_edges_run_from_larger_to_smaller_id(
    repo: Path, edit: Edit
) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "U5")["related"] = {"conflicts_with": ["U2"], "strengthens": ["U2"]}
        rule(doc, "U2")["related"] = {}

    edit("data/rules.yaml", seed)
    msgs = messages(repo, "relation-contradictions")
    assert len([m for m in msgs if "U2 and U5 conflict" in m]) == 1


def test_domain_count_without_domain_index_section(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        for sec in doc["sections"]:
            if sec["key"] == "domain_index":
                sec["key"] = "renamed"

    edit("data/meta.yaml", seed)
    assert any("no 'N domains" in m for m in messages(repo, "domain-count"))


def test_yaml_syntax_error_is_a_finding(repo: Path) -> None:
    (repo / "data" / "glossary.yaml").write_text("a: [unclosed\n", encoding="utf-8")
    findings = run_checks(repo)
    assert [f.check for f in findings] == ["load"]
    assert "glossary.yaml" in findings[0].message


def test_missing_schema_is_a_finding(repo: Path) -> None:
    (repo / "schema" / "rules.schema.json").unlink()
    msgs = messages(repo, "schema")
    assert any("rules.schema.json" in m for m in msgs)


def test_missing_data_file_is_a_finding(repo: Path) -> None:
    (repo / "data" / "rules.yaml").unlink()
    findings = run_checks(repo)
    assert findings and findings[0].check == "load"
    assert "rules.yaml" in findings[0].message


def test_missing_sources_registry_is_an_error(repo: Path) -> None:
    (repo / "data" / "sources.yaml").unlink()
    findings = run_checks(repo)
    assert findings and "sources.yaml" in findings[0].message
