#!/usr/bin/env python3
"""One-off re-key of the rule IDs: edition-9 U/R/C numbers -> opaque P1-P83.

Provenance record (plan work item D4, "User decision (rule IDs)"). It ran
once, before 1.0.0, on the tree that still used the edition-9 IDs, and is
kept only to document how ``sources/import/id-map.yaml`` and the renamed
dataset came about. Running it again on a re-keyed tree refuses to do
anything.

The new IDs follow category order: categories A to I as listed in
``data/categories.yaml``, and within a category the order of that list,
which is edition 9's section 7 order. ``K1``-``K8`` and the quote IDs keep
their names.

What it does:

1. computes the map ``old -> new`` and writes ``sources/import/id-map.yaml``;
2. rewrites every rule ID in ``data/`` and in the extra files given on the
   command line, including lowercase anchors (``#u12`` -> ``#p15``);
3. expands every old range (``U1-U5``) through the map and re-compresses
   only runs of three or more that are contiguous in the new IDs
   (``P3-P5, P9``), sorted;
4. reorders ``data/rules.yaml`` into new-ID order and sorts the ``related``
   lists.

The result was reviewed by hand afterwards (prose that is not a plain ID
mention, and the places that cite edition 9 as such and keep its IDs).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from ruamel.yaml import YAML

#: A rule ID, or a range of two IDs with a hyphen or en dash between them.
_TOKEN = re.compile(
    r"(?<![\w/#.-])(?P<a>[URC])(?P<an>[1-9][0-9]*)"
    r"(?:(?P<sep>[ \t]*[–-][ \t]*)(?P<b>[URC])(?P<bn>[1-9][0-9]*))?\b"
)
_ANCHOR = re.compile(r"(?<=#)([urc])([1-9][0-9]*)\b")
_DATA_FILES = [
    "meta",
    "categories",
    "rules",
    "conflicts",
    "domains",
    "glossary",
    "method",
    "quotes",
    "rigor_matrix",
    "sources",
    "history",
]


def compute_map(root: Path) -> list[tuple[str, str]]:
    """``[(old, new)]`` in new-ID order, from ``data/`` (category, section 7)."""
    cats = YAML().load((root / "data/categories.yaml").read_text("utf-8"))
    rules = YAML().load((root / "data/rules.yaml").read_text("utf-8"))
    category = {r["id"]: r["category"] for r in rules}
    order = [rid for cat in cats for rid in cat["rules"]]
    for cat in cats:
        for rid in cat["rules"]:
            if category[rid] != cat["id"]:
                raise SystemExit(f"{rid} is listed in category {cat['id']}")
    if sorted(order) != sorted(category) or len(set(order)) != len(order):
        raise SystemExit("categories.rules and rules.yaml disagree")
    return [(old, f"P{n}") for n, old in enumerate(order, start=1)]


def _compress(numbers: list[int], dash: str) -> list[str]:
    """``[3, 4, 5, 9]`` -> ``["P3–P5", "P9"]``; runs of two stay separate."""
    out: list[str] = []
    i = 0
    while i < len(numbers):
        j = i
        while j + 1 < len(numbers) and numbers[j + 1] == numbers[j] + 1:
            j += 1
        if j - i >= 2:
            out.append(f"P{numbers[i]}{dash}P{numbers[j]}")
        else:
            out.extend(f"P{n}" for n in numbers[i : j + 1])
        i = j + 1
    return out


def rewrite(text: str, mapping: dict[str, str]) -> str:
    """Rewrite every old rule ID and range in ``text``."""

    def token(m: re.Match[str]) -> str:
        a = f"{m['a']}{m['an']}"
        if a not in mapping:
            return m.group(0)
        if m["b"] is None:
            return mapping[a]
        b = f"{m['b']}{m['bn']}"
        lo, hi = int(m["an"]), int(m["bn"])
        if m["a"] == m["b"] and lo < hi:
            olds = [f"{m['a']}{n}" for n in range(lo, hi + 1)]
            if all(o in mapping for o in olds):
                nums = sorted(int(mapping[o][1:]) for o in olds)
                dash = "–" if "–" in m["sep"] else "-"
                return ", ".join(_compress(nums, dash))
        # Not a range (a pair such as "U35-U23"): map both ends.
        return mapping[a] + m["sep"] + mapping.get(b, b)

    def anchor(m: re.Match[str]) -> str:
        old = f"{m[1].upper()}{m[2]}"
        return mapping[old].lower() if old in mapping else m.group(0)

    return _ANCHOR.sub(anchor, _TOKEN.sub(token, text))


def sort_runs(text: str, indent: int) -> str:
    """Sort every run of ``- P<n>`` list items at ``indent`` spaces by number."""

    def sort_run(m: re.Match[str]) -> str:
        lines = m.group(0).splitlines(keepends=True)
        return "".join(sorted(lines, key=lambda s: int(re.search(r"P(\d+)", s)[1])))  # type: ignore[index]

    return re.sub(rf"(?m)(?:^ {{{indent}}}- P[1-9][0-9]*\n)+", sort_run, text)


def reorder_rules(text: str) -> str:
    """Put the entries of a *rewritten* ``rules.yaml`` in P order and sort the
    ``related`` lists."""
    head, *chunks = re.split(r"(?m)^(?=- id: )", text)
    chunks.sort(key=lambda c: int(re.match(r"- id: P(\d+)", c)[1]))  # type: ignore[index]
    return head + sort_runs("".join(chunks), 4)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("files", nargs="*", help="extra files to rewrite (repo-relative)")
    args = ap.parse_args()
    root: Path = args.root
    if re.search(r"(?m)^- id: P\d+$", (root / "data/rules.yaml").read_text("utf-8")):
        raise SystemExit("data/ already uses the P IDs; nothing to do")
    pairs = compute_map(root)
    mapping = dict(pairs)
    header = (
        "# Edition-9 rule IDs -> the opaque IDs of 1.0.0 (P1-P83), in new-ID order.\n"
        "# Provenance only (plan item D4): 1.0.0 is the first version, so\n"
        "# data/history.yaml `id_map` stays empty. New IDs follow category order\n"
        "# (A to I), then the order of edition 9's section 7. K1-K8 are unchanged.\n"
        "# Generated by sources/import/rekey_d4.py.\n"
    )
    entries = "".join(f"- old: {o}\n  new: {n}\n" for o, n in pairs)
    targets = [root / f"data/{n}.yaml" for n in _DATA_FILES] + [
        root / f for f in args.files
    ]
    if args.dry_run:
        for path in targets:
            old = path.read_text("utf-8")
            if rewrite(old, mapping) != old:
                print(path)
        return
    (root / "sources/import/id-map.yaml").write_text(header + entries, "utf-8")
    for path in targets:
        new = rewrite(path.read_text("utf-8"), mapping)
        if path.name == "rules.yaml":
            new = reorder_rules(new)
        elif path.name == "rigor_matrix.yaml":
            new = sort_runs(new, 2)
        path.write_text(new, "utf-8")


if __name__ == "__main__":
    sys.exit(main())
