"""Tests for the site renderer (``taxonomy.render_site``)."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from taxonomy import render_site
from taxonomy.load import load_dataset, load_yaml
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


def _stub_root(tmp_path: Path) -> Path:
    """A repo copy with every learning file emptied, whatever content is live."""
    root = tmp_path / "stub"
    for name in ("data", "publication", "docs", "paper"):
        shutil.copytree(
            REPO / name, root / name, ignore=shutil.ignore_patterns("plans")
        )
    shutil.copyfile(REPO / "mkdocs.yml", root / "mkdocs.yml")
    for path in (root / "data" / "learn").glob("*/*.yaml"):
        path.write_text("[]\n", encoding="utf-8")
    return root


def _fixture_root(tmp_path: Path, assets: bool = False) -> Path:
    """A repo copy whose ``data/learn`` holds the learn fixtures."""
    root = tmp_path / "repo"
    for name in ("data", "publication", "docs", "paper"):
        shutil.copytree(
            REPO / name, root / name, ignore=shutil.ignore_patterns("plans")
        )
    shutil.rmtree(root / "data" / "learn")
    shutil.copytree(REPO / "tests" / "fixtures" / "learn", root / "data" / "learn")
    shutil.copyfile(REPO / "mkdocs.yml", root / "mkdocs.yml")
    if assets:
        (root / "site-assets").mkdir()
        (root / "site-assets" / "quiz.js").write_text("// js\n", encoding="utf-8")
        (root / "site-assets" / "quiz.css").write_text("/* css */\n", encoding="utf-8")
    return root


def test_nav_lists_exactly_the_generated_pages() -> None:
    def pages(node: object) -> set[str]:
        if isinstance(node, str):
            return {node}
        if isinstance(node, list):
            return set().union(*(pages(n) for n in node)) if node else set()
        if isinstance(node, dict):
            return set().union(*(pages(v) for v in node.values()))
        return set()

    nav = load_yaml(REPO / "mkdocs.yml")["nav"]
    src = render_site.assemble(REPO)
    built = {p.relative_to(src).as_posix() for p in src.rglob("*.md")}
    assert pages(nav) == built


def test_assemble_writes_learn_quiz_bank_and_assets(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path, assets=True)
    src = render_site.assemble(root)
    bank = json.loads((src / "assets/quiz/quiz-bank.json").read_text("utf-8"))
    assert [q["id"] for q in bank] == ["q-a-01", "q-k-01"]
    assert (src / "assets/quiz/quiz.js").read_text("utf-8") == "// js\n"
    assert (src / "assets/quiz/quiz.css").is_file()
    chapter = (src / "07-rules.md").read_text("utf-8")
    assert "([Learn](learn/a.md#p1))" in chapter
    assert "[Learn](learn/a.md#p2)" not in chapter
    # publication/ is untouched by the site-only links.
    assert "[Learn]" not in (root / "publication/chapters/07-rules.md").read_text(
        "utf-8"
    )
    index = (src / "index.md").read_text("utf-8")
    assert "(learn/index.md)" in index and "(quiz/index.md)" in index
    snippet = (src / "quiz/a.md").read_text("utf-8")
    assert 'data-qid="q-a-01"' in snippet


def test_assets_cannot_replace_the_generated_bank(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path, assets=True)
    (root / "site-assets" / "quiz-bank.json").write_text("[]\n", encoding="utf-8")
    src = render_site.assemble(root)
    bank = json.loads((src / "assets/quiz/quiz-bank.json").read_text("utf-8"))
    assert [q["id"] for q in bank] == ["q-a-01", "q-k-01"]


def test_assemble_without_site_assets_or_learn_data(tmp_path: Path) -> None:
    src = render_site.assemble(_stub_root(tmp_path))
    assert json.loads((src / "assets/quiz/quiz-bank.json").read_text("utf-8")) == []
    assert "[Learn](" not in (src / "07-rules.md").read_text("utf-8")
    assert len(list((src / "learn").glob("*.md"))) == 1 + 9 + 20
    assert len(list((src / "quiz").glob("*.md"))) == 1 + 1 + 9 + 1


def test_fixture_build_strict_renders_quiz_and_learn(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path, assets=True)
    out = tmp_path / "site"
    render_site.build(out, root)
    quiz = (out / "quiz" / "a" / "index.html").read_text("utf-8")
    assert '<form class="quiz-q" data-qid="q-a-01">' in quiz
    assert 'src="../../assets/quiz/quiz.js"' in quiz and 'type="module"' in quiz
    assert (out / "assets/quiz/quiz-bank.json").is_file()
    mixed = (out / "quiz" / "mixed" / "index.html").read_text("utf-8")
    assert 'data-bank="../../assets/quiz/quiz-bank.json"' in mixed
    rules = (out / "07-rules" / "index.html").read_text("utf-8")
    assert 'href="../learn/a/#p1"' in rules
    learn = (out / "learn" / "a" / "index.html").read_text("utf-8")
    assert 'id="p1"' in learn and "Real case" in learn
    assert (out / "learn" / "branch-civil" / "index.html").is_file()


def test_build_rejects_unknown_engine(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown engine"):
        render_site.build(tmp_path / "out", tmp_path, engine="hugo")


def test_zensical_config_is_relative_to_the_config_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copyfile(REPO / "mkdocs.yml", root / "mkdocs.yml")
    config = render_site._zensical_config(root, tmp_path / "elsewhere" / "site")
    assert config.parent == root / "build"
    loaded = load_yaml(config)
    assert loaded["docs_dir"] == "site-src"
    assert loaded["site_dir"] == "../../elsewhere/site"
    assert loaded["strict"] is True
    assert loaded["nav"] == load_yaml(REPO / "mkdocs.yml")["nav"]


def test_zensical_build_matches_the_mkdocs_pages(tmp_path: Path) -> None:
    """Opt-in spike (issue #9): runs only where the ``zensical`` extra is installed."""
    pytest.importorskip("zensical")
    root = _fixture_root(tmp_path, assets=True)
    render_site.build(tmp_path / "mk", root)
    render_site.build(tmp_path / "zs", root, engine="zensical")

    def pages(out: Path) -> set[str]:
        return {str(p.relative_to(out)) for p in out.rglob("*.html")}

    assert pages(tmp_path / "zs") == pages(tmp_path / "mk")
    assert (tmp_path / "zs" / "search.json").is_file()
