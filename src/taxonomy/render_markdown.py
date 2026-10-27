"""Render the dataset as Markdown: the single file and the split chapters.

``render_single`` reproduces the edition-9 Markdown from ``data/``;
``render_chapters`` splits the same content by numbered section for GitHub
reading, adding stable ``<a id="p1"></a>`` rule anchors and relative links
between chapters.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from taxonomy.ids import link_ids
from taxonomy.model import (
    CHECKER_LEVEL_RULE,
    CLASS_LETTER,
    RELATION_LABELS,
    Dataset,
    Management,
    Quote,
    Rule,
    Source,
)

_CITATION = re.compile(r"\[(@[^\[\]]*)\]")
_ITEM = re.compile(r"^@([a-z0-9]+(?:-[a-z0-9]+)*)(?:,\s*(.+))?$")
_FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)
_INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")


def strip_code(text: str) -> str:
    """Blank out fenced code blocks and inline code spans (keeps length of lines)."""
    text = _FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return _INLINE_CODE.sub("", text)


def parse_citation(inner: str) -> list[tuple[str, str | None]]:
    """Parse the inside of ``[@a, p. 3; @b]`` into ``[(slug, locator), ...]``.

    Raises ``ValueError`` for an item that is not ``@slug`` or ``@slug, locator``.
    """
    items: list[tuple[str, str | None]] = []
    for part in inner.split(";"):
        match = _ITEM.match(part.strip())
        if not match:
            raise ValueError(f"malformed citation item {part.strip()!r}")
        items.append((match.group(1), match.group(2)))
    return items


def citation_slugs(text: str) -> list[str]:
    """All slugs cited in ``text`` outside code, in order. Malformed items raise."""
    slugs: list[str] = []
    for match in _CITATION.finditer(strip_code(text)):
        slugs.extend(slug for slug, _ in parse_citation(match.group(1)))
    return slugs


class UnknownSlugError(KeyError):
    """A citation or source list names a slug that no registry defines."""

    def __init__(self, slug: str) -> None:
        super().__init__(slug)
        self.slug = slug

    def __str__(self) -> str:
        return f"unknown source slug {self.slug!r} (in no source registry)"


def lookup(registry: Mapping[str, Source], slug: str) -> Source:
    """``registry[slug]``, raising ``UnknownSlugError`` for an unknown slug."""
    try:
        return registry[slug]
    except KeyError:
        raise UnknownSlugError(slug) from None


_TITLE_SPECIAL = re.compile(r"([\\`*_\[\]<>])")
_URL_UNSAFE = re.compile(r"[\s<>]")


def escape_title(title: str) -> str:
    """``title`` safe as Markdown link text: backslash-escape ``\\ ` * _ [ ] < >``.

    ``|`` is left alone; ``table`` escapes it for any cell.
    """
    return _TITLE_SPECIAL.sub(r"\\\1", title)


def _balanced(url: str) -> bool:
    depth = 0
    for ch in url:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def safe_url(url: str) -> str:
    """``url`` safe as an inline link destination.

    Whitespace and ``<``/``>`` are percent-encoded; parentheses are kept when
    balanced (CommonMark allows them) and percent-encoded otherwise.
    """
    url = _URL_UNSAFE.sub(lambda m: "".join(f"%{b:02X}" for b in m[0].encode()), url)
    if not _balanced(url):
        url = url.replace("(", "%28").replace(")", "%29")
    return url


def md_link(title: str, url: str) -> str:
    """``[title](url)`` with the title and URL escaped."""
    return f"[{escape_title(title)}]({safe_url(url)})"


def resolve_citations(
    text: str,
    registry: Mapping[str, Source],
    titles: Mapping[str, str] | None = None,
) -> str:
    """Turn Pandoc citations into Markdown links.

    ``[@a]`` becomes ``[title](url)``; ``[@a; @b]`` becomes
    ``[title a](url a); [title b](url b)``; ``[@a, p. 3]`` becomes
    ``[title](url), p. 3``. ``titles`` overrides the link title per slug (the
    per-use ``source_titles``). Citations inside code are left alone. An
    unknown slug raises ``UnknownSlugError`` (a ``KeyError``).
    """
    titles = titles or {}

    def link(slug: str, locator: str | None) -> str:
        source = lookup(registry, slug)
        out = md_link(titles.get(slug, source["title"]), source["url"])
        return f"{out}, {locator}" if locator else out

    def replace(match: re.Match[str]) -> str:
        return "; ".join(link(s, loc) for s, loc in parse_citation(match.group(1)))

    return _outside_code(text, replace)


def _outside_code(text: str, replace: Callable[[re.Match[str]], str]) -> str:
    """``text`` with every citation outside code passed through ``replace``."""
    pieces: list[str] = []
    last = 0
    spans = [(m.start(), m.end()) for m in _FENCE.finditer(text)]
    for m in _INLINE_CODE.finditer(text):
        if not any(a <= m.start() < b for a, b in spans):
            spans.append((m.start(), m.end()))
    for start, end in sorted(spans):
        if start < last:
            continue
        pieces.append(_CITATION.sub(replace, text[last:start]))
        pieces.append(text[start:end])
        last = end
    pieces.append(_CITATION.sub(replace, text[last:]))
    return "".join(pieces)


def number_citations(text: str, registry: Mapping[str, Source]) -> str:
    """Turn Pandoc citations into numbered links and add a reference list.

    Each ``[@slug]`` becomes ``[[n]](#ref-n)``, numbered per page in order of
    first citation (``[@a; @b]`` becomes ``[1], [2]``; a locator follows the
    number: ``[@a, p. 3]`` becomes ``[1], p. 3``). When the text cites
    anything, a ``## References`` list ends it, one entry per number with the
    anchor ``ref-n`` and the source title linked to its URL. Citations inside
    code are left alone. An unknown slug raises ``UnknownSlugError``.
    """
    numbers: dict[str, int] = {}

    def link(slug: str, locator: str | None) -> str:
        lookup(registry, slug)
        n = numbers.setdefault(slug, len(numbers) + 1)
        out = f"[\\[{n}\\]](#ref-{n})"
        return f"{out}, {locator}" if locator else out

    def replace(match: re.Match[str]) -> str:
        return ", ".join(link(s, loc) for s, loc in parse_citation(match.group(1)))

    body = _outside_code(text, replace)
    if not numbers:
        return body
    entries = [
        f'- <a id="ref-{n}"></a>\\[{n}\\] '
        + md_link(registry[slug]["title"], registry[slug]["url"])
        for slug, n in numbers.items()
    ]
    return body.rstrip("\n") + "\n\n## References\n\n" + "\n".join(entries) + "\n"


@dataclass
class Block:
    """One Markdown block: a heading, paragraph, list or table."""

    kind: str  # h1 | h2 | h3 | para | list | table
    text: str
    #: Row anchors need to know where rules are defined (chapters only).
    section: int = 0


@dataclass
class Section:
    number: int
    key: str
    title: str
    blocks: list[Block]


_UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def table(header: list[str], rows: list[list[str]]) -> str:
    """A pipe table; every row must have the header's column count."""

    def line(cells: list[str]) -> str:
        return "| " + " | ".join(_UNESCAPED_PIPE.sub(r"\\|", c) for c in cells) + " |"

    for row in rows:
        if len(row) != len(header):
            raise ValueError(
                f"table row has {len(row)} cells, header has {len(header)}"
            )
    return "\n".join([line(header), line(["---"] * len(header)), *map(line, rows)])


class _Builder:
    def __init__(
        self, ds: Dataset, registry: Mapping[str, Source], chapter: bool
    ) -> None:
        self.ds = ds
        self.reg = registry
        self.chapter = chapter
        self.rules = ds.rule_by_id()
        self.cats = ds.category_by_id()
        self.meta = ds.meta
        self.tables: dict[str, list[str]] = ds.meta["tables"]
        self.sections = {s["key"]: s for s in ds.meta["sections"]}

    # -- cells -----------------------------------------------------------
    def c(self, text: str, titles: Mapping[str, str] | None = None) -> str:
        return resolve_citations(text, self.reg, titles)

    def links(
        self, slugs: list[str], titles: Mapping[str, str] | None, sep: str
    ) -> str:
        return sep.join(self.c(f"[@{s}]", titles) for s in slugs)

    def evidence(self, item: Rule | Management) -> str:
        if "evidence_text" in item:
            return self.c(item["evidence_text"])
        note = item.get("evidence_note")
        return f"{item['evidence']} ({self.c(note)})" if note else item["evidence"]

    def anchor(self, rule_id: str) -> str:
        return f'<a id="{rule_id.lower()}"></a>{rule_id}' if self.chapter else rule_id

    def rule_label(self, rule_id: str) -> str:
        return (
            "Master rule"
            if rule_id == "Master"
            else f"{rule_id} {self.rules[rule_id]['name']}"
        )

    # -- sections ----------------------------------------------------------
    @staticmethod
    def _num(sec: Mapping[str, object]) -> int:
        return int(str(sec["number"]))

    def heading(self, sec: Mapping[str, object]) -> Block:
        return Block("h2", f"## {sec['number']}. {sec['title']}", self._num(sec))

    def intro(self, text: str | None, number: int) -> list[Block]:
        if not text:
            return []
        return [Block("para", self.c(p), number) for p in text.split("\n\n")]

    def build(self) -> list[Section]:
        makers: dict[str, Callable[[Mapping[str, object]], list[Block]]] = {
            "how_to_read": self.how_to_read,
            "master_rule": self.master_rule,
            "overview": self.overview,
            "domain_index": self.domain_index,
            "glossary": self.glossary,
            "rigor_matrix": self.rigor_matrix,
            "rules": self.rules_section,
            "conflicts": self.conflicts,
            "sources_by_rule": self.sources_by_rule,
            "management_forms": self.management_forms,
            "quotes": self.quotes,
            "method": self.method,
        }
        out: list[Section] = []
        for sec in self.meta["sections"]:
            blocks = [self.heading(sec), *makers[sec["key"]](sec)]
            out.append(Section(sec["number"], sec["key"], sec["title"], blocks))
        return out

    def how_to_read(self, sec: Mapping[str, object]) -> list[Block]:
        text = "\n".join(
            f"- {self.c(item['text'])}" for item in self.meta["how_to_read"]
        )
        return [Block("list", text, self._num(sec))]

    def master_rule(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        m = self.meta["master_rule"]
        regions = m["risk_regions"]
        return [
            Block("list", f"1. {self.c(m['scale'])}\n2. {self.c(m['alarp'])}", n),
            Block(
                "table",
                table(
                    self.tables["master_rule_regions"],
                    [
                        [k, self.c(regions[k])]
                        for k in ("unacceptable", "tolerable", "negligible")
                    ],
                ),
                n,
            ),
            Block("para", self.c(m["management_intro"]), n),
            Block(
                "table",
                table(
                    self.tables["master_rule_terms"],
                    [
                        [
                            self.c(t["engineering"]),
                            self.c(t["management"]),
                            self.c(t["source"]),
                        ]
                        for t in m["management_terms"]
                    ],
                ),
                n,
            ),
        ]

    def overview(self, sec: Mapping[str, object]) -> list[Block]:
        meta = self.meta
        n = self._num(sec)
        qv, am = meta["quick_view"], meta["analogy_map"]
        subsections = sec["subsections"]
        assert isinstance(subsections, dict)
        questions = meta["quick_view_questions"]
        qrows = [
            [f"{cat['id']}. {cat['name']}", self.c(questions[cat["id"]])]
            for cat in self.ds.categories
        ]
        arows = [
            [self.c(r["engineering"]), self.c(r["management"]), self.c(r["role"])]
            for r in am["rows"]
        ]
        lines: list[str] = []
        for cat in self.ds.categories:
            lines.append(
                f"- **{cat['id']}. {cat['name']}** — {self.c(cat['description'])}"
            )
            for rid in cat["rules"]:
                r = self.rules[rid]
                lines.append(f"  - {rid} {r['name']} ({r['strength']})")
        ids = ", ".join(k["id"] for k in self.ds.conflicts)
        lines.append(f"- **K. Conflict rules** — {ids}")
        return [
            *self.intro(self._intro(sec), n),
            Block("h3", f"### {qv['title']}", n),
            *self.intro(qv.get("intro"), n),
            Block("table", table(self.tables["quick_view"], qrows), n),
            Block("h3", f"### {am['title']}", n),
            *self.intro(am.get("intro"), n),
            Block("table", table(self.tables["analogy_map"], arows), n),
            Block("h3", f"### {subsections['rules_per_category']}", n),
            Block("list", "\n".join(lines), n),
        ]

    @staticmethod
    def _intro(sec: Mapping[str, object]) -> str | None:
        value = sec.get("intro")
        return str(value) if value else None

    def domain_index(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        blocks = self.intro(self._intro(sec), n)
        branches: dict[str, list[list[str]]] = {}
        for d in self.ds.domains["domains"]:
            if "rules_text" in d:
                rules_cell = self.c(d["rules_text"])
            else:
                supports = set(d.get("supports", []))
                rules_cell = "; ".join(
                    self.rule_label(rid) + (" (supports)" if rid in supports else "")
                    for rid in d["rules"]
                )
            refs = self.links(d["references"], d.get("reference_titles"), " ")
            branches.setdefault(d["branch"], []).append([d["domain"], rules_cell, refs])
        for branch, rows in branches.items():
            blocks.append(Block("h3", f"### {branch}", n))
            blocks.append(Block("table", table(self.tables["domains"], rows), n))
        cw = sec["checked_without_row"]
        assert isinstance(cw, dict)
        blocks.append(Block("h3", f"### {cw['title']}", n))
        blocks.extend(self.intro(cw.get("intro"), n))
        rows = [
            [x["domain"], self.c(x["note"]), self.c(x["applicable"])]
            for x in self.ds.domains["checked_without_row"]
        ]
        blocks.append(
            Block("table", table(self.tables["checked_without_row"], rows), n)
        )
        return blocks

    def glossary(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        rows = [
            [term, self.c(v["meaning"]), self.c(v["not_same_as"])]
            for term, v in self.ds.glossary.items()
        ]
        return [
            *self.intro(self._intro(sec), n),
            Block("table", table(self.tables["glossary"], rows), n),
        ]

    def rigor_matrix(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        cells = {(r["consequence"], r["uncertainty"]): r for r in self.ds.rigor_matrix}

        def cell(cons: str, unc: str) -> str:
            r = cells[(cons, unc)]
            level = f"Checker level: {r['checker_level']} ({CHECKER_LEVEL_RULE})."
            return f"{', '.join(r['apply'])}. {level}"

        rows = [
            [
                f"**{cons.capitalize()} consequence**",
                cell(cons, "low"),
                cell(cons, "high"),
            ]
            for cons in ("low", "high")
        ]
        return [
            *self.intro(self._intro(sec), n),
            Block("table", table(self.tables["rigor_matrix"], rows), n),
        ]

    def rules_section(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        blocks: list[Block] = []
        for cat in self.ds.categories:
            blocks.append(Block("h3", f"### {cat['id']}. {cat['name']}", n))
            blocks.append(Block("para", self.c(cat["description"]), n))
            main: list[list[str]] = []
            detail: list[list[str]] = []
            for rid in cat["rules"]:
                r = self.rules[rid]
                main.append(
                    [
                        self.anchor(rid),
                        r["name"],
                        r["strength"],
                        self.c(r["if"]),
                        self.c(r["then"]),
                        self.c(r["because"]),
                        self.c(r["example"]),
                    ]
                )
                detail.append(
                    [
                        rid,
                        f"{r['class']} ({CLASS_LETTER[r['class']]}), category "
                        f"{r['category']}: {r['class_note']}",
                        self.c(r["check"]),
                        self.c(r["violation"]),
                        self.related(r),
                        self.evidence(r),
                        self.c(r["source_domain"]),
                    ]
                )
            blocks.append(Block("table", table(self.tables["rules_main"], main), n))
            blocks.append(Block("table", table(self.tables["rules_detail"], detail), n))
        return blocks

    def related(self, r: Rule) -> str:
        if "related_text" in r:
            return self.c(r["related_text"])
        parts = [
            f"{RELATION_LABELS[key]} {', '.join(r['related'][key])}"
            for key in r["related"]
        ]
        return "; ".join(parts)

    def conflicts(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        rows = [
            [
                self.anchor(k["id"]),
                self.c(k["if"]),
                self.c(k["then"]),
                self.c(k["because"]),
                self.c(k["example"]),
                self.c(k["basis"]),
            ]
            for k in self.ds.conflicts
        ]
        return [
            *self.intro(self._intro(sec), n),
            Block("table", table(self.tables["conflicts"], rows), n),
        ]

    def sources_by_rule(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        m = self.meta["master_rule"]
        rows = [["Master rule", self.links(m["sources"], m.get("source_titles"), "; ")]]
        for r in self.ds.rules:
            rows.append(
                [r["id"], self.links(r["sources"], r.get("source_titles"), "; ")]
            )
        return [
            *self.intro(self._intro(sec), n),
            Block("table", table(self.tables["sources_by_rule"], rows), n),
        ]

    def management_forms(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        blocks = self.intro(self._intro(sec), n)
        overrides = sec.get("header_overrides") or {}
        titles = sec.get("category_titles") or {}
        assert isinstance(overrides, dict) and isinstance(titles, dict)
        for cat in self.ds.categories:
            rows: list[list[str]] = []
            for rid in cat["rules"]:
                m = self.rules[rid]["management"]
                if not m:
                    continue
                st = m.get("source_titles")
                src = (
                    self.c(m["sources_text"], st)
                    if "sources_text" in m
                    else self.links(m["sources"], st, "; ")
                )
                rows.append(
                    [
                        rid,
                        m["name"],
                        self.c(m["form_name"]),
                        self.c(m["form"]),
                        self.c(m["example"]),
                        src,
                        self.evidence(m),
                    ]
                )
            if not rows:
                continue
            header = overrides.get(cat["id"]) or self.tables["management_forms"]
            blocks.append(
                Block("h3", f"### {cat['id']}. {titles.get(cat['id'], cat['name'])}", n)
            )
            blocks.append(Block("table", table(header, rows), n))
        return blocks

    def quotes(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        blocks = self.intro(self._intro(sec), n)
        groups = sec["groups"]
        assert isinstance(groups, list)
        for g in groups:
            rows = [self.quote_row(q) for q in self.ds.quotes if q["group"] == g["key"]]
            blocks.append(Block("h3", f"### {g['title']}", n))
            blocks.append(Block("table", table(g["header"], rows), n))
        return blocks

    def quote_row(self, q: Quote) -> list[str]:
        label = q.get("rule_label") or ", ".join(q["rules"])
        st = q.get("source_titles")
        if "sources_text" in q:
            src = self.c(q["sources_text"], st)
        else:
            slugs = ([q["source"]] if q["source"] else []) + q.get("extra_sources", [])
            src = self.links(slugs, st, "; ")
        return [label, src, self.c(q["text"])]

    def method(self, sec: Mapping[str, object]) -> list[Block]:
        n = self._num(sec)
        blocks: list[Block] = []
        for part in self.ds.method:
            blocks.append(Block("h3", f"### {part['section']}", n))
            blocks.append(Block("para", self.c(part["text"]), n))
        return blocks


def counts_line(ds: Dataset) -> str:
    """The ``Version ... · date · counts`` line under the title."""
    by_class = {"universal": 0, "risk-scaled": 0, "conditional": 0}
    for r in ds.rules:
        by_class[r["class"]] += 1
    return (
        f"Version {ds.meta['edition']} · {ds.meta['date']} · {len(ds.rules)} rules "
        f"({by_class['universal']} universal, {by_class['risk-scaled']} risk-scaled, "
        f"{by_class['conditional']} conditional) and "
        f"{len(ds.conflicts)} conflict rules "
        f"in {len(ds.categories)} categories"
    )


def contents_blocks(ds: Dataset) -> list[Block]:
    items = [
        f"{s['number']}. {s.get('contents_title', s['title'])}"
        for s in ds.meta["sections"]
    ]
    return [Block("h2", "## Contents"), Block("list", "\n".join(items))]


def build_sections(
    ds: Dataset, registry: Mapping[str, Source], chapter: bool
) -> list[Section]:
    return _Builder(ds, registry, chapter).build()


def render_single(ds: Dataset, registry: Mapping[str, Source]) -> str:
    """The single-file Markdown (edition-9 layout, version line from ``meta``)."""
    blocks = [
        Block("h1", f"# {ds.meta['title']}"),
        Block("para", counts_line(ds)),
        *contents_blocks(ds),
    ]
    for sec in build_sections(ds, registry, chapter=False):
        blocks.extend(sec.blocks)
    quirks = {
        (q["section"], q["block"], q["starts_with"]): q["blank_lines_before"]
        for q in ds.meta["layout_quirks"]
    }
    lines: list[str] = []
    for i, block in enumerate(blocks):
        blank = _quirk_blanks(quirks, block) if i else 0
        lines.extend([""] * blank)
        lines.extend(block.text.split("\n"))
    return "\n".join(lines) + "\n"


def _quirk_blanks(quirks: Mapping[tuple[int, str, str], int], block: Block) -> int:
    first = block.text.split("\n", 1)[0]
    for (section, kind, starts), blanks in quirks.items():
        if section == block.section and kind == block.kind and first.startswith(starts):
            return blanks
    return 1


def chapter_filename(ds: Dataset, number: int) -> str:
    sec = next(s for s in ds.meta["sections"] if s["number"] == number)
    return f"{number:02d}-{sec['key'].replace('_', '-')}.md"


def _section_number(ds: Dataset, key: str) -> int:
    """The number of the section with ``key``."""
    return next(int(s["number"]) for s in ds.meta["sections"] if s["key"] == key)


# Skipped when linking: inline code, an existing inline link (link text may
# hold escaped brackets; the destination is ``<...>`` or holds balanced
# parentheses to one nesting level, as in CommonMark) and a rule anchor.
_SKIP = re.compile(
    r"`[^`\n]*`"
    r"|\[(?:\\.|[^\]\\])*\]\((?:<[^<>\n]*>|[^()]|\([^()]*\))*\)"
    r"|<a id=\"[^\"]*\"></a>[A-Z]\d+"
)
_SECTION_REF = re.compile(r"\b([Ss]ection) (\d{1,2})\b(?![.\d]\d)")


