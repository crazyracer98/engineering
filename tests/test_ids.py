"""Rule IDs: the edition-9 -> P1-P83 map, category order, prefix-generic
matching and class-from-field (plan item D4)."""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

from taxonomy.ids import id_finder, id_key, link_ids
from taxonomy.load import load_dataset, load_registry
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


def _href(rid: str) -> str:
    return f"x.md#{rid.lower()}"


def test_link_ids_links_p_and_k_ids() -> None:
    out = link_ids("P1 beats K2.", {"P1", "K2"}, ["P", "K"], _href)
    assert out == "[P1](x.md#p1) beats [K2](x.md#k2)."
    assert link_ids("P99 stays", {"P1"}, ["P", "K"], _href) == "P99 stays"


def test_link_ids_links_every_id_of_a_range() -> None:
    known = {"P3", "P4", "P5", "K1", "K2", "K3"}
    for dash in ("–", "-"):
        out = link_ids(f"see P3{dash}P5 now", known, ["P", "K"], _href)
        assert out == ("see [P3](x.md#p3), [P4](x.md#p4), [P5](x.md#p5) now"), dash
    out = link_ids("K1-K3", known, ["P", "K"], _href)
    assert out.count("](") == 3


def test_link_ids_leaves_non_ranges_alone() -> None:
    known = {"P3", "P4", "K2"}
    # Mixed prefixes and descending pairs are not ranges: each end links alone.
    assert link_ids("P3–K2", known, ["P", "K"], _href) == (
        "[P3](x.md#p3)–[K2](x.md#k2)"
    )
    assert link_ids("P4–P3", known, ["P", "K"], _href) == (
        "[P4](x.md#p4)–[P3](x.md#p3)"
    )
    # A gap that is not a known ID: the ends link, nothing is invented.
    assert link_ids("P3–P9", known, ["P", "K"], _href) == "[P3](x.md#p3)–P9"


def test_chapter_linking_covers_p_k_and_ranges() -> None:
    ds = load_dataset(REPO)
    lines = _link_block("P1, K3 and P3-P5.", ds, 5)
    assert lines == [
        "[P1](07-rules.md#p1), [K3](08-conflicts.md#k3) and "
        "[P3](07-rules.md#p3), [P4](07-rules.md#p4), [P5](07-rules.md#p5)."
    ]
    here = _link_block("P1 and K3", ds, 7)[0]
    assert here == "[P1](#p1) and [K3](08-conflicts.md#k3)"


def test_paper_links_p_k_and_ranges() -> None:
    ds = load_dataset(REPO)
    out = _Paper(ds).link_ids("P1, K3, P3–P4")
    assert out == "[P1](#p1), [K3](#k3), [P3](#p3), [P4](#p4)"


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
