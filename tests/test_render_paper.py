"""The paper build: CSL-JSON, the assembled Markdown, Pandoc failures and the PDF."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from taxonomy import render_paper
from taxonomy.load import load_dataset, load_registry
from taxonomy.render_paper import (
    assemble,
    csl_json,
    csl_type,
    method_markdown,
    paper_sections,
    write_csl_json,
)

REPO = Path(__file__).resolve().parent.parent
Edit = Callable[[str, Callable[[Any], None]], None]


def test_csl_json_has_every_slug_of_all_three_registries(
    repo: Path, tmp_path: Path
) -> None:
    registry = load_registry(repo)
    out = tmp_path / "references.json"
    write_csl_json(repo, out)
    items = json.loads(out.read_text(encoding="utf-8"))
    assert {i["id"] for i in items} == set(registry)
    # one slug from each registry file
    assert {
        "epcland-checking-design",  # data/sources.yaml
        "iso-iec-ieee-15288-2023",  # paper/references-extra.yaml
    } <= set(registry)
    own = {x["slug"] for x in load_dataset(repo).sources} | {"iso-iec-ieee-15288-2023"}
    assert set(registry) - own, "docs/methodology-references.yaml adds sources too"


def test_csl_item_fields(repo: Path) -> None:
    registry = load_registry(repo)
    items = {i["id"]: i for i in csl_json(registry)}
    for slug, source in registry.items():
        item = items[slug]
        assert item["title"] == source["title"]
        assert item["URL"] == source["url"]
        if source.get("year"):
            assert item["issued"] == {"date-parts": [[source["year"]]]}
        else:
            assert "issued" not in item
        if source.get("accessed"):
            y, m, d = (int(p) for p in str(source["accessed"]).split("-"))
            assert item["accessed"] == {"date-parts": [[y, m, d]]}
        if source.get("publisher"):
            assert item["publisher"] == source["publisher"]


def test_csl_type_mapping() -> None:
    def kind(url: str, notes: str | None = None) -> str:
        return csl_type({"slug": "x", "title": "t", "url": url, "notes": notes})

    assert kind("https://en.wikipedia.org/wiki/Return_period") == "webpage"
    assert (
        kind("https://www.nejm.org/doi/full/10.1056/NEJMsa0810119") == "article-journal"
    )
    assert kind("https://doi.org/10.1136/bmj.n71") == "article-journal"
    assert kind("https://example.org/a.pdf") == "report"
    assert kind("https://example.org/book", "ISBN 9781119814290") == "book"


def test_section_references_are_mapped() -> None:
    assert paper_sections("see section 6") == "see Section 4.4"
    assert paper_sections("Section 12 lists") == "Appendix E lists"
    assert paper_sections("in sections 1 and 12.") == "in Section 4.1 and Appendix E."
    assert (
        paper_sections("sections 9,\n11 and 12")
        == "the Sources line of each rule card, Appendix D and Appendix E"
    )
    assert paper_sections("Section 4.1 stays") == "Section 4.1 stays"


def test_method_boxes_become_typst_boxes() -> None:
    text = (REPO / "docs" / "methodology.md").read_text(encoding="utf-8")
    boxes = text.count("> **Applied in this taxonomy:**")
    assert boxes >= 7
    out = method_markdown(text)
    assert not out.startswith("# Methodology")
    assert "> **Applied in this taxonomy:**" not in out
    assert out.count("#appliedbox[") == boxes
    assert out.count("**Applied in this taxonomy:**") == boxes
    assert "](history.md)" not in out
    assert "## Phase 0: Frame" in out


def test_assembled_markdown_structure(repo: Path) -> None:
    md = assemble(repo)
    ds = load_dataset(repo)
    order = [
        "# Abstract",
        "# Introduction",
        "# Related work",
        "# Method {#sec-method}",
        "# The taxonomy {#sec-taxonomy}",
        "## Master rule",
        "## Overview and quick view",
        "## Rigor matrix",
        "## Rules by category",
        "# Conflict rules and the analogy map",
        "# Discussion",
        "# Conclusion",
        "#show: appendix",
        "# Glossary",
        "# Domain index",
        "# Management form of each rule",
        "# Direct quotes",
        "# Limits and source quality",
        "# References",
    ]
    positions = [md.index(heading) for heading in order]
    assert positions == sorted(positions), "sections out of order"

    for rule in ds.rules:
        rid = rule["id"]
        assert f"{{#{rid.lower()} .unnumbered}}" in md, rid
        assert f"#### {rid}. {rule['name']}" in md
    for k in ds.conflicts:
        assert f"### {k['id']} {{#{k['id'].lower()} .unnumbered}}" in md
    assert md.count("#rulecard[") == len(ds.rules) + len(ds.conflicts)
    for label in ("IF", "THEN", "BECAUSE", "Check", "Violation", "Related", "Sources"):
        assert f"\n{label}\n:   " in md

    # the wide tables are not used for rules, and citations stay for citeproc
    assert "| Rule | Name |" not in md
    assert re.search(r"\[@[a-z0-9-]+", md)
    assert "](https://" not in md.split("# Glossary", 1)[1].split("# References", 1)[0]


def test_placeholder_quotes_are_skipped_and_see_rows_stay(repo: Path) -> None:
    md = assemble(repo)
    ds = load_dataset(repo)
    placeholders = [q for q in ds.quotes if q.get("placeholder")]
    assert placeholders
    quotes = md.split("# Direct quotes", 1)[1].split("# Limits", 1)[0]
    for q in placeholders:
        assert f"**{q['id']}:" not in quotes
    assert "no quote checked" not in md
    see = [q for q in ds.quotes if q["text"].startswith("see ")]
    assert see and all(f"**{q['id']}:" in quotes for q in see)


def test_limits_appendix_carries_limits_and_source_quality(repo: Path) -> None:
    md = assemble(repo)
    appendix = md.split("# Limits and source quality", 1)[1]
    assert "## Limits" in appendix and "## Source quality" in appendix
    assert "Paid documents" in appendix
    assert "garbled table extraction" in appendix


def test_edition_must_match_metadata(repo: Path, edit: Edit) -> None:
    def bump(doc: Any) -> None:
        doc["edition"] = "9.9.9"

    edit("paper/metadata.yaml", bump)
    with pytest.raises(ValueError, match="edition"):
        assemble(repo)


def test_pandoc_fails_on_missing_citation(tmp_path: Path) -> None:
    refs = tmp_path / "references.json"
    refs.write_text("[]", encoding="utf-8")
    md = tmp_path / "t.md"
    md.write_text("Claim [@no-such-source].\n", encoding="utf-8")
    meta = {
        "title": "T",
        "author": "A",
        "date": "2026-10-14",
        "keywords": ["k"],
    }
    with pytest.raises(RuntimeError, match="no-such-source"):
        render_paper.run_pandoc(
            md,
            refs,
            REPO / render_paper.CSL_RELATIVE,
            REPO / render_paper.TEMPLATE_RELATIVE,
            tmp_path / "t.typ",
            render_paper.pandoc_variables(meta),
        )


@pytest.mark.slow
def test_build_real_pdf(tmp_path: Path) -> None:
    out = tmp_path / "build" / "paper.pdf"
    render_paper.build(out, root=REPO)  # raises on any Pandoc or Typst warning
    pdf = out.read_bytes()
    assert pdf.startswith(b"%PDF")
    assert b"pdfaid:part>2<" in pdf and b"pdfaid:conformance>B<" in pdf
    assert len(re.findall(rb"/Type\s*/Page(?![s\w])", pdf)) > 10
    refs = json.loads((out.with_name("references.json")).read_text(encoding="utf-8"))
    assert {i["id"] for i in refs} == set(load_registry(REPO))
    assert out.with_name("paper.md").is_file() and out.with_name("paper.typ").is_file()
    typ = out.with_name("paper.typ").read_text(encoding="utf-8")
    assert "not found" not in typ