class _RefLinker:
    """Links ``section N`` and rule IDs; the per-chapter lookups are built once."""

    def __init__(self, ds: Dataset, current: int) -> None:
        self.ds = ds
        self.current = current
        self.numbers = {s["number"] for s in ds.meta["sections"]}
        self.ids = ds.all_ids()
        self.prefixes = list(ds.meta["id_prefixes"])
        self.conflicts = {k["id"] for k in ds.conflicts}
        self.rules_number = _section_number(ds, "rules")
        self.conflicts_number = _section_number(ds, "conflicts")
        self.filenames = {n: chapter_filename(ds, n) for n in self.numbers}

    def _sec_sub(self, m: re.Match[str]) -> str:
        num = int(m.group(2))
        if num not in self.numbers:
            return m.group(0)
        return f"[{m.group(1)} {num}]({self.filenames[num]})"

    def _href(self, rid: str) -> str:
        number = self.conflicts_number if rid in self.conflicts else self.rules_number
        anchor = f"#{rid.lower()}"
        return anchor if self.current == number else f"{self.filenames[number]}{anchor}"

    def _link(self, piece: str) -> str:
        return link_ids(
            _SECTION_REF.sub(self._sec_sub, piece), self.ids, self.prefixes, self._href
        )

    def line(self, text: str) -> str:
        """``text`` with references linked, outside existing links and code."""
        out: list[str] = []
        last = 0
        for m in _SKIP.finditer(text):
            out.append(self._link(text[last : m.start()]))
            out.append(m.group(0))
            last = m.end()
        out.append(self._link(text[last:]))
        return "".join(out)


