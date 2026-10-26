"""Every source in the three registries names its authors (CSL-JSON name objects)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parent.parent
REGISTRIES = (
    "data/sources.yaml",
    "paper/references-extra.yaml",
    "docs/methodology-references.yaml",
)
SCHEMA = json.loads((REPO / "schema" / "sources.schema.json").read_text("utf-8"))
AUTHOR = Draft202012Validator(SCHEMA["items"]["properties"]["author"])


def _entries(path: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = YAML(typ="safe").load(
        (REPO / path).read_text("utf-8")
    )
    return entries


@pytest.mark.parametrize("path", REGISTRIES)
def test_every_entry_has_valid_nonempty_author(path: str) -> None:
    entries = _entries(path)
    assert entries
    for entry in entries:
        assert entry.get("author"), f"{path}: {entry['slug']} has no author"
        errors = [e.message for e in AUTHOR.iter_errors(entry["author"])]
        assert not errors, f"{path}: {entry['slug']}: {errors}"


@pytest.mark.parametrize("path", REGISTRIES)
def test_registry_is_schema_valid(path: str) -> None:
    errors = [
        e.message for e in Draft202012Validator(SCHEMA).iter_errors(_entries(path))
    ]
    assert not errors


def test_author_is_required_by_schema() -> None:
    entry = {
        "slug": "x",
        "title": "X",
        "url": "https://x.example",
        "kind": "primary",
        "paid": False,
    }
    assert list(Draft202012Validator(SCHEMA).iter_errors([entry]))
    entry["author"] = [{"literal": ""}]
    assert list(Draft202012Validator(SCHEMA).iter_errors([entry]))
    entry["author"] = [{"given": "A"}]
    assert list(Draft202012Validator(SCHEMA).iter_errors([entry]))
    entry["author"] = [{"family": "F", "given": "G"}, {"literal": "Org"}]
    assert not list(Draft202012Validator(SCHEMA).iter_errors([entry]))
