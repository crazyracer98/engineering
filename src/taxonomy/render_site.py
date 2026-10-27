"""Build the Material for MkDocs site.

``assemble`` writes ``build/site-src`` (the chapters, the methodology, the
history and an index page); ``build`` then runs ``mkdocs build --strict``.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from taxonomy import render_learn
from taxonomy.load import find_root, load_dataset, load_learn, load_registry
from taxonomy.model import Dataset, Learn, Source
from taxonomy.render_markdown import number_citations

REPO_URL = "https://github.com/crazyracer98/engineering"
SITE_SRC = Path("build") / "site-src"
#: Quiz engine files (written by the quiz-engine item) copied to ``assets/quiz/``.
SITE_ASSETS = Path("site-assets")
QUIZ_ASSETS = Path("assets") / "quiz"
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
        "## Learn and test yourself",
        "",
        "- [Learn](learn/index.md): worked examples for every rule and domain",
        "- [Quiz](quiz/index.md): self-check quizzes and a mixed test",
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


def write_learn(
    root: Path, src: Path, ds: Dataset, learn: Learn, registry: dict[str, Source]
) -> None:
    """Write the Learn and Quiz pages, ``quiz-bank.json`` and the quiz assets."""
    for name, text in render_learn.pages(ds, learn, registry).items():
        target = src / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    assets = src / QUIZ_ASSETS
    assets.mkdir(parents=True)
    bank = render_learn.bank(learn, ds.all_ids())
    (assets / "quiz-bank.json").write_text(
        json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    # Copy whatever the quiz engine provides; a missing directory is not an error.
    source = root / SITE_ASSETS
    if source.is_dir():
        for path in sorted(source.iterdir()):
            # The generated bank is authoritative; an asset must not replace it.
            if path.is_file() and path.name != "quiz-bank.json":
                shutil.copyfile(path, assets / path.name)


def assemble(root: Path) -> Path:
    """Write ``build/site-src`` and return it."""
    ds = load_dataset(root)
    registry = load_registry(root)
    learn = load_learn(root)
    src = root / SITE_SRC
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True)
    chapters: list[tuple[str, str]] = []
    for path in sorted((root / "publication" / "chapters").glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        if path.name == "07-rules.md":
            text = render_learn.add_learn_links(text, learn, ds)
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
    write_learn(root, src, ds, learn, registry)
    (src / "index.md").write_text(
        index_page(str(ds.meta["edition"]), chapters), encoding="utf-8"
    )
    return src


ENGINES = ("mkdocs", "zensical")


def _zensical_config(root: Path, out: Path) -> Path:
    """Write a copy of ``mkdocs.yml`` that builds into ``out`` (inside ``root``).

    ``zensical build`` has no ``-d``; it takes the output directory from
    ``site_dir``, resolved against the config file. The copy lives in
    ``build/`` with ``docs_dir`` and ``site_dir`` relative to it.
    """
    from ruamel.yaml import YAML

    yaml = YAML()
    config = yaml.load((root / "mkdocs.yml").read_text(encoding="utf-8"))
    path = root / "build" / "zensical-spike.yml"
    # Absolute paths panic Zensical 0.0.73 (Id(Format(Path(RootDir)))), so
    # both are written relative to the config file.
    config["docs_dir"] = os.path.relpath(root / SITE_SRC, path.parent)
    config["site_dir"] = os.path.relpath(out.resolve(), path.parent)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(config, handle)
    return path


def build(out: Path, root: Path | None = None, engine: str | None = None) -> None:
    """Assemble the site sources and build the site into ``out``.

    ``engine="zensical"`` (or ``TAXONOMY_SITE_ENGINE=zensical``) is the opt-in
    spike for issue #9 (``docs/zensical-spike.md``); MkDocs stays the default.
    """
    engine = engine or os.environ.get("TAXONOMY_SITE_ENGINE") or "mkdocs"
    if engine not in ENGINES:
        raise ValueError(f"unknown engine {engine!r}; expected one of {ENGINES}")
    root = root or find_root()
    assemble(root)
    env = {**os.environ, "NO_MKDOCS_2_WARNING": "1"}
    final = out
    if engine == "zensical":
        # Zensical rejects a site_dir outside the project root
        # ("site_dir must be within project root"); build inside and copy out.
        if not out.resolve().is_relative_to(root.resolve()):
            out = root / "build" / "zensical-out"
        command = [
            sys.executable,
            "-m",
            "zensical",
            "build",
            "--clean",
            "--strict",
            "-f",
            str(_zensical_config(root, out)),
        ]
    else:
        command = [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "-f",
            str(root / "mkdocs.yml"),
            "-d",
            str(out.resolve()),
        ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        check=False,
        cwd=root if engine == "zensical" else None,
    )
    if result.returncode:
        raise RuntimeError(f"{engine} build failed:\n{result.stdout}{result.stderr}")
    if out != final:
        shutil.rmtree(final, ignore_errors=True)
        shutil.copytree(out, final)
