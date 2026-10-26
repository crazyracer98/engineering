"""Build the PDF paper: Markdown -> Pandoc (citeproc, IEEE CSL) -> Typst -> PDF.

``build(out)`` writes the PDF at ``out`` and the CSL-JSON bibliography at
``out.with_name("references.json")``; the intermediate ``paper.md`` and
``paper.typ`` go next to them. See ``paper/README.md`` for how the paper is
assembled.

The paper leaves ``[@slug]`` citations to citeproc. The dataset's prose
overrides used by the Markdown round trip (``source_titles``,
``sources_text``) are not used here: every source is cited as ``[@slug]``.
"""

from __future__ import annotations

import json
import re
import subprocess
import warnings
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pypandoc
import typst

from taxonomy.ids import link_ids
from taxonomy.load import find_root, load_dataset, load_registry, load_yaml
from taxonomy.model import (
    CHECKER_LEVEL_RULE,
    RELATION_LABELS,
    Dataset,
    Management,
    Rule,
    Source,
)
from taxonomy.render_markdown import table

#: Hand-written paper sections, in paper order, around the generated ones.
SECTIONS_BEFORE_METHOD = ("abstract.md", "01-introduction.md", "02-related-work.md")
SECTIONS_AFTER_RESULTS = ("06-discussion.md", "07-conclusion.md")

#: Where the edition-9 section numbers of the dataset's prose now live.
SECTION_MAP = {
    1: "Section 4.1",
    2: "Section 4.2",
    3: "Section 4.3",
    4: "Appendix B",
    5: "Appendix A",
    6: "Section 4.4",
    7: "Section 4.5",
    8: "Section 5",
    9: "the Sources line of each rule card",
    10: "Appendix C",
    11: "Appendix D",
    12: "Appendix E",
}

_SECTION_REF = re.compile(
    r"\b([Ss])ections?\s+(\d{1,2})((?:\s*(?:,|and)\s*\d{1,2})*)(?!\d|\.\d)"
)
#: A relative link or image (any target without a URL scheme such as ``https:``
#: or ``mailto:``, and not an in-page ``#anchor``). ``method_markdown`` reduces
#: it to its text; an image, which cannot be fetched from the repository, to
#: its alt text.
_REL_LINK = re.compile(r"!?\[([^\]]*)\]\((?![a-zA-Z][a-zA-Z0-9+.-]*:|#)[^)]*\)")
_APPLIED = "> **Applied in this taxonomy:**"
#: The published history page; the paper cannot link ``history.md``.
HISTORY_URL = "https://crazyracer98.github.io/engineering/history/"
#: An apostrophe after a digit or a link ("P71's") in Pandoc's Typst output.
#: Typst's smart quotes would typeset it as a prime, so it becomes ``’``.
_DIGIT_APOSTROPHE = re.compile(r"([0-9]|\])'(?=[A-Za-z])")

#: Hosts whose pages are journal articles, for the CSL ``type`` mapping.
_JOURNAL_HOSTS = (
    "doi.org",
    "nejm.org",
    "bmj.com",
    "pubmed.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "sciencedirect.com",
    "springer.com",
    "tandfonline.com",
    "jamanetwork.com",
    "thelancet.com",
)

CSL_RELATIVE = "paper/csl/ieee.csl"
TEMPLATE_RELATIVE = "paper/template.typ"


# -- CSL-JSON ---------------------------------------------------------------


def csl_type(source: Source) -> str:
    """The CSL item type of a source: simple URL/notes heuristics.

    ``article-journal`` for known journal hosts, ``book`` when the notes give
    an ISBN, ``report`` for a PDF, and ``webpage`` otherwise.
    """
    url = source.get("url", "")
    host = re.sub(r"^https?://(www\.)?", "", url).split("/", 1)[0].lower()
    if any(host == h or host.endswith("." + h) for h in _JOURNAL_HOSTS):
        return "article-journal"
    if "ISBN" in (source.get("notes") or ""):
        return "book"
    if url.lower().split("?", 1)[0].endswith(".pdf"):
        return "report"
    return "webpage"


