"""Generated files, chapters, the flattened YAML, citation resolution and the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from taxonomy import build, cli
from taxonomy.load import load_dataset, load_registry
from taxonomy.render_markdown import (
    number_citations,
    render_chapters,
    render_single,
    resolve_citations,
)
from taxonomy.render_yaml import build_document, render_yaml
from tests.conftest import REPO
from tests.test_checks import Edit


def test_publication_is_up_to_date() -> None:
    assert build.stale(REPO) == []


def test_build_check_detects_stale_files(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = repo / "publication" / "engineering-best-practices.md"
    target.write_text(
        target.read_text(encoding="utf-8") + "\nstray\n", encoding="utf-8"
    )
    (repo / "publication" / "chapters" / "99-extra.md").write_text(
        "x\n", encoding="utf-8"
    )
    assert cli.main(["--root", str(repo), "build", "--check"]) == 1
    err = capsys.readouterr().err
    assert "publication/engineering-best-practices.md" in err
    assert "publication/chapters/99-extra.md" in err


def test_build_writes_and_cleans(repo: Path) -> None:
    (repo / "publication" / "chapters" / "99-extra.md").write_text(
        "x\n", encoding="utf-8"
    )
    assert cli.main(["--root", str(repo), "build"]) == 0
    assert not (repo / "publication" / "chapters" / "99-extra.md").exists()
    assert cli.main(["--root", str(repo), "build", "--check"]) == 0


def test_check_command(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["--root", str(repo), "check"]) == 0
    (repo / "docs" / "extra.md").write_text("[@missing]\n", encoding="utf-8")
    assert cli.main(["--root", str(repo), "check"]) == 1
    assert "[citations]" in capsys.readouterr().err


def test_chapters_have_anchors_and_relative_links() -> None:
    ds = load_dataset(REPO)
    chapters = render_chapters(ds, load_registry(REPO))
    rules = chapters["07-rules.md"]
    assert '<a id="p1"></a>P1' in rules
    assert '<a id="k1"></a>K1' in chapters["08-conflicts.md"]
    assert "[section 6](06-rigor-matrix.md)" in chapters["01-how-to-read.md"]
    assert "[P56](07-rules.md#p56)" in chapters["06-rigor-matrix.md"]
    assert len([n for n in chapters if n[:2].isdigit()]) == 12


def test_flattened_yaml_resolves_citations_and_drops_placeholders() -> None:
    ds = load_dataset(REPO)
    reg = load_registry(REPO)
    text = render_yaml(ds, reg)
    assert "[@" not in text
    assert "placeholder" not in text
    kept = sum(1 for q in ds.quotes if not q.get("placeholder"))
    assert text.count("\n- id: Q") == kept
    assert text.startswith("# Engineering Best Practices")
    assert text.endswith("\n") and not text.endswith("\n\n")


def test_resolve_citations_forms() -> None:
    reg = {
        "a": {"slug": "a", "title": "Alpha", "url": "https://x/a"},
        "b": {"slug": "b", "title": "Beta", "url": "https://x/b"},
    }
    r = resolve_citations
    assert r("see [@a]", reg) == "see [Alpha](https://x/a)"  # type: ignore[arg-type]
    assert r("[@a; @b]", reg) == "[Alpha](https://x/a); [Beta](https://x/b)"  # type: ignore[arg-type]
    assert r("[@a, p. 3]", reg) == "[Alpha](https://x/a), p. 3"  # type: ignore[arg-type]
    assert r("[@a]", reg, {"a": "Other"}) == "[Other](https://x/a)"  # type: ignore[arg-type]
    assert r("`[@zz]` and [@a]", reg) == "`[@zz]` and [Alpha](https://x/a)"  # type: ignore[arg-type]
    with pytest.raises(KeyError):
        r("[@zz]", reg)  # type: ignore[arg-type]


def test_number_citations_numbers_per_page_and_lists_references() -> None:
    reg = {
        "a": {"slug": "a", "title": "Alpha", "url": "https://x/a"},
        "b": {"slug": "b", "title": "Beta", "url": "https://x/b"},
    }
    text = "One [@b]. Two [@a; @b], and [@a, p. 3]. `[@zz]`\n"
    out = number_citations(text, reg)  # type: ignore[arg-type]
    body, refs = out.split("\n\n## References\n\n")
    one, two = r"[\[1\]](#ref-1)", r"[\[2\]](#ref-2)"
    assert body == f"One {one}. Two {two}, {one}, and {two}, p. 3. `[@zz]`"
    assert "Alpha" not in body
    assert refs == (
        '- <a id="ref-1"></a>\\[1\\] [Beta](https://x/b)\n'
        '- <a id="ref-2"></a>\\[2\\] [Alpha](https://x/a)\n'
    )
    # a page without citations gets no list, and an unknown slug raises
    assert number_citations("none\n", reg) == "none\n"  # type: ignore[arg-type]
    with pytest.raises(KeyError):
        number_citations("[@zz]", reg)  # type: ignore[arg-type]


def test_cli_reports_load_errors_without_traceback(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "data" / "glossary.yaml").write_text("a: [unclosed\n", encoding="utf-8")
    assert cli.main(["--root", str(repo), "check"]) == 1
    err = capsys.readouterr().err
    assert "[load]" in err and "Traceback" not in err
    assert cli.main(["--root", str(repo), "build"]) == 1
    err = capsys.readouterr().err
    assert "taxonomy build:" in err and "Traceback" not in err


def test_cli_without_a_repository_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["--root", str(tmp_path), "check"]) == 1
    assert "no data/meta.yaml" in capsys.readouterr().err
    assert cli.main(["--root", str(tmp_path), "site"]) == 1


def test_publication_readme_is_generated_and_dotfiles_are_ignored(repo: Path) -> None:
    assert (repo / "publication" / "README.md").is_file()
    (repo / "publication" / ".DS_Store").write_text("x", encoding="utf-8")
    assert build.stale(repo) == []
    (repo / "publication" / "README.md").unlink()
    assert build.stale(repo) == ["README.md"]


def test_duplicate_slugs_are_all_reported(repo: Path, edit: Edit) -> None:
    def seed(doc: Any) -> None:
        for i, slug in enumerate(("wikipedia-andon", "rfc-2119")):
            doc.append(
                {
                    "slug": slug,
                    "title": "D",
                    "url": f"https://example.org/{i}",
                    "kind": "primary",
                    "paid": False,
                }
            )

    edit("paper/references-extra.yaml", seed)
    with pytest.raises(ValueError) as info:
        load_registry(repo)
    assert "wikipedia-andon" in str(info.value) and "rfc-2119" in str(info.value)


def test_yaml_sources_text_uses_per_use_titles_like_markdown() -> None:
    ds = load_dataset(REPO)
    reg = load_registry(REPO)
    doc = build_document(ds, reg)
    md = render_single(ds, reg)
    items = [(f"quote {q['id']}", q) for q in doc["quotes"]] + [
        (f"management form {r['id']}", r["management"])
        for r in doc["rules"]
        if r.get("management")
    ]
    checked = 0
    for label, item in items:
        text = item.get("sources_text")
        if text is None:
            continue
        checked += 1
        assert f"| {text} |" in md, (
            f"{label}: the YAML sources_text is not a cell of the Markdown: {text!r}"
        )
    assert checked, "no quote or management form has a sources_text to compare"
    form = next(r for r in doc["rules"] if r["id"] == "P57")["management"]
    assert form["sources_text"].startswith("[ISO 22301:2019](")
