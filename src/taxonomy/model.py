"""Typed view of the dataset in ``data/`` and shared constants.

The YAML files are loaded into plain ``dict``/``list`` values (see
``taxonomy.load``). The ``TypedDict`` types here describe the entities that
the checks and renderers rely on; the JSON Schemas in ``schema/`` stay the
authority on what is valid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, TypedDict

# Rule ID shapes, as in the schemas.
RULE_ID = re.compile(r"^P[1-9][0-9]*$")
CONFLICT_ID = re.compile(r"^K[1-9][0-9]*$")
#: The rule named in every rigor-matrix cell ("Checker level: peer (P56)").
CHECKER_LEVEL_RULE = "P56"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

#: Relation keys of ``rules.related``, in the order edition 9 prints them,
#: with the words used in the RELATED cell.
RELATION_LABELS: dict[str, str] = {
    "depends_on": "depends on",
    "strengthens": "strengthens",
    "strengthened_by": "strengthened by",
    "conflicts_with": "conflicts with",
    "checks": "checks",
    "checked_by": "checked by",
    "scaled_by": "scaled by",
}


class Source(TypedDict, total=False):
    slug: str
    title: str
    url: str
    kind: str
    publisher: str | None
    year: int | None
    via: dict[str, str]
    paid: bool
    accessed: str | None
    notes: str | None


class Management(TypedDict, total=False):
    name: str
    form_name: str
    form: str
    example: str
    sources: list[str]
    source_titles: dict[str, str]
    sources_text: str
    evidence: str
    evidence_note: str | None
    evidence_text: str


Rule = TypedDict(
    "Rule",
    {
        "id": str,
        "former_id": str,
        "name": str,
        "class": str,
        "class_note": str,
        "strength": str,
        "category": str,
        "if": str,
        "then": str,
        "because": str,
        "example": str,
        "check": str,
        "violation": str,
        "related": dict[str, list[str]],
        "related_text": str,
        "evidence": str,
        "evidence_note": str | None,
        "evidence_text": str,
        "source_domain": str,
        "counterexample": str,
        "notes": str | None,
        "sources": list[str],
        "source_titles": dict[str, str],
        "management": Management | None,
    },
    total=False,
)

Conflict = TypedDict(
    "Conflict",
    {
        "id": str,
        "if": str,
        "then": str,
        "because": str,
        "example": str,
        "basis": str,
        "rules": list[str],
    },
)


class Quote(TypedDict, total=False):
    id: str
    rules: list[str]
    source: str | None
    text: str
    locator: str | None
    group: str
    placeholder: bool
    rule_label: str
    extra_sources: list[str]
    source_titles: dict[str, str]
    sources_text: str


class Category(TypedDict):
    id: str
    name: str
    description: str
    rules: list[str]


@dataclass
class Dataset:
    """Everything under ``data/``, loaded as plain Python values."""

    meta: dict[str, Any]
    categories: list[Category]
    rules: list[Rule]
    conflicts: list[Conflict]
    sources: list[Source]
    quotes: list[Quote]
    domains: dict[str, Any]
    glossary: dict[str, dict[str, str]]
    rigor_matrix: list[dict[str, Any]]
    method: list[dict[str, str]]
    history: dict[str, Any]
    #: Raw file contents by file stem, for generic walks (``"rules"`` ...).
    raw: dict[str, Any] = field(default_factory=dict)

    def rule_by_id(self) -> dict[str, Rule]:
        return {r["id"]: r for r in self.rules}

    def category_by_id(self) -> dict[str, Category]:
        return {c["id"]: c for c in self.categories}

    def all_ids(self) -> set[str]:
        """IDs of all rules and conflict rules."""
        return {r["id"] for r in self.rules} | {k["id"] for k in self.conflicts}
