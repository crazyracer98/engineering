"""Load ``data/`` and the source registries.

``load_registry`` is the public citation resolver input: it merges the three
registries (``data/sources.yaml``, ``paper/references-extra.yaml`` and
``docs/methodology-references.yaml``) into one ``slug -> Source`` mapping.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from taxonomy.model import (
    Category,
    Conflict,
    Dataset,
    Quote,
    Rule,
    Source,
)

#: Registry files, relative to the repository root. The first is required.
REGISTRY_FILES = (
    "data/sources.yaml",
    "paper/references-extra.yaml",
    "docs/methodology-references.yaml",
)

#: Data files (stems) and the dataset field they fill.
DATA_STEMS = (
    "meta",
    "categories",
    "rules",
    "conflicts",
    "sources",
    "quotes",
    "domains",
    "glossary",
    "rigor_matrix",
    "method",
    "history",
)


def find_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (default: cwd) to the directory holding ``data/``."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "data" / "meta.yaml").is_file():
            return candidate
    raise FileNotFoundError(f"no repository root (data/meta.yaml) at or above {here}")


def plain(value: Any) -> Any:
    """Convert ruamel containers and scalar subclasses to plain Python values."""
    if isinstance(value, CommentedMap | dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, CommentedSeq | list):
        return [plain(v) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, str):
        return str(value)
    if isinstance(value, int):
        return int(value)
    return value


def load_yaml(path: Path) -> Any:
    """Read one YAML file with the round-trip loader, as plain values."""
    yaml = YAML()
    try:
        with path.open(encoding="utf-8") as handle:
            return plain(yaml.load(handle))
    except Exception as exc:
        raise ValueError(f"{path}: {type(exc).__name__}: {exc}") from exc


def load_dataset(root: Path) -> Dataset:
    """Load every file of ``data/`` under ``root``."""
    raw = {stem: load_yaml(root / "data" / f"{stem}.yaml") for stem in DATA_STEMS}
    return Dataset(
        meta=raw["meta"],
        categories=cast("list[Category]", raw["categories"]),
        rules=cast("list[Rule]", raw["rules"]),
        conflicts=cast("list[Conflict]", raw["conflicts"]),
        sources=cast("list[Source]", raw["sources"]),
        quotes=cast("list[Quote]", raw["quotes"]),
        domains=raw["domains"],
        glossary=raw["glossary"],
        rigor_matrix=raw["rigor_matrix"],
        method=raw["method"],
        history=raw["history"],
        raw=raw,
    )


def load_registry_files(root: Path) -> list[tuple[str, list[Source]]]:
    """Each existing registry file (relative path) with its entries, in order."""
    out: list[tuple[str, list[Source]]] = []
    for i, rel in enumerate(REGISTRY_FILES):
        path = root / rel
        if i == 0 and not path.is_file():
            raise FileNotFoundError(f"required registry {rel} is missing under {root}")
        if path.is_file():
            out.append((rel, cast("list[Source]", load_yaml(path) or [])))
    return out


def load_registry(root: Path) -> dict[str, Source]:
    """Merge the three registries into ``slug -> Source``.

    Raises ``FileNotFoundError`` when ``data/sources.yaml`` is missing and
    ``ValueError`` listing every slug that is defined twice (``taxonomy check``
    reports that, and duplicate URLs, with file names).
    """
    registry: dict[str, Source] = {}
    origin: dict[str, str] = {}
    duplicates: list[str] = []
    for rel, entries in load_registry_files(root):
        for entry in entries:
            slug = entry["slug"]
            if slug in registry:
                duplicates.append(f"{slug!r} in {rel} (also in {origin[slug]})")
                continue
            registry[slug] = entry
            origin[slug] = rel
    if duplicates:
        raise ValueError("duplicate source slugs: " + "; ".join(duplicates))
    return registry


def load_schema(root: Path, stem: str) -> dict[str, Any]:
    """The JSON Schema ``schema/<stem>.schema.json``."""
    with (root / "schema" / f"{stem}.schema.json").open(encoding="utf-8") as handle:
        return cast("dict[str, Any]", json.load(handle))
