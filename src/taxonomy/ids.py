"""Rule-ID matching that works for any prefix in ``meta.id_prefixes``.

Rule IDs are opaque (``P12``, ``K3``): a prefix from ``meta.id_prefixes``
plus a number. The class of a rule is its ``class`` field, never its ID.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Iterable

#: Separators of an ID range ("P3–P5", "P3-P5"): en dash or hyphen.
_DASH = "[–-]"


def prefix_alt(prefixes: Iterable[str]) -> str:
    """A regex alternative of ``prefixes``, longest first."""
    return "|".join(re.escape(p) for p in sorted(prefixes, key=len, reverse=True))


def id_pattern(prefixes: Iterable[str]) -> str:
    """A regex (no groups) for any ID with one of ``prefixes``."""
    return rf"(?:{prefix_alt(prefixes)})[1-9][0-9]*"


def id_key(rule_id: str, prefixes: Iterable[str]) -> tuple[int, int]:
    """Sort key: prefix in ``prefixes`` order, then number; unknown IDs last."""
    order = list(prefixes)
    match = re.fullmatch(rf"({prefix_alt(order)})([1-9][0-9]*)", rule_id)
    if not match:
        return (len(order), 0)
    return (order.index(match.group(1)), int(match.group(2)))


def id_finder(prefixes: Iterable[str]) -> re.Pattern[str]:
    """Regex finding whole IDs in prose (group 0 is the ID)."""
    return re.compile(rf"(?<![\w/#-]){id_pattern(prefixes)}\b")


def link_ids(
    text: str,
    known: Collection[str],
    prefixes: Iterable[str],
    href: Callable[[str], str],
) -> str:
    """Turn every known ID in ``text`` into a Markdown link ``[ID](href(ID))``.

    A range ("P3–P5" or "P3-P5", same prefix, ascending) whose IDs are all
    known links every ID in it, written as a comma list ("P3, P4, P5").
    An unknown ID, or a pair that is not a range ("P35–K2"), stays as
    written, each known end linked on its own.
    """
    alt = prefix_alt(prefixes)
    one = re.compile(rf"(?<![\w/#-])({alt})([1-9][0-9]*)\b")
    tail = re.compile(rf"[ \t]*{_DASH}[ \t]*({alt})([1-9][0-9]*)\b")
    out: list[str] = []
    pos = 0
    while (m := one.search(text, pos)) is not None:
        out.append(text[pos : m.start()])
        pos = m.end()
        end = tail.match(text, pos)
        if end and end[1] == m[1] and int(m[2]) < int(end[2]):
            run = [f"{m[1]}{n}" for n in range(int(m[2]), int(end[2]) + 1)]
            if all(i in known for i in run):
                out.append(", ".join(f"[{i}]({href(i)})" for i in run))
                pos = end.end()
                continue
        rid = m.group(0)
        out.append(f"[{rid}]({href(rid)})" if rid in known else rid)
    out.append(text[pos:])
    return "".join(out)
