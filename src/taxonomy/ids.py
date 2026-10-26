"""Rule-ID matching that works for any prefix in ``meta.id_prefixes``.

Rule IDs are opaque (``P12``, ``K3``): a prefix from ``meta.id_prefixes``
plus a number. The class of a rule is its ``class`` field, never its ID.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Iterable
from functools import lru_cache

#: Separators of an ID range ("P3–P5", "P3-P5"): en dash or hyphen, with
#: optional spaces around it.
_RANGE_SEP = r"[ \t]*[–-][ \t]*"
#: Not inside a word, path or anchor, and not the tail of a hyphenated word
#: ("ISO-P1"). A hyphen after a digit ("P3-P5") is a range separator.
_BEFORE = r"(?<![\w/#])(?<![A-Za-z]-)"


def prefix_alt(prefixes: Iterable[str]) -> str:
    """A regex alternative of ``prefixes``, longest first."""
    return "|".join(re.escape(p) for p in sorted(prefixes, key=len, reverse=True))


def id_pattern(prefixes: Iterable[str]) -> str:
    """A regex (no groups) for any ID with one of ``prefixes``."""
    return rf"(?:{prefix_alt(prefixes)})[1-9][0-9]*"


@lru_cache(maxsize=32)
def _key_pattern(order: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(rf"({prefix_alt(order)})([1-9][0-9]*)")


def id_key(rule_id: str, prefixes: Iterable[str]) -> tuple[int, int]:
    """Sort key: prefix in ``prefixes`` order, then number; unknown IDs last."""
    order = tuple(prefixes)
    match = _key_pattern(order).fullmatch(rule_id)
    if not match:
        return (len(order), 0)
    return (order.index(match.group(1)), int(match.group(2)))


@lru_cache(maxsize=32)
def _finder(prefixes: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(rf"{_BEFORE}{id_pattern(prefixes)}\b")


def id_finder(prefixes: Iterable[str]) -> re.Pattern[str]:
    """Regex finding whole IDs in prose (group 0 is the ID)."""
    return _finder(tuple(prefixes))


@lru_cache(maxsize=32)
def _one_and_tail(
    prefixes: tuple[str, ...],
) -> tuple[re.Pattern[str], re.Pattern[str]]:
    alt = prefix_alt(prefixes)
    one = re.compile(rf"{_BEFORE}({alt})([1-9][0-9]*)\b")
    tail = re.compile(rf"{_RANGE_SEP}({alt})([1-9][0-9]*)\b")
    return one, tail


def _range_end(
    first: re.Match[str], text: str, tail: re.Pattern[str]
) -> re.Match[str] | None:
    """The match of the range end after ``first``, or None when there is none.

    A range is two IDs with the same prefix, ascending, joined by an en dash
    or a hyphen (spaces allowed).
    """
    end = tail.match(text, first.end())
    if end and end[1] == first[1] and int(first[2]) < int(end[2]):
        return end
    return None


def link_ids(
    text: str,
    known: Collection[str],
    prefixes: Iterable[str],
    href: Callable[[str], str],
) -> str:
    """Turn every known ID in ``text`` into a Markdown link ``[ID](href(ID))``.

    A range ("P3–P5", "P3-P5" or "P3 – P5": same prefix, ascending) keeps its
    written form, with the separator normalised to an en dash and without
    spaces, and links both of its ends ("[P3](…)–[P5](…)") when both are
    known. It is not expanded into a list. An unknown ID, or a pair that is
    not a range ("P35–K2"), stays as written, each known end linked on its own.
    """
    one, tail = _one_and_tail(tuple(prefixes))

    def link(rid: str) -> str:
        return f"[{rid}]({href(rid)})" if rid in known else rid

    out: list[str] = []
    pos = 0
    while (m := one.search(text, pos)) is not None:
        out.append(text[pos : m.start()])
        pos = m.end()
        end = _range_end(m, text, tail)
        first, last = m.group(0), f"{end[1]}{end[2]}" if end else ""
        if end and first in known and last in known:
            out.append(f"{link(first)}–{link(last)}")
            pos = end.end()
            continue
        out.append(link(first))
    out.append(text[pos:])
    return "".join(out)


def expand_ids(text: str, prefixes: Iterable[str]) -> list[str]:
    """Every ID named in ``text`` in order, a range ("P3–P5") counting as all
    of its IDs (P3, P4, P5)."""
    one, tail = _one_and_tail(tuple(prefixes))
    found: list[str] = []
    pos = 0
    while (m := one.search(text, pos)) is not None:
        pos = m.end()
        end = _range_end(m, text, tail)
        if end:
            found.extend(f"{m[1]}{n}" for n in range(int(m[2]), int(end[2]) + 1))
            pos = end.end()
        else:
            found.append(m.group(0))
    return found
