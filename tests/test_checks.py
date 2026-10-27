"""One seeded violation per integrity check (NFR-0001); each must fail clearly."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from taxonomy import cli
from taxonomy.load import load_dataset, load_registry
from taxonomy.render_markdown import render_single
from taxonomy.validate import CHECKS, Finding, parse_id_list, run_checks

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
        "management-count",
        "slug-references",
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
        "checker-level-rule",
        "domain-anchors",
        "quote-passages",
    }
    assert set(CHECKS) == names


def test_finding_str() -> None:
    assert str(Finding("x", "y")) == "[x] y"


def test_unique_ids(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        doc[1]["id"] = doc[0]["id"]

    edit("data/rules.yaml", seed)
    assert any("duplicate ID P1" in m for m in messages(repo, "unique-ids"))


def test_related_target_missing(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "P1")["related"]["strengthens"].append("P999"),
    )
    assert any(
        "P1 strengthens P999: no such rule" in m
        for m in messages(repo, "related-targets")
    )


def test_id_reference_missing(repo: Path, edit: Edit) -> None:
    edit("data/categories.yaml", lambda d: d[0]["rules"].append("P998"))
    assert any(
        "category A names unknown rule P998" in m
        for m in messages(repo, "id-references")
    )


def test_rule_in_no_domain(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        for d in doc["domains"]:
            if "P1" in d["rules"]:
                d["rules"].remove("P1")
                if not d["rules"]:
                    d["rules"].append("P2")

    edit("data/domains.yaml", seed)
    assert any("P1 appears in no domain" in m for m in messages(repo, "rule-in-domain"))


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


def test_pipe_in_a_cell_is_escaped_not_a_column(repo: Path, edit: Edit) -> None:
    edit("data/glossary.yaml", lambda d: d["error"].update(meaning="a | b"))
    assert messages(repo, "table-columns") == []
    md = render_single(load_dataset(repo), load_registry(repo))
    assert "a \\| b" in md


def test_table_column_count(repo: Path, edit: Edit) -> None:
    # A header with one column fewer than its rows: the table cannot be built.
    edit("data/meta.yaml", lambda d: d["tables"]["glossary"].pop())
    found = messages(repo, "table-columns")
    assert any("table row has 3 cells, header has 2" in m for m in found), found


def test_escaped_pipe_is_not_a_column(repo: Path, edit: Edit) -> None:
    edit("data/glossary.yaml", lambda d: d["error"].update(meaning="a \\| b"))
    assert messages(repo, "table-columns") == []


def test_pipe_in_code_span_is_not_a_column(repo: Path, edit: Edit) -> None:
    edit("data/glossary.yaml", lambda d: d["error"].update(meaning="use `a | b` here"))
    assert messages(repo, "table-columns") == []


def test_checker_level_rule_renamed(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P56").update(name="Something else"))
    msgs = messages(repo, "checker-level-rule")
    assert len(msgs) == 1 and "P56" in msgs[0] and "Something else" in msgs[0]


def test_checker_level_rule_missing(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P56").update(id="P9999"))
    assert any("no such rule" in m for m in messages(repo, "checker-level-rule"))


def _first_branch(doc: Any) -> tuple[str, dict[str, Any]]:
    row = doc["domains"][0]
    return row["branch"], row


def test_domain_anchor_collision(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        branch, row = _first_branch(doc)
        twin = dict(row)
        row["domain"], twin["domain"] = "Same name", "Same-name"
        doc["domains"].append({**twin, "branch": branch})

    edit("data/domains.yaml", seed)
    msgs = messages(repo, "domain-anchors")
    assert any("share the anchor 'same-name'" in m for m in msgs), msgs


def test_domain_anchor_empty(repo: Path, edit: Edit) -> None:
    edit("data/domains.yaml", lambda d: _first_branch(d)[1].update(domain="***"))
    assert any("empty anchor" in m for m in messages(repo, "domain-anchors"))


def test_quote_without_scorable_part(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        q = next(q for q in doc if q.get("source") and not q.get("placeholder"))
        q["text"] = 'only "a b ... c d" here'

    edit("data/quotes.yaml", seed)
    msgs = messages(repo, "quote-passages")
    assert len(msgs) == 1 and "no scorable quoted passage" in msgs[0], msgs


def test_cross_reference_quote_is_not_a_passage(repo: Path) -> None:
    assert messages(repo, "quote-passages") == []


def test_case_quote_needs_four_alphanumerics(repo: Path, edit: Edit) -> None:
    for path in (repo / "data" / "learn").glob("*/*.yaml"):
        path.write_text("[]\n", encoding="utf-8")
    shutil.copytree(
        Path(__file__).resolve().parent / "fixtures" / "learn",
        repo / "data" / "learn",
        dirs_exist_ok=True,
    )
    assert messages(repo, "quote-passages") == []
    edit("data/learn/cases/1.yaml", lambda d: d[0]["quotes"][0].update(text="-- ab --"))
    msgs = messages(repo, "quote-passages")
    assert len(msgs) == 1 and "fewer than 4" in msgs[0], msgs


def test_id_range_over_the_cap_is_a_finding(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P2").update(related_text="P1-P9999"))
    assert any("limit" in m for m in messages(repo, "override-agreement"))


def test_relation_contradiction_conflict_vs_support(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "P2")["related"] = {"strengthens": ["P56"]}
        rule(doc, "P56")["related"] = {"conflicts_with": ["P2"]}

    edit("data/rules.yaml", seed)
    msgs = messages(repo, "relation-contradictions")
    assert any("P2 and P56 conflict and also support each other" in m for m in msgs)


def test_relation_contradiction_mutual_dependency(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "P2")["related"] = {"depends_on": ["P56"]}
        rule(doc, "P56")["related"] = {"depends_on": ["P2"]}

    edit("data/rules.yaml", seed)
    assert any(
        "P2 and P56 depend on each other" in m
        for m in messages(repo, "relation-contradictions")
    )


def test_relation_self_reference(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml", lambda d: rule(d, "P2")["related"].update(depends_on=["P2"])
    )
    assert any(
        "P2 lists itself" in m for m in messages(repo, "relation-contradictions")
    )


def test_missing_inverse_is_not_a_contradiction(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "P2")["related"] = {"strengthens": ["P56"]}
        rule(doc, "P56")["related"] = {}

    edit("data/rules.yaml", seed)
    assert messages(repo, "relation-contradictions") == []


def test_missing_inverse_strengthened_by(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P56")["related"].pop("strengthened_by"))
    msgs = messages(repo, "inverse-complete")
    assert "P2 strengthens P56, but P56 does not list P2 under strengthened_by" in msgs


def test_missing_inverse_strengthens(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P46")["related"].pop("strengthens"))
    msgs = messages(repo, "inverse-complete")
    assert (
        "P45 strengthened_by P46, but P46 does not list P45 under strengthens" in msgs
    )


def test_missing_inverse_checked_by(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P73")["related"].pop("checked_by"))
    msgs = messages(repo, "inverse-complete")
    assert "P70 checks P73, but P73 does not list P70 under checked_by" in msgs


def test_conflicts_one_sided(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P73")["related"].pop("conflicts_with"))
    msgs = messages(repo, "conflicts-symmetric")
    assert msgs == [
        "P83 conflicts_with P73, but P73 does not list P83 under conflicts_with"
    ]


def test_related_key_order(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        r = rule(doc, "P83")
        r["related"] = {"conflicts_with": ["P73"], "depends_on": ["P11"]}

    edit("data/rules.yaml", seed)
    assert any(
        "P83 related keys ['conflicts_with', 'depends_on'] are not in "
        "relation_types order" in m
        for m in messages(repo, "related-order")
    )


def test_related_id_order(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "P45")["related"].update(
            strengthened_by=["P46", "P34", "P22", "P41"]
        ),
    )
    assert any(
        "P45 strengthened_by ['P46', 'P34', 'P22', 'P41'] is not in ID order "
        "['P22', 'P34', 'P41', 'P46']" in m
        for m in messages(repo, "related-order")
    )


def test_override_disagrees_with_related(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "P5").update(
            related_text="strengthens P80, P82, P4; conflicts with accountability"
        ),
    )
    msgs = messages(repo, "override-agreement")
    assert any("P5 related_text names" in m and "'P63'" in m for m in msgs)


def test_override_ignores_non_rule_text(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "P7").update(
            related_text="depends on P2; conflicts with P71, P72, P61 (see K6, K7)"
        ),
    )
    assert messages(repo, "override-agreement") == []


def test_secondary_source_before_primary(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P82")["sources"].reverse())
    assert messages(repo, "sources-primary-first") == [
        "P82 sources lists a secondary source before a primary one"
    ]


def test_management_secondary_source_before_primary(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P68")["management"]["sources"].reverse())
    assert messages(repo, "sources-primary-first") == [
        "P68 management.sources lists a secondary source before a primary one"
    ]


def test_primary_source_missing(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        rule(doc, "P1")["sources"] = ["wikipedia-andon"]

    edit("data/rules.yaml", seed)
    assert any(
        "P1 has no primary source" in m for m in messages(repo, "primary-source")
    )


def test_known_exception_is_allowed(repo: Path, edit: Edit) -> None:
    edit("data/meta.yaml", lambda d: d["known_exceptions"].clear())
    assert any(
        "P53 has no primary source" in m for m in messages(repo, "primary-source")
    )


def test_c_rule_without_counterexample(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        del rule(doc, "P60")["counterexample"]

    edit("data/rules.yaml", seed)
    assert any(
        "P60 is a conditional (C) rule without a counterexample" in m
        for m in messages(repo, "counterexamples")
    )


def test_k_rule_names_too_few_rules(repo: Path, edit: Edit) -> None:
    edit("data/conflicts.yaml", lambda d: d[0].update(rules=["P23"]))
    assert any(
        "K1 names fewer than 2 rules" in m for m in messages(repo, "conflict-rules")
    )


def test_k_rule_names_unknown_rule(repo: Path, edit: Edit) -> None:
    edit("data/conflicts.yaml", lambda d: d[0].update(rules=["P23", "P777"]))
    assert any(
        "K1 names unknown rule P777" in m for m in messages(repo, "conflict-rules")
    )


def test_category_membership_mismatch(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P1").update(category="B"))
    assert any(
        "P1 is listed in category A but has category B" in m
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
        lambda d: d["id_map"].append({"old": "X1", "new": "P999", "edition": "1.0.0"}),
    )
    assert any("X1 -> P999" in m for m in messages(repo, "id-map"))


def test_unresolved_citation_in_data(repo: Path, edit: Edit) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "P1").update(because="see [@no-such-source]"),
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
    edit("data/rules.yaml", lambda d: rule(d, "P1").update(strength="MAYBE"))
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
        rule(doc, "P55")["related"] = {"conflicts_with": ["P2"], "strengthens": ["P2"]}
        rule(doc, "P2")["related"] = {}

    edit("data/rules.yaml", seed)
    msgs = messages(repo, "relation-contradictions")
    assert len([m for m in msgs if "P2 and P55 conflict" in m]) == 1


def test_domain_count_without_domain_index_section(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        for sec in doc["sections"]:
            if sec["key"] == "domain_index":
                sec["key"] = "renamed"

    edit("data/meta.yaml", seed)
    assert any("no 'N domains" in m for m in messages(repo, "domain-count"))


def test_yaml_syntax_error_is_a_finding(repo: Path, edit: Edit) -> None:
    edit("data/rules.yaml", lambda d: rule(d, "P1").update(strength="MAYBE"))
    (repo / "data" / "glossary.yaml").write_text("a: [unclosed\n", encoding="utf-8")
    findings = run_checks(repo)
    assert findings[0].check == "load"
    assert "glossary.yaml" in findings[0].message
    schema = [f.message for f in findings if f.check == "schema"]
    assert any(m.startswith("data/glossary.yaml cannot be loaded") for m in schema)
    assert any("data/rules.yaml at 0/strength" in m for m in schema)
    assert {f.check for f in findings} == {"load", "schema"}


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


def test_slug_reference_typo(
    repo: Path, edit: Edit, capsys: pytest.CaptureFixture[str]
) -> None:
    edit(
        "data/rules.yaml",
        lambda d: rule(d, "P1")["sources"].__setitem__(0, "nspe-typo"),
    )
    assert messages(repo, "slug-references") == [
        "data/rules.yaml: P1 sources names unknown source slug 'nspe-typo'"
    ]
    assert cli.main(["--root", str(repo), "build"]) == 1
    err = capsys.readouterr().err
    assert "unknown source slug 'nspe-typo'" in err
    assert "data/rules.yaml: P1 sources" in err
    assert "Traceback" not in err


def test_schema_findings_are_per_file(repo: Path, edit: Edit) -> None:
    (repo / "schema" / "glossary.schema.json").unlink()
    edit("data/rules.yaml", lambda d: rule(d, "P1").update(strength="MAYBE"))
    msgs = messages(repo, "schema")
    assert any(
        "schema/glossary.schema.json (for data/glossary.yaml)" in m for m in msgs
    )
    assert any("data/rules.yaml at 0/strength" in m for m in msgs)
    assert not any("could not run" in m for m in msgs)


def _scope(doc: Any, old: str, new: str) -> None:
    item = next(h for h in doc["how_to_read"] if h["key"] == "scope")
    assert old in item["text"]
    item["text"] = item["text"].replace(old, new)


def test_management_count_wrong_n(repo: Path, edit: Edit) -> None:
    edit("data/meta.yaml", lambda d: _scope(d, "67 of the 83", "66 of the 83"))
    assert any(
        "states section 10 has 66 of 83" in m and "has 67 of 83" in m
        for m in messages(repo, "management-count")
    )


def test_management_count_wrong_id_list(repo: Path, edit: Edit) -> None:
    edit(
        "data/meta.yaml",
        lambda d: _scope(
            d,
            "P35, P43,",
            "P35, P16,",
        ),
    )
    assert messages(repo, "management-count") == [
        "meta's list of rules without a management form has extra ['P16'] "
        "and misses ['P43']"
    ]


def test_management_count_sentence_missing(repo: Path, edit: Edit) -> None:
    edit("data/meta.yaml", lambda d: _scope(d, "Section 10 states", "Section 10 has"))
    assert any(
        "has no 'Section 10 states" in m for m in messages(repo, "management-count")
    )


def test_parse_id_list_is_prefix_generic() -> None:
    assert parse_id_list("P1–P3, P9, P10-P11", ["P", "K"]) == [
        "P1",
        "P2",
        "P3",
        "P9",
        "P10",
        "P11",
    ]
    with pytest.raises(ValueError, match="within one prefix"):
        parse_id_list("P1–K3", ["P", "K"])
    with pytest.raises(ValueError, match="not a rule ID"):
        parse_id_list("U1", ["P"])


def test_source_cited_only_by_itself_is_unused(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        doc.append(
            {
                "slug": "self-cited",
                "title": "Self",
                "url": "https://example.org/self",
                "kind": "primary",
                "paid": False,
                "notes": "see [@self-cited]",
            }
        )

    edit("data/sources.yaml", seed)
    assert any("self-cited" in m for m in messages(repo, "source-used"))