def csl_item(source: Source) -> dict[str, Any]:
    """One CSL-JSON item: ``id`` (the slug), ``type``, ``title``, ``URL``,
    ``author`` (CSL name objects), ``issued`` (from ``year``), ``publisher`` and ``accessed`` when present."""
    item: dict[str, Any] = {
        "id": source["slug"],
        "type": csl_type(source),
        "title": source["title"],
        "URL": source["url"],
    }
    if source.get("author"):
        item["author"] = [dict(name) for name in source["author"]]
    if source.get("year"):
        item["issued"] = {"date-parts": [[int(source["year"] or 0)]]}
    if source.get("publisher"):
        item["publisher"] = source["publisher"]
    accessed = source.get("accessed")
    if accessed:
        item["accessed"] = {
            "date-parts": [[int(part) for part in str(accessed).split("-")]]
        }
    return item


def csl_json(registry: Mapping[str, Source]) -> list[dict[str, Any]]:
    """CSL-JSON items for every source of the merged registry, by slug."""
    return [csl_item(registry[slug]) for slug in sorted(registry)]


def write_csl_json(root: Path, out: Path) -> None:
    """Write the CSL-JSON of ``data/sources.yaml``, ``paper/references-extra.yaml``
    and ``docs/methodology-references.yaml`` to ``out``."""
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(csl_json(load_registry(root)), indent=2, ensure_ascii=False)
    out.write_text(text + "\n", encoding="utf-8")


# -- Markdown assembly --------------------------------------------------------


def paper_sections(text: str) -> str:
    """Rewrite edition-9 section references ("section 6", "sections 9, 11 and 12")
    in dataset prose to where that content sits in the paper."""

    def sub(match: re.Match[str]) -> str:
        nums = [int(match.group(2))] + [
            int(n) for n in re.findall(r"\d+", match.group(3))
        ]
        if any(n not in SECTION_MAP for n in nums):
            return match.group(0)
        names = [SECTION_MAP[n] for n in nums]
        if match.group(1) == "S":
            names[0] = names[0][0].upper() + names[0][1:]
        return (
            names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        )

    return _SECTION_REF.sub(sub, text)


def method_markdown(text: str) -> str:
    """``docs/methodology.md`` as the paper's Method section body.

    The ``# Methodology`` title is dropped (the section heading replaces it;
    the ``##`` phase headings become ``3.x``). Each ``> **Applied in this
    taxonomy:**`` blockquote becomes a raw-Typst ``#appliedbox[ ... ]`` block
    (styled in ``paper/template.typ``), with edition-9 section numbers mapped
    to the paper's. Relative links to other repository files become plain text.
    """
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith(_APPLIED):
            quote: list[str] = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(re.sub(r"^> ?", "", lines[i]))
                i += 1
            out += [*_typst_open("appliedbox"), paper_sections("\n".join(quote))]
            out += _typst_close()
            continue
        out.append(lines[i])
        i += 1
    text = "\n".join(out).replace("](history.md)", f"]({HISTORY_URL})")
    return _REL_LINK.sub(r"\1", text).strip() + "\n"


def _typst_open(function: str) -> list[str]:
    return ["", "```{=typst}", f"#{function}[", "```", ""]


def _typst_close() -> list[str]:
    return ["", "```{=typst}", "]", "```", ""]


def _cite(slugs: list[str]) -> str:
    return "[" + "; ".join(f"@{s}" for s in slugs) + "]" if slugs else ""


def _pipe_table(header: list[str], rows: list[list[str]], weights: list[int]) -> str:
    """``table`` with the separator row's dashes set to relative column widths."""
    lines = table(header, rows).split("\n")
    lines[1] = "|" + "|".join("-" * w for w in weights) + "|"
    return "\n".join(lines)


