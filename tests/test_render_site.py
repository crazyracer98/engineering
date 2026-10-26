"""Tests for the site renderer (``taxonomy.render_site``)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from taxonomy import render_site
from taxonomy.load import load_dataset
from taxonomy.render_markdown import strip_code

REPO = Path(__file__).resolve().parents[1]


def test_assemble_has_every_page_without_raw_citations() -> None:
    src = render_site.assemble(REPO)
    names = {p.name for p in src.glob("*.md")}
    chapters = sorted((REPO / "publication" / "chapters").glob("[0-9][0-9]-*.md"))
    assert len(chapters) == 12
    assert {p.name for p in chapters} <= names
    assert {"index.md", "methodology.md", "history.md"} <= names
    assert "README.md" not in names
    for path in src.glob("*.md"):
        assert "[@" not in strip_code(path.read_text(encoding="utf-8")), path.name


def test_site_citations_are_numbered_links_with_a_reference_list() -> None:
    src = render_site.assemble(REPO)
    page = (src / "methodology.md").read_text(encoding="utf-8")
    body, refs = page.split("\n## References\n\n")
    assert r"[\[1\]](#ref-1)" in body
    assert "RFC 2119" not in body.split("## Cross-cutting", 1)[0]
    entries = refs.strip().split("\n")
    for n, entry in enumerate(entries, 1):
        assert entry.startswith(f'- <a id="ref-{n}"></a>\\[{n}\\] [')
        assert entry.endswith(")")
    cited = {int(m) for m in re.findall(r"\(#ref-(\d+)\)", body)}
    assert cited == set(range(1, len(entries) + 1))
    assert "References" not in (src / "history.md").read_text(encoding="utf-8")


def test_index_version_line_and_downloads() -> None:
    edition = str(load_dataset(REPO).meta["edition"])
    index = (render_site.assemble(REPO) / "index.md").read_text(encoding="utf-8")
    assert f"Version {edition}" in index
    base = f"releases/download/v{edition}/"
    for file, _ in render_site.ASSETS:
        assert base + file in index
    assert "(07-rules.md)" in index


def test_index_page_uses_given_edition() -> None:
    text = render_site.index_page("9.9.9", [("01-x.md", "1. X")])
    assert "Version 9.9.9" in text and "v9.9.9/" in text


def test_repo_links_rewrites_parent_links_only() -> None:
    text = "[a](../data/x.yaml) [b](history.md#h) [c](https://e.org/)"
    assert render_site.repo_links(text) == (
        f"[a]({render_site.REPO_URL}/blob/main/data/x.yaml) "
        "[b](history.md#h) [c](https://e.org/)"
    )


def test_real_build_strict(tmp_path: Path) -> None:
    out = tmp_path / "site"
    render_site.build(out, REPO)
    assert (out / "index.html").is_file()
    rules = (out / "07-rules" / "index.html").read_text(encoding="utf-8")
    assert 'id="p1"' in rules
    assert re.search(
        r'href="\.\./07-rules/#p56"',
        (out / "03-overview" / "index.html").read_text("utf-8"),
    )
    assert (out / "methodology" / "index.html").is_file()


def test_build_raises_on_mkdocs_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(render_site, "assemble", lambda root: root)
    with pytest.raises(RuntimeError, match="mkdocs build failed"):
        render_site.build(tmp_path / "out", tmp_path)  # no mkdocs.yml there
