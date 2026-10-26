"""Shared fixtures: a temp copy of the repository's dataset to seed violations into."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parent.parent
COPIED = ("data", "schema", "paper", "docs", "publication", "sources")


def pytest_configure(config: pytest.Config) -> None:
    """Register the ``slow`` marker (it still runs in the default invocation)."""
    config.addinivalue_line(
        "markers", "slow: builds the real PDF paper (a few seconds; runs by default)"
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A copy of the data, schemas, prose and publication under a temp root."""
    for name in COPIED:
        src = REPO / name
        if src.is_dir():
            shutil.copytree(
                src,
                tmp_path / name,
                ignore=shutil.ignore_patterns("plans", "__pycache__"),
            )
    return tmp_path


@pytest.fixture
def edit(repo: Path) -> Callable[[str, Callable[[Any], None]], None]:
    """Edit a YAML file of the temp repo in place: ``edit("data/rules.yaml", fn)``."""

    def apply(rel: str, fn: Callable[[Any], None]) -> None:
        yaml = YAML()
        yaml.width = 1_000_000
        path = repo / rel
        with path.open(encoding="utf-8") as handle:
            doc = yaml.load(handle)
        fn(doc)
        with path.open("w", encoding="utf-8") as handle:
            yaml.dump(doc, handle)

    return apply
