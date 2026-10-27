"""Renderer helpers: code-aware linking and citation scanning."""

from __future__ import annotations

from pathlib import Path

import pytest

from taxonomy import build, cli
from taxonomy.load import load_dataset, load_registry
from taxonomy.model import Source
from taxonomy.render_markdown import (
    _link_block,
    _RefLinker,
    build_sections,
    citation_slugs,
    number_citations,
    render_chapters,
    resolve_citations,
    table,
)
from tests.conftest import REPO


def test_chapter_linking_skips_inline_and_fenced_code() -> None:
    ds = load_dataset(REPO)
    text = (
        "Use `P56` and `section 6` but P56 and section 6 link.\n"
        "```\nP56 section 6\n```\nP56"
    )
    lines = _link_block(text, ds, 5)
    assert lines[0].startswith("Use `P56` and `section 6` but [P56](07-rules.md#p56)")
    assert "[section 6](06-rigor-matrix.md)" in lines[0]
    assert lines[2] == "P56 section 6"
    assert lines[4] == "[P56](07-rules.md#p56)"


def test_chapter_linking_skips_links_with_balanced_parentheses() -> None:
    ds = load_dataset(REPO)
    line = "[W](https://e.org/P1_(x)) and [A \\[P2\\]](<https://e.org/P3_(>) P4"
    out = _link_block(line, ds, 5)[0]
    assert out.startswith(
        "[W](https://e.org/P1_(x)) and [A \\[P2\\]](<https://e.org/P3_(>) "
    )
    assert out.endswith("[P4](07-rules.md#p4)")


def test_table_escapes_pipes_in_cells() -> None:
    out = table(["a", "b"], [["x|y", "already \\| escaped"]])
    assert out.splitlines()[2] == "| x\\|y | already \\| escaped |"
    assert out.splitlines()[0] == "| a | b |"


def test_titles_and_urls_are_escaped() -> None:
    reg: dict[str, Source] = {
        "s": {
            "slug": "s",
            "title": "A_b *c* [d] <e> `f` \\g",
            "url": "https://e.org/x y(1)",
            "kind": "primary",
            "paid": False,
        },
        "u": {
            "slug": "u",
            "title": "T",
            "url": "https://e.org/a_(b)_c)(",
            "kind": "primary",
            "paid": False,
        },
        "ok": {
            "slug": "ok",
            "title": "T",
            "url": "https://e.org/a_(b)",
            "kind": "primary",
            "paid": False,
        },
    }
    assert resolve_citations("[@s]", reg) == (
        "[A\\_b \\*c\\* \\[d\\] \\<e\\> \\`f\\` \\\\g](https://e.org/x%20y(1))"
    )
    assert resolve_citations("[@u]", reg) == "[T](https://e.org/a_%28b%29_c%29%28)"
    assert resolve_citations("[@ok]", reg) == "[T](https://e.org/a_(b))"
    # A per-use title is escaped too.
    assert resolve_citations("[@ok]", reg, {"ok": "x_y"}) == (
        "[x\\_y](https://e.org/a_(b))"
    )
    numbered = number_citations("see [@s]", reg)
    assert numbered.endswith(
        "\\[1\\] [A\\_b \\*c\\* \\[d\\] \\<e\\> \\`f\\` \\\\g](https://e.org/x%20y(1))\n"
    )


def test_rendering_follows_section_keys_not_positions_or_numbers() -> None:
    ds = load_dataset(REPO)
    reg = load_registry(REPO)
    baseline = {
        s.key: [b.text for b in s.blocks] for s in build_sections(ds, reg, False)
    }
    sections = ds.meta["sections"]
    sections.reverse()
    for sec in sections:  # swap the numbers of the rules and conflicts chapters
        if sec["key"] in ("rules", "conflicts"):
            sec["number"] = 15 - sec["number"]
    sec_by_key = {s["key"]: s for s in sections}
    assert (sec_by_key["rules"]["number"], sec_by_key["conflicts"]["number"]) == (8, 7)
    built = build_sections(ds, reg, False)
    assert [s.key for s in built] == [s["key"] for s in sections]
    for sec in built:
        assert {b.section for b in sec.blocks} == {sec.number}, sec.key
        body = [b.text for b in sec.blocks][1:]  # the heading carries the number
        assert body == baseline[sec.key][1:], sec.key
    chapters = render_chapters(ds, reg)
    assert "07-conflicts.md" in chapters and "08-rules.md" in chapters
    linker = _RefLinker(ds, 5)
    assert linker.line("K3") == "[K3](07-conflicts.md#k3)"
    assert linker.line("P3") == "[P3](08-rules.md#p3)"
    assert _RefLinker(ds, 8).line("P3") == "[P3](#p3)"


def test_inline_code_does_not_cross_a_newline() -> None:
    assert citation_slugs("a stray ` tick\nlater [@some-slug] here `code`") == [
        "some-slug"
    ]


def test_lone_backtick_does_not_hide_an_unknown_citation(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "docs" / "extra.md").write_text(
        "A lone ` backtick.\n\nLater [@unknown-slug] text.\n", encoding="utf-8"
    )
    assert cli.main(["--root", str(repo), "check"]) == 1
    assert "[@unknown-slug] does not resolve" in capsys.readouterr().err


def test_build_ignores_dot_directories_and_removes_empty_directories(
    repo: Path,
) -> None:
    hidden = repo / "publication" / ".cache"
    hidden.mkdir()
    (hidden / "file.txt").write_text("x", encoding="utf-8")
    assert build.stale(repo) == []
    stray = repo / "publication" / "old" / "deeper"
    stray.mkdir(parents=True)
    (stray / "x.md").write_text("x", encoding="utf-8")
    assert build.stale(repo) == ["old/deeper/x.md"]
    build.write(repo)
    assert not (repo / "publication" / "old").exists()
    assert hidden.is_dir()
    assert build.stale(repo) == []