def _link_block(
    text: str, ds: Dataset, current: int, linker: _RefLinker | None = None
) -> list[str]:
    """Link references line by line, leaving fenced code blocks untouched."""
    linker = linker or _RefLinker(ds, current)
    out: list[str] = []
    fence: str | None = None
    for line in text.split("\n"):
        marker = line.lstrip()[:3]
        if fence is None and marker in ("```", "~~~"):
            fence = marker
            out.append(line)
        elif fence is not None:
            if marker == fence:
                fence = None
            out.append(line)
        else:
            out.append(linker.line(line))
    return out


def render_chapters(ds: Dataset, registry: Mapping[str, Source]) -> dict[str, str]:
    """``{filename: text}`` for ``publication/chapters/``: one file per section,
    plus ``README.md`` (title, version line and linked contents)."""
    files: dict[str, str] = {}
    toc: list[str] = []
    for sec in build_sections(ds, registry, chapter=True):
        name = chapter_filename(ds, sec.number)
        meta_sec = next(s for s in ds.meta["sections"] if s["number"] == sec.number)
        toc.append(
            f"{sec.number}. [{meta_sec.get('contents_title', sec.title)}]({name})"
        )
        linker = _RefLinker(ds, sec.number)
        lines: list[str] = []
        for i, block in enumerate(sec.blocks):
            if i:
                lines.append("")
            if block.kind in ("h2", "h3"):
                lines.append(block.text[1:])  # demote one level under the chapter H1
            else:
                lines.extend(_link_block(block.text, ds, sec.number, linker))
        files[name] = "\n".join(lines) + "\n"
    head = [f"# {ds.meta['title']}", "", counts_line(ds), "", "## Contents", "", *toc]
    files["README.md"] = "\n".join(head) + "\n"
    return files