class _Paper:
    def __init__(self, ds: Dataset) -> None:
        self.ds = ds
        self.rules = ds.rule_by_id()
        self.ids = ds.all_ids()
        self.meta = ds.meta
        self.tables: dict[str, list[str]] = ds.meta["tables"]

    # -- text helpers ---------------------------------------------------------
    @staticmethod
    def c(text: str | None) -> str:
        """Dataset prose for the paper: section references mapped, citations kept."""
        return paper_sections(text or "").strip()

    def link_ids(self, text: str) -> str:
        """Link rule and conflict-rule IDs in ``text`` to their cards."""
        return link_ids(
            text, self.ids, self.meta["id_prefixes"], lambda rid: f"#{rid.lower()}"
        )

    def evidence(self, item: Rule | Management) -> str:
        note = item.get("evidence_note")
        return f"{item['evidence']} ({self.c(note)})" if note else item["evidence"]

    @staticmethod
    def terms(fields: list[tuple[str, str | None]]) -> str:
        """A definition list (rendered as label and text columns in a card)."""
        return "\n\n".join(
            f"{label}\n:   {' '.join(text.split())}" for label, text in fields if text
        )

    def card(self, heading: str, tagline: str | None, fields: str) -> str:
        parts = [heading, "", *_typst_open("rulecard")]
        if tagline:
            parts += [tagline, ""]
        parts += [fields, *_typst_close()]
        return "\n".join(parts)

    # -- section 4: the taxonomy -------------------------------------------------
    def taxonomy(self) -> str:
        parts = [
            "# The taxonomy {#sec-taxonomy}",
            self.how_to_read(),
            self.master_rule(),
            self.overview(),
            self.rigor_matrix(),
            self.rules_by_category(),
        ]
        return "\n\n".join(parts)

    def how_to_read(self) -> str:
        items = "\n".join(
            f"- {self.link_ids(self.c(item['text']))}"
            for item in self.meta["how_to_read"]
        )
        return "\n\n".join(["## How to read the rules {#sec-howto}", items])

    def master_rule(self) -> str:
        m = self.meta["master_rule"]
        regions = m["risk_regions"]
        region_rows = [
            [k, self.c(regions[k])] for k in ("unacceptable", "tolerable", "negligible")
        ]
        term_rows = [
            [self.c(t["engineering"]), self.c(t["management"]), self.c(t["source"])]
            for t in m["management_terms"]
        ]
        return "\n\n".join(
            [
                "## Master rule {#sec-master-rule}",
                f"1. {self.c(m['scale'])}\n2. {self.c(m['alarp'])}",
                f"Sources: {_cite(m['sources'])}.",
                _pipe_table(self.tables["master_rule_regions"], region_rows, [20, 60]),
                self.c(m["management_intro"]),
                _pipe_table(self.tables["master_rule_terms"], term_rows, [25, 40, 35]),
            ]
        )

    def overview(self) -> str:
        meta = self.meta
        sec = next(s for s in meta["sections"] if s["key"] == "overview")
        qv = meta["quick_view"]
        questions = meta["quick_view_questions"]
        qrows = [
            [f"{cat['id']}. {cat['name']}", self.c(questions[cat["id"]])]
            for cat in self.ds.categories
        ]
        lines: list[str] = []
        for cat in self.ds.categories:
            lines.append(
                f"- **{cat['id']}. {cat['name']}**: {self.c(cat['description'])}"
            )
            for rid in cat["rules"]:
                r = self.rules[rid]
                lines.append(f"  - {self.link_ids(rid)} {r['name']} ({r['strength']})")
        ids = ", ".join(self.link_ids(k["id"]) for k in self.ds.conflicts)
        lines.append(f"- **K. Conflict rules** (Section 5): {ids}")
        return "\n\n".join(
            [
                "## Overview and quick view {#sec-overview}",
                self.c(sec.get("intro")),
                f"### {qv['title']} {{#sec-quick-view}}",
                self.c(qv.get("intro")),
                _pipe_table(self.tables["quick_view"], qrows, [30, 70]),
                "### Rules per category {#sec-rules-per-category}",
                "\n".join(lines),
            ]
        )

    def rigor_matrix(self) -> str:
        sec = next(s for s in self.meta["sections"] if s["key"] == "rigor_matrix")
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
        return "\n\n".join(
            [
                "## Rigor matrix {#sec-rigor-matrix}",
                self.c(sec.get("intro")),
                _pipe_table(self.tables["rigor_matrix"], rows, [20, 40, 40]),
            ]
        )

    def related(self, r: Rule) -> str:
        if "related_text" in r:
            return self.link_ids(self.c(r["related_text"]))
        return self.link_ids(
            "; ".join(
                f"{RELATION_LABELS[key]} {', '.join(r['related'][key])}"
                for key in r["related"]
            )
        )

    def rule_card(self, r: Rule) -> str:
        rid = r["id"]
        tagline = (
            f"**{r['strength']}** · {r['class']} ({r['class'][0].upper()}) · "
            f"category {r['category']} · evidence: {r['evidence']}"
        )
        fields = self.terms(
            [
                ("IF", self.c(r["if"])),
                ("THEN", self.c(r["then"])),
                ("BECAUSE", self.c(r["because"])),
                ("Example", self.c(r["example"])),
                ("Counterexample", self.c(r.get("counterexample"))),
                ("Check", self.c(r["check"])),
                ("Violation", self.c(r["violation"])),
                ("Related", self.related(r)),
                ("Evidence", self.evidence(r)),
                ("Sources", _cite(r["sources"]) + "."),
                ("Source domain", self.c(r["source_domain"])),
                ("Class (why)", self.c(r["class_note"])),
                ("Notes", self.c(r.get("notes"))),
            ]
        )
        heading = f"#### {rid}. {r['name']} {{#{rid.lower()} .unnumbered}}"
        return self.card(heading, tagline, fields)

    def rules_by_category(self) -> str:
        parts = ["## Rules by category {#sec-rules}"]
        for cat in self.ds.categories:
            parts.append(f"### {cat['id']}. {cat['name']} {{#cat-{cat['id'].lower()}}}")
            parts.append(self.c(cat["description"]))
            parts.extend(self.rule_card(self.rules[rid]) for rid in cat["rules"])
        return "\n\n".join(parts)

    # -- section 5: conflicts and analogy map ------------------------------------
    def conflicts(self) -> str:
        sec = next(s for s in self.meta["sections"] if s["key"] == "conflicts")
        am = self.meta["analogy_map"]
        arows = [
            [self.c(r["engineering"]), self.c(r["management"]), self.c(r["role"])]
            for r in am["rows"]
        ]
        parts = [
            "# Conflict rules and the analogy map {#sec-conflicts}",
            "## Conflict rules {#sec-k-rules}",
            self.c(sec.get("intro")) or self.meta["id_prefixes"]["K"]["description"],
        ]
        for k in self.ds.conflicts:
            fields = self.terms(
                [
                    ("IF", self.link_ids(self.c(k["if"]))),
                    ("THEN", self.link_ids(self.c(k["then"]))),
                    ("BECAUSE", self.link_ids(self.c(k["because"]))),
                    ("Example", self.link_ids(self.c(k["example"]))),
                    ("Basis", self.c(k["basis"])),
                    ("Rules", self.link_ids(", ".join(k["rules"]))),
                ]
            )
            parts.append(
                self.card(
                    f"### {k['id']} {{#{k['id'].lower()} .unnumbered}}", None, fields
                )
            )
        parts += [
            "## Analogy map {#sec-analogy-map}",
            self.c(am.get("intro")),
            _pipe_table(self.tables["analogy_map"], arows, [30, 35, 35]),
        ]
        return "\n\n".join(parts)

    # -- appendices ----------------------------------------------------------------
    def appendices(self) -> str:
        return "\n\n".join(
            [
                "\n".join(["```{=typst}", "#show: appendix", "```"]),
                self.glossary(),
                self.domain_index(),
                self.management_forms(),
                self.quotes(),
                self.limits(),
            ]
        )

    def intro_of(self, key: str) -> str:
        sec = next(s for s in self.meta["sections"] if s["key"] == key)
        return self.link_ids(self.c(sec.get("intro")))

    def glossary(self) -> str:
        rows = [
            [term, self.c(v["meaning"]), self.c(v["not_same_as"])]
            for term, v in self.ds.glossary.items()
        ]
        return "\n\n".join(
            [
                "# Glossary {#app-glossary}",
                self.intro_of("glossary"),
                _pipe_table(self.tables["glossary"], rows, [20, 50, 30]),
            ]
        )

    def domain_index(self) -> str:
        sec = next(s for s in self.meta["sections"] if s["key"] == "domain_index")
        parts = ["# Domain index {#app-domains}", self.intro_of("domain_index")]
        branches: dict[str, list[list[str]]] = {}
        for d in self.ds.domains["domains"]:
            if "rules_text" in d:
                rules_cell = self.link_ids(self.c(d["rules_text"]))
            else:
                supports = set(d.get("supports", []))
                rules_cell = "; ".join(
                    self.link_ids(rid) + (" (supports)" if rid in supports else "")
                    for rid in d["rules"]
                )
            branches.setdefault(d["branch"], []).append(
                [d["domain"], rules_cell, _cite(d["references"])]
            )
        for branch, rows in branches.items():
            parts.append(f"## {branch}")
            parts.append(
                _pipe_table(
                    [self.tables["domains"][0], "Rules", self.tables["domains"][2]],
                    rows,
                    [30, 30, 40],
                )
            )
        cw = sec["checked_without_row"]
        assert isinstance(cw, dict)
        parts += [f"## {cw['title']} {{#app-checked}}", self.c(cw.get("intro"))]
        crows = [
            [
                x["domain"],
                x["reason"].replace("-", " "),
                self.c(x["note"]),
                self.link_ids(self.c(x["applicable"])),
            ]
            for x in self.ds.domains["checked_without_row"]
        ]
        parts.append(
            _pipe_table(
                ["Domain", "Reason", "Note", "Rules that apply anyway"],
                crows,
                [22, 12, 31, 35],
            )
        )
        return "\n\n".join(parts)

    def management_forms(self) -> str:
        sec = next(s for s in self.meta["sections"] if s["key"] == "management_forms")
        titles = sec.get("category_titles") or {}
        parts = [
            "# Management form of each rule {#app-management}",
            self.intro_of("management_forms"),
        ]
        for cat in self.ds.categories:
            rows: list[list[str]] = []
            for rid in cat["rules"]:
                m = self.rules[rid]["management"]
                if not m:
                    continue
                # A row without sources prints its sources_text ("cross-reference
                # only"), never an empty citation.
                sources = _cite(m["sources"]) or self.c(m.get("sources_text"))
                rows.append(
                    [
                        f"{self.link_ids(rid)} {m['name']}",
                        f"**{self.c(m['form_name'])}**: {self.c(m['form'])}. "
                        f"*Example:* {self.c(m['example'])}",
                        f"{sources}. Evidence: {self.evidence(m)}.",
                    ]
                )
            if not rows:
                continue
            parts.append(
                f"## {cat['id']}. {titles.get(cat['id'], cat['name'])} "
                f"{{#app-mgmt-{cat['id'].lower()}}}"
            )
            parts.append(
                _pipe_table(
                    ["Rule", "Management form", "Sources and evidence"],
                    rows,
                    [22, 52, 26],
                )
            )
        return "\n\n".join(parts)

    def quotes(self) -> str:
        sec = next(s for s in self.meta["sections"] if s["key"] == "quotes")
        parts = ["# Direct quotes {#app-quotes}", self.intro_of("quotes")]
        for g in sec["groups"]:
            parts.append(f"## {g['title']}")
            for q in self.ds.quotes:
                if q["group"] != g["key"] or q.get("placeholder"):
                    continue
                label = q.get("rule_label") or ", ".join(q["rules"])
                source = q.get("source")
                slugs: list[str] = ([source] if source else []) + q.get(
                    "extra_sources", []
                )
                locator = f" ({q['locator']})" if q.get("locator") else ""
                parts.append(
                    f"**{q['id']}: {self.link_ids(label)}** {_cite(slugs)}{locator}"
                )
                # verbatim quote: never rewritten (no section-reference mapping)
                parts.append("> " + q["text"].strip().replace("\n", "\n> "))
        return "\n\n".join(parts)

    def limits(self) -> str:
        blocks = {part["section"]: part["text"] for part in self.ds.method}
        return "\n\n".join(
            [
                "# Limits and source quality {#app-limits}",
                "These are the limits recorded with the dataset (Section 6 discusses "
                "what they mean for the claims of this paper).",
                "## Limits {#app-limits-list}",
                self.link_ids(self.c(blocks["Limits"])),
                "## Source quality {#app-source-quality}",
                self.link_ids(self.c(blocks["Source quality"])),
            ]
        )


