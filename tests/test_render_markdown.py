"""Renderer helpers: code-aware linking and citation scanning."""

from __future__ import annotations

from pathlib import Path

import pytest

from taxonomy import build, cli
from taxonomy.load import load_dataset
from taxonomy.render_markdown import _link_block, citation_slugs
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
