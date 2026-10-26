"""Build the Material for MkDocs site.

``assemble`` writes ``build/site-src`` (the chapters, the methodology, the
history and an index page); ``build`` then runs ``mkdocs build --strict``.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from taxonomy.load import find_root, load_dataset, load_registry
from taxonomy.render_markdown import number_citations

REPO_URL = "https://github.com/crazyracer98/engineering"
SITE_SRC = Path("build") / "site-src"
#: Release assets the index links to, named by the release contract.
ASSETS = (
    ("engineering-best-practices.pdf", "PDF paper"),
    ("engineering-best-practices.md", "Single-file Markdown"),
    ("engineering-best-practices.yaml", "YAML dataset"),
    ("references.json", "References (CSL JSON)"),
)
_PARENT_LINK = re.compile(r"\]\(((?:\.\./)+)([^)\s]*)\)")
_TITLE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def chapter_title(text: str) -> str:
    match = _TITLE.search(text)
    return match.group(1) if match else ""


def repo_links(text: str) -> str:
    """Point links that leave the docs (``../data/x``) at the repository on GitHub."""
    return _PARENT_LINK.sub(lambda m: f"]({REPO_URL}/blob/main/{m.group(2)})", text)


def index_page(edition: str, chapters: list[tuple[str, str]]) -> str:
    """The home page: version line, description and links."""
    base = f"{REPO_URL}/releases/download/v{edition}"
    lines = [
        "# Engineering Best Practices",
        "",
        f"Version {edition}",
        "",
        "A cross-domain taxonomy of engineering and management rules, each with "
        "its condition, action, reason, check and evidence, and the sources "
        "behind it. The site is generated from the dataset in "
        f"[`data/`]({REPO_URL}/tree/main/data).",
        "",
        "## Chapters",
        "",
        *(f"- [{title}]({name})" for name, title in chapters),
        "",
        "## About",
        "",
        "- [Methodology](methodology.md)",
        "- [History](history.md)",
        "",
        "## Downloads",
        "",
        *(f"- [{label}]({base}/{file})" for file, label in ASSETS),
        "",
    ]
    return "\n".join(lines)


def assemble(root: Path) -> Path:
    """Write ``build/site-src`` and return it."""
    ds = load_dataset(root)
    registry = load_registry(root)
    src = root / SITE_SRC
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True)
    chapters: list[tuple[str, str]] = []
    for path in sorted((root / "publication" / "chapters").glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        (src / path.name).write_text(text, encoding="utf-8")
        chapters.append((path.name, chapter_title(text) or path.stem))
    if not chapters:
        raise FileNotFoundError(
            "publication/chapters has no NN-*.md; run `taxonomy build`"
        )
    for name in ("methodology.md", "history.md"):
        text = (root / "docs" / name).read_text(encoding="utf-8")
        text = repo_links(number_citations(text, registry))
        (src / name).write_text(text, encoding="utf-8")
    (src / "index.md").write_text(
        index_page(str(ds.meta["edition"]), chapters), encoding="utf-8"
    )
    return src


def build(out: Path, root: Path | None = None) -> None:
    """Assemble the site sources and build the site into ``out``."""
    root = root or find_root()
    assemble(root)
    env = {**os.environ, "NO_MKDOCS_2_WARNING": "1"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "-f",
            str(root / "mkdocs.yml"),
            "-d",
            str(out.resolve()),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"mkdocs build failed:\n{result.stdout}{result.stderr}")