def front_matter(root: Path, ds: Dataset) -> dict[str, Any]:
    """The Pandoc metadata block: ``paper/metadata.yaml`` plus the dataset's date.

    Raises ``ValueError`` when the paper's edition differs from ``meta.edition``.
    """
    metadata = dict(load_yaml(root / "paper" / "metadata.yaml"))
    if str(metadata["edition"]) != str(ds.meta["edition"]):
        raise ValueError(
            f"paper/metadata.yaml edition {metadata['edition']!r} differs from "
            f"data/meta.yaml edition {ds.meta['edition']!r}"
        )
    metadata["edition"] = str(ds.meta["edition"])
    metadata["date"] = str(ds.meta["date"])
    metadata["link-citations"] = True
    return metadata


def assemble(root: Path) -> str:
    """The whole paper as one Pandoc Markdown document (YAML block first)."""
    ds = load_dataset(root)
    sections = root / "paper" / "sections"

    def prose(name: str) -> str:
        return (sections / name).read_text(encoding="utf-8").strip()

    paper = _Paper(ds)
    method_text = (root / "docs" / "methodology.md").read_text(encoding="utf-8")
    parts = [
        "---\n" + json.dumps(front_matter(root, ds), indent=2) + "\n---",
        *(prose(name) for name in SECTIONS_BEFORE_METHOD),
        "# Method {#sec-method}\n\n" + method_markdown(method_text),
        paper.taxonomy(),
        paper.conflicts(),
        *(prose(name) for name in SECTIONS_AFTER_RESULTS),
        paper.appendices(),
        "# References {.unnumbered #references}\n\n::: {#refs}\n:::",
    ]
    return "\n\n".join(parts) + "\n"


