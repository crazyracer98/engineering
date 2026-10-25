"""Generate ``publication/`` from ``data/``."""

from __future__ import annotations

from pathlib import Path

from taxonomy.load import load_dataset, load_registry
from taxonomy.render_markdown import render_chapters, render_single
from taxonomy.render_yaml import render_yaml

PUBLICATION = "publication"


def generate(root: Path) -> dict[str, str]:
    """``{path relative to publication/: text}`` for every generated file."""
    ds = load_dataset(root)
    reg = load_registry(root)
    files = {
        "engineering-best-practices.md": render_single(ds, reg),
        "engineering-best-practices.yaml": render_yaml(ds, reg),
    }
    for name, text in render_chapters(ds, reg).items():
        files[f"chapters/{name}"] = text
    return files


def existing(root: Path) -> dict[str, str]:
    base = root / PUBLICATION
    if not base.is_dir():
        return {}
    return {
        str(p.relative_to(base)): p.read_text(encoding="utf-8")
        for p in sorted(base.rglob("*"))
        if p.is_file()
    }


def stale(root: Path) -> list[str]:
    """Paths (relative to ``publication/``) that are missing, differ or are extra."""
    want = generate(root)
    have = existing(root)
    out = [p for p in want if have.get(p) != want[p]]
    out += [p for p in have if p not in want]
    return sorted(out)


def write(root: Path) -> list[str]:
    """Write ``publication/`` and remove files no longer generated.

    Returns the changed paths.
    """
    want = generate(root)
    have = existing(root)
    base = root / PUBLICATION
    changed: list[str] = []
    for rel, text in want.items():
        if have.get(rel) != text:
            path = base / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            changed.append(rel)
    for rel in have:
        if rel not in want:
            (base / rel).unlink()
            changed.append(rel)
    return sorted(changed)
