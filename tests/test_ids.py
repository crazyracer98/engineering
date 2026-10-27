"""Rule IDs: the edition-9 -> P1-P83 map, category order, prefix-generic
matching and class-from-field (plan item D4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from taxonomy.ids import MAX_RANGE, expand_ids, id_finder, id_key, link_ids
from taxonomy.load import load_dataset, load_registry
from taxonomy.model import CLASS_LETTER
from taxonomy.render_markdown import _link_block, render_chapters
from taxonomy.render_paper import _Paper
from tests.conftest import REPO
from tests.test_checks import Edit, messages, rule

ID_MAP = REPO / "sources/import/id-map.yaml"


def _entries() -> list[dict[str, str]]:
    entries = YAML().load(ID_MAP.read_text(encoding="utf-8"))
    return [{"old": str(e["old"]), "new": str(e["new"])} for e in entries]


def test_id_map_is_a_bijection_over_all_rules() -> None:
    entries = _entries()
    assert len(entries) == 83
    olds = [e["old"] for e in entries]
    news = [e["new"] for e in entries]
    assert len(set(olds)) == 83
    assert len(set(news)) == 83
    # Every edition-9 rule ID is present: U1-U58, R1-R9 and C1-C16.
    expected = (
        {f"U{n}" for n in range(1, 59)}
        | {f"R{n}" for n in range(1, 10)}
        | {f"C{n}" for n in range(1, 17)}
    )
    assert set(olds) == expected
    assert set(news) == {f"P{n}" for n in range(1, 84)}
    # Listed in new-ID order.
    assert news == [f"P{n}" for n in range(1, 84)]


def test_new_ids_follow_category_order() -> None:
    ds = load_dataset(REPO)
    news = [e["new"] for e in _entries()]
    # The rules of 1.0.0 (a later rule gets the next free number, not a place
    # in this order) run through the categories A to I as P1 to P83.
    flat = [rid for cat in ds.categories for rid in cat["rules"] if rid in news]
    assert flat == news
    by_id = ds.rule_by_id()
    categories = [by_id[rid]["category"] for rid in flat]
    assert categories == sorted(categories)
    assert [r["id"] for r in ds.rules if r["id"] in news] == news


def test_history_id_map_stays_empty() -> None:
    ds = load_dataset(REPO)
    assert ds.history["id_map"] == []
    assert not any("former_id" in r for r in ds.rules)


def test_id_key_orders_by_prefix_list_then_number() -> None:
    ids = ["K2", "P10", "P9", "K1"]
    assert sorted(ids, key=lambda i: id_key(i, ["P", "K"])) == [
        "P9",
        "P10",
        "K1",
        "K2",
    ]
    assert sorted(ids, key=lambda i: id_key(i, ["K", "P"]))[0] == "K1"
    assert id_key("X1", ["P", "K"]) == (2, 0)


def test_id_finder_does_not_match_inside_words_or_urls() -> None:
    found = id_finder(["P", "K"])
    assert [m.group(0) for m in found.finditer("P1, (K2) and P33.")] == [
        "P1",
        "K2",
        "P33",
    ]
    assert not found.findall("see ISO-P1 or /P1 or #P1 or XP1 or P01")
    # The end of a hyphen-written range is found; a hyphenated word's tail is not.
    assert [m.group(0) for m in found.finditer("P3-P5 and ISO-P1")] == ["P3", "P5"]


def _href(rid: str) -> str:
    return f"x.md#{rid.lower()}"


def test_link_ids_links_p_and_k_ids() -> None:
    out = link_ids("P1 beats K2.", {"P1", "K2"}, ["P", "K"], _href)
    assert out == "[P1](x.md#p1) beats [K2](x.md#k2)."
    assert link_ids("P99 stays", {"P1"}, ["P", "K"], _href) == "P99 stays"


def test_link_ids_keeps_a_range_and_links_both_ends() -> None:
    known = {"P3", "P4", "P5", "K1", "K2", "K3"}
    for dash in ("–", "-", " – ", " - "):
        out = link_ids(f"see P3{dash}P5 now", known, ["P", "K"], _href)
        assert out == "see [P3](x.md#p3)–[P5](x.md#p5) now", dash
    assert link_ids("K1-K3", known, ["P", "K"], _href) == (
        "[K1](x.md#k1)–[K3](x.md#k3)"
    )
    # Not expanded: P4 is in the range but is not written, so it is not linked.
    assert "P4" not in link_ids("P3–P5", known, ["P", "K"], _href)
    # The range's end links even when a hyphen precedes it.
    assert link_ids("P3, P4-P5", known, ["P", "K"], _href) == (
        "[P3](x.md#p3), [P4](x.md#p4)–[P5](x.md#p5)"
    )


def test_link_ids_leaves_non_ranges_alone() -> None:
    known = {"P3", "P4", "K2"}
    # Mixed prefixes and descending pairs are not ranges: each end links alone,
    # as written (no dash normalisation).
    assert link_ids("P3–K2", known, ["P", "K"], _href) == (
        "[P3](x.md#p3)–[K2](x.md#k2)"
    )
    assert link_ids("P4-P3", known, ["P", "K"], _href) == (
        "[P4](x.md#p4)-[P3](x.md#p3)"
    )
    # An unknown end: the known end links, nothing is invented.
    assert link_ids("P3–P9", known, ["P", "K"], _href) == "[P3](x.md#p3)–P9"


def test_expand_ids_expands_ranges_for_the_agreement_check() -> None:
    assert expand_ids("P3-P5, K1 and P7 – P8", ["P", "K"]) == [
        "P3",
        "P4",
        "P5",
        "K1",
        "P7",
        "P8",
    ]
    assert expand_ids("P5-P3 and ISO-P1", ["P", "K"]) == ["P5", "P3"]


def test_chapter_linking_covers_p_k_and_ranges() -> None:
    ds = load_dataset(REPO)
    lines = _link_block("P1, K3 and P3-P5.", ds, 5)
    assert lines == [
        "[P1](07-rules.md#p1), [K3](08-conflicts.md#k3) and "
        "[P3](07-rules.md#p3)–[P5](07-rules.md#p5)."
    ]
    here = _link_block("P1 and K3", ds, 7)[0]
    assert here == "[P1](#p1) and [K3](08-conflicts.md#k3)"
    # The IDs paragraph of the reading guide keeps "P1–P83" and "K1–K8".
    text = _link_block("(P1–P83) and K1–K8", ds, 1)[0]
    assert "P2" not in text and "[P83](07-rules.md#p83)" in text
    assert "[K8](08-conflicts.md#k8)" in text


def test_paper_links_p_k_and_ranges() -> None:
    ds = load_dataset(REPO)
    out = _Paper(ds).link_ids("P1, K3, P3–P4")
    assert out == "[P1](#p1), [K3](#k3), [P3](#p3)–[P4](#p4)"


def test_class_comes_from_the_field_not_the_id(repo: Path, edit: Edit) -> None:
    # P1 is universal. Making it conditional (and nothing else) makes it a
    # conditional rule without a counterexample, whatever its ID letter is.
    edit("data/rules.yaml", lambda d: rule(d, "P1").update({"class": "conditional"}))
    assert any(
        "P1 is a conditional (C) rule without a counterexample" in m
        for m in messages(repo, "counterexamples")
    )
    # Rendering takes the class from the field as well.
    ds = load_dataset(repo)
    chapters = render_chapters(ds, load_registry(repo))
    assert "| conditional (C), category A:" in chapters["07-rules.md"]


def test_rendering_shows_class_and_category_next_to_the_id() -> None:
    ds = load_dataset(REPO)
    chapters = render_chapters(ds, load_registry(REPO))
    assert "| [P1](#p1) | universal (U), category A: " in chapters["07-rules.md"]
    paper = _Paper(ds).rule_card(ds.rule_by_id()["P1"])
    assert "universal (U) · category A" in paper


def test_expand_ids_caps_a_range() -> None:
    assert len(expand_ids(f"P1-P{MAX_RANGE}", ["P"])) == MAX_RANGE
    with pytest.raises(ValueError, match="limit"):
        expand_ids(f"P1-P{MAX_RANGE + 1}", ["P"])


def test_ids_after_a_digit_hyphen_are_not_linked() -> None:
    known = {"P1", "P3", "P5"}
    for text in ("ISO27001-P1", "2024-P1", "ISO-P1", "x9-P1"):
        assert link_ids(text, known, ["P"], _href) == text, text
        assert expand_ids(text, ["P"]) == [], text
        assert not id_finder(["P"]).findall(text), text
    # A whole ID before the hyphen keeps its range / pair behaviour.
    assert [m.group(0) for m in id_finder(["P"]).finditer("P3-P5")] == ["P3", "P5"]
    assert link_ids("P3-P5", known, ["P"], _href) == "[P3](x.md#p3)–[P5](x.md#p5)"


def test_id_key_ignores_prefix_order_duplicates() -> None:
    from taxonomy.ids import _key_pattern

    _key_pattern.cache_clear()
    id_key("K1", ["P", "K"])
    id_key("K1", ["K", "P"])
    id_key("K1", ["P", "K", "P"])
    assert _key_pattern.cache_info().currsize == 1
    assert id_key("K2", ["P", "K"]) == (1, 2)


def test_class_letter_covers_every_class() -> None:
    schema = json.loads((REPO / "schema/rules.schema.json").read_text("utf-8"))
    assert set(schema["items"]["properties"]["class"]["enum"]) == set(CLASS_LETTER)