# -- Pandoc and Typst -------------------------------------------------------------


def _typst_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def pandoc_variables(meta: Mapping[str, Any]) -> dict[str, str]:
    """Raw Typst values for the template's PDF-metadata variables."""
    date = datetime.fromisoformat(str(meta["date"]))
    keywords = ", ".join(_typst_string(str(k)) for k in meta["keywords"])
    return {
        "pdf-title": _typst_string(str(meta["title"])),
        "pdf-author": _typst_string(str(meta["author"])),
        "pdf-keywords": f"({keywords},)",
        "pdf-date": (
            f"datetime(year: {date.year}, month: {date.month}, day: {date.day})"
        ),
    }


def run_pandoc(
    markdown: Path,
    refs: Path,
    csl: Path,
    template: Path,
    typ: Path,
    variables: Mapping[str, str],
) -> None:
    """Markdown to Typst with citeproc. Any Pandoc warning (for instance
    ``citeproc: citation ... not found``) or error raises ``RuntimeError``."""
    args = [
        pypandoc.get_pandoc_path(),
        "--from=markdown-tex_math_dollars-raw_tex",
        "--to=typst",
        "--standalone",
        "--citeproc",
        f"--bibliography={refs}",
        f"--csl={csl}",
        f"--template={template}",
        "--toc",
        "--toc-depth=2",
        "--fail-if-warnings",
        f"--output={typ}",
        *(f"--variable={k}:{v}" for k, v in variables.items()),
        str(markdown),
    ]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0 or result.stderr.strip():
        raise RuntimeError(
            f"pandoc failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )
    typ.write_text(typographic_apostrophes(typ.read_text("utf-8")), encoding="utf-8")


def typographic_apostrophes(typst_source: str) -> str:
    """Replace a straight apostrophe after a digit or ``]`` ("P71's") by ``’``."""
    return _DIGIT_APOSTROPHE.sub("\\1\u2019", typst_source)


def compile_typst(typ: Path, out: Path, date: str) -> None:
    """Typst to a reproducible PDF/A-2b with Typst's bundled fonts only.

    Typst warnings and errors raise ``RuntimeError``.
    """
    stamp = datetime.fromisoformat(date).replace(tzinfo=UTC)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            typst.compile(
                str(typ),
                output=str(out),
                root=str(typ.parent),
                ignore_system_fonts=True,
                pdf_standards=["a-2b"],
                timestamp=stamp,
            )
        except typst.TypstError as exc:
            raise RuntimeError(f"typst failed:\n{exc.diagnostic or exc}") from exc
    if caught:
        details = "\n".join(str(w.message) for w in caught)
        raise RuntimeError(f"typst warnings:\n{details}")


def build(out: Path, root: Path | None = None) -> None:
    """Build the PDF at ``out`` and ``references.json`` next to it.

    The intermediate ``paper.md`` and ``paper.typ`` are written next to ``out``
    (``build/`` in the usual ``--out build/paper.pdf``). ``root`` defaults to
    the repository found from the working directory.
    """
    root = root or find_root()
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    refs = out.with_name("references.json")
    write_csl_json(root, refs)

    markdown = out.with_name("paper.md")
    markdown.write_text(assemble(root), encoding="utf-8")
    meta = front_matter(root, load_dataset(root))
    typ = out.with_name("paper.typ")
    run_pandoc(
        markdown,
        refs,
        root / CSL_RELATIVE,
        root / TEMPLATE_RELATIVE,
        typ,
        pandoc_variables(meta),
    )
    compile_typst(typ, out, str(meta["date"]))
