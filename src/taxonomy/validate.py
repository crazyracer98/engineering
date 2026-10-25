"""Dataset integrity checks (NFR-0001).

``run_checks(root)`` returns a list of ``Finding``; an empty list means the
dataset is clean. Every check is a function ``(Context) -> list[str]`` of
messages and is registered in ``CHECKS`` under its name.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from taxonomy.ids import id_finder, id_key, id_pattern, prefix_alt
from taxonomy.load import (
    DATA_STEMS,
    REGISTRY_FILES,
    load_dataset,
    load_registry_files,
    load_schema,
    load_yaml,
)
from taxonomy.model import Dataset, Source
from taxonomy.render_markdown import (
    build_sections,
    citation_slugs,
)

#: Data file stem -> schema stem is the identity; these files use ``sources``.
EXTRA_REGISTRIES = dict.fromkeys(REGISTRY_FILES[1:], "sources")

#: Relation pairs that must not both hold between the same two rules.
#: Supportive relations contradict ``conflicts_with`` between the same rules.
SUPPORTIVE = (
    "depends_on",
    "strengthens",
    "strengthened_by",
    "checks",
    "checked_by",
    "scaled_by",
)


@dataclass(frozen=True)
class Finding:
    """One failed check."""

    check: str
    message: str

    def __str__(self) -> str:
        return f"[{self.check}] {self.message}"


@dataclass
class Context:
    root: Path
    ds: Dataset
    #: ``(relative path, entries)`` per registry file.
    registries: list[tuple[str, list[Source]]]
    #: Merged slug -> Source (first wins; duplicates are reported separately).
    registry: dict[str, Source] = field(default_factory=dict)


# -- text sources for citations ---------------------------------------------------


def _strings(value: Any, path: str = "") -> list[tuple[str, str]]:
    """Every string below ``value`` with a dotted path."""
    if isinstance(value, str):
        return [(path, value)]
    out: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for k, v in value.items():
            out.extend(_strings(v, f"{path}.{k}" if path else str(k)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.extend(_strings(v, f"{path}[{i}]"))
    return out


def prose_files(root: Path) -> list[Path]:
    """Markdown and YAML files that may cite ``[@slug]`` outside ``data/``."""
    files: list[Path] = []
    for sub in ("paper", "docs"):
        base = root / sub
        if base.is_dir():
            files.extend(
                p
                for p in sorted(base.rglob("*"))
                if p.suffix in (".md", ".yaml")
                and "plans" not in p.relative_to(base).parts
            )
    return files


def cited_texts(ctx: Context) -> list[tuple[str, str]]:
    """``(location, text)`` for all prose that may carry citations."""
    out = [
        (f"data/{stem}.yaml:{p}", s)
        for stem, v in ctx.ds.raw.items()
        for p, s in _strings(v)
    ]
    for path in prose_files(ctx.root):
        rel = str(path.relative_to(ctx.root))
        if path.suffix == ".md":
            out.append((rel, path.read_text(encoding="utf-8")))
        else:
            out.extend((f"{rel}:{p}", s) for p, s in _strings(load_yaml(path)))
    return out


# -- checks ----------------------------------------------------------------------------


def schema_findings(root: Path) -> list[str]:
    """Validate each data file and extra registry on its own.

    A missing or invalid schema, or a file that fails to load, is a message for
    that file; the other files are still validated.
    """
    msgs: list[str] = []
    targets = [(f"data/{stem}.yaml", stem) for stem in DATA_STEMS]
    targets += [
        (rel, stem) for rel, stem in EXTRA_REGISTRIES.items() if (root / rel).is_file()
    ]
    for rel, stem in targets:
        try:
            schema = load_schema(root, stem)
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # OSError, JSONDecodeError, SchemaError
            msgs.append(
                f"schema/{stem}.schema.json (for {rel}) is missing or not a valid "
                f"JSON Schema: {type(exc).__name__}: {exc}"
            )
            continue
        try:
            data = load_yaml(root / rel)
        except Exception as exc:
            msgs.append(f"{rel} cannot be loaded: {exc}")
            continue
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for err in sorted(
            validator.iter_errors(data), key=lambda e: list(e.absolute_path)
        ):
            where = "/".join(str(p) for p in err.absolute_path) or "(root)"
            msgs.append(f"{rel} at {where}: {err.message}")
    return msgs


def check_schema(ctx: Context) -> list[str]:
    return schema_findings(ctx.root)


def check_unique_ids(ctx: Context) -> list[str]:
    msgs: list[str] = []
    groups = {
        "rules.yaml": [r["id"] for r in ctx.ds.rules],
        "conflicts.yaml": [k["id"] for k in ctx.ds.conflicts],
        "quotes.yaml": [q["id"] for q in ctx.ds.quotes],
        "categories.yaml": [c["id"] for c in ctx.ds.categories],
    }
    for name, ids in groups.items():
        seen: set[str] = set()
        for i in ids:
            if i in seen:
                msgs.append(f"duplicate ID {i} in {name}")
            seen.add(i)
    rule_ids = set(groups["rules.yaml"])
    for k in groups["conflicts.yaml"]:
        if k in rule_ids:
            msgs.append(f"conflict ID {k} is also a rule ID")
    return msgs


def check_related_targets(ctx: Context) -> list[str]:
    ids = ctx.ds.all_ids()
    msgs: list[str] = []
    for r in ctx.ds.rules:
        for rel, targets in r["related"].items():
            for t in targets:
                if t not in ids:
                    msgs.append(f"{r['id']} {rel} {t}: no such rule")
    return msgs


def check_id_references(ctx: Context) -> list[str]:
    """Other places that name rules: categories, domains, quotes, exceptions."""
    ds = ctx.ds
    ids = ds.all_ids()
    msgs: list[str] = []

    def need(where: str, rid: str, allow_master: bool = False) -> None:
        if rid not in ids and not (allow_master and rid == "Master"):
            msgs.append(f"{where} names unknown rule {rid}")

    for c in ds.categories:
        for rid in c["rules"]:
            need(f"category {c['id']}", rid)
    for k in ds.conflicts:
        for rid in k["rules"]:
            need(f"conflict {k['id']}", rid)
    for d in ds.domains["domains"]:
        for rid in [*d["rules"], *d.get("supports", [])]:
            need(f"domain {d['domain']!r}", rid, True)
    for q in ds.quotes:
        for rid in q["rules"]:
            need(f"quote {q['id']}", rid, True)
    for e in ds.meta["known_exceptions"]:
        need("meta.known_exceptions", e["rule"])
    return msgs


_DOMAIN_COUNT = re.compile(
    r"(\d+) domains in (\d+) branches "
    r"\((\d+) engineering branches, (\d+) management branches\)"
)


def check_domain_count(ctx: Context) -> list[str]:
    """The domain-index intro states counts that must match domains.yaml."""
    section: dict[str, Any] = next(
        (s for s in ctx.ds.meta["sections"] if s["key"] == "domain_index"), {}
    )
    match = _DOMAIN_COUNT.search(section.get("intro", ""))
    if not match:
        return ["domain_index intro has no 'N domains in B branches (...)' sentence"]
    domains = ctx.ds.domains["domains"]
    branches = {d["branch"] for d in domains}
    management = {b for b in branches if b.startswith("Management:")}
    actual = (
        len(domains),
        len(branches),
        len(branches) - len(management),
        len(management),
    )
    stated = tuple(int(g) for g in match.groups())
    if stated != actual:
        return [
            f"domain-index intro states {stated[0]} domains in {stated[1]} branches "
            f"({stated[2]} engineering, {stated[3]} management) but domains.yaml has "
            f"{actual[0]} domains in {actual[1]} branches ({actual[2]} engineering, "
            f"{actual[3]} management)"
        ]
    return []


def parse_id_list(text: str, prefixes: list[str]) -> list[str]:
    """``"P47–P58, K9, P14-P16"`` -> every ID, ranges expanded (en dash or hyphen).

    Raises ``ValueError`` for an item that is not an ID or a range within one
    prefix.
    """
    one = re.compile(rf"({prefix_alt(prefixes)})([1-9][0-9]*)")
    ids: list[str] = []
    for item in (i.strip() for i in text.split(",")):
        ends = [e.strip() for e in re.split(r"[–-]", item)]
        parsed = [one.fullmatch(e) for e in ends]
        if len(ends) > 2 or not all(parsed):
            raise ValueError(f"{item!r} is not a rule ID or ID range")
        matches = [m for m in parsed if m]
        lo, hi = matches[0], matches[-1]
        if lo.group(1) != hi.group(1) or int(lo.group(2)) > int(hi.group(2)):
            raise ValueError(f"{item!r} is not a range within one prefix")
        ids.extend(
            f"{lo.group(1)}{n}" for n in range(int(lo.group(2)), int(hi.group(2)) + 1)
        )
    return ids


def check_management_count(ctx: Context) -> list[str]:
    """The scope sentence on section 10 matches the rules without ``management``."""
    prefixes = list(ctx.ds.meta["id_prefixes"])
    item = rf"{id_pattern(prefixes)}(?:\s*[–-]\s*{id_pattern(prefixes)})?"
    sentence = re.compile(
        r"Section 10 states (\d+) of the (\d+) rules in management form.*?"
        rf"the other (\d+) \(({item}(?:,\s*{item})*)\)"
    )
    match = next(
        (m for _, s in _strings(ctx.ds.meta) if (m := sentence.search(s))), None
    )
    if not match:
        return [
            "meta has no 'Section 10 states N of the M rules in management form ... "
            "the other K (IDs)' sentence"
        ]
    stated_n, stated_m, stated_k = (int(match.group(i)) for i in (1, 2, 3))
    listed = parse_id_list(match.group(4), prefixes)
    rules = ctx.ds.rules
    without = [r["id"] for r in rules if not r["management"]]
    msgs: list[str] = []
    actual = (len(rules) - len(without), len(rules), len(without))
    if (stated_n, stated_m, stated_k) != actual:
        msgs.append(
            f"meta states section 10 has {stated_n} of {stated_m} rules and "
            f"{stated_k} others, but rules.yaml has {actual[0]} of {actual[1]} "
            f"with a management form and {actual[2]} without"
        )
    if sorted(listed) != sorted(without):
        msgs.append(
            "meta's list of rules without a management form has extra "
            f"{sorted(set(listed) - set(without), key=_id_key(ctx))} and misses "
            f"{sorted(set(without) - set(listed), key=_id_key(ctx))}"
        )
    return msgs


def check_rule_in_domain(ctx: Context) -> list[str]:
    covered = {rid for d in ctx.ds.domains["domains"] for rid in d["rules"]}
    return [
        f"{r['id']} appears in no domain (domains.yaml)"
        for r in ctx.ds.rules
        if r["id"] not in covered
    ]


def structured_slugs(ds: Dataset) -> list[tuple[str, str]]:
    """``(location, slug)`` for every slug named outside prose citations."""
    out = [
        ("data/meta.yaml: master_rule.sources", s)
        for s in ds.meta["master_rule"]["sources"]
    ]
    for r in ds.rules:
        out.extend((f"data/rules.yaml: {r['id']} sources", s) for s in r["sources"])
        if r["management"]:
            out.extend(
                (f"data/rules.yaml: {r['id']} management.sources", s)
                for s in r["management"]["sources"]
            )
    for d in ds.domains["domains"]:
        out.extend(
            (f"data/domains.yaml: domain {d['domain']!r} references", s)
            for s in d["references"]
        )
    for q in ds.quotes:
        if q["source"]:
            out.append((f"data/quotes.yaml: {q['id']} source", q["source"]))
        out.extend(
            (f"data/quotes.yaml: {q['id']} extra_sources", s)
            for s in q.get("extra_sources", [])
        )
    return out


def _in_registry(location: str) -> bool:
    """True for a ``cited_texts`` location inside a source registry file."""
    return any(location.startswith(f"{rel}:") for rel in REGISTRY_FILES)


def _used_slugs(ctx: Context) -> set[str]:
    """Slugs used by data or cited in prose; a registry citing itself is no use."""
    used = {slug for _, slug in structured_slugs(ctx.ds)}
    for where, text in cited_texts(ctx):
        if _in_registry(where):
            continue
        try:
            used.update(citation_slugs(text))
        except ValueError:
            pass  # reported by the citations check
    return used


def slug_locations(ctx: Context, slug: str) -> list[str]:
    """Every place that names ``slug``, structured or as a citation."""
    found = [where for where, s in structured_slugs(ctx.ds) if s == slug]
    for where, text in cited_texts(ctx):
        try:
            if slug in citation_slugs(text):
                found.append(where)
        except ValueError:
            continue
    return found


def check_slug_references(ctx: Context) -> list[str]:
    return [
        f"{where} names unknown source slug {slug!r}"
        for where, slug in structured_slugs(ctx.ds)
        if slug not in ctx.registry
    ]


def check_source_used(ctx: Context) -> list[str]:
    used = _used_slugs(ctx)
    msgs: list[str] = []
    for rel, entries in ctx.registries:
        for s in entries:
            if s["slug"] not in used:
                msgs.append(
                    f"source {s['slug']} ({rel}) is not used by data, paper/ or docs/"
                )
    return msgs


_PIPE = re.compile(r"(?<!\\)\|")


def check_table_columns(ctx: Context) -> list[str]:
    """Render the single file and compare every row's column count to its header."""
    msgs: list[str] = []
    try:
        for sec in build_sections(ctx.ds, ctx.registry, chapter=False):
            for block in sec.blocks:
                if block.kind != "table":
                    continue
                rows = block.text.split("\n")
                width = len(_PIPE.findall(rows[0])) - 1
                for row in rows[1:]:
                    if len(_PIPE.findall(row)) - 1 != width:
                        msgs.append(
                            f"section {sec.number}: a table row has a different column "
                            "count "
                            f"than its header ({width}): {row[:60]!r}"
                        )
    except (ValueError, KeyError) as exc:
        msgs.append(f"a table cannot be built: {exc!r}")
    return msgs


def relation_edges(ds: Dataset) -> dict[tuple[str, str], set[str]]:
    """``(a, b) -> relation names`` stated by a about b."""
    edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in ds.rules:
        for rel, targets in r["related"].items():
            for t in targets:
                edges[(r["id"], t)].add(rel)
    return edges


def check_relation_contradictions(ctx: Context) -> list[str]:
    """Contradictory relations (missing inverses are ``inverse-complete``'s job).

    - a rule relates to itself;
    - A conflicts_with B (either way) while A and B also have a supportive
      relation (depends_on, strengthens, strengthened_by, checks, checked_by,
      scaled_by) in either direction;
    - A depends_on B while B depends_on A.
    """
    edges = relation_edges(ctx.ds)
    msgs: list[str] = []
    for (a, b), rels in sorted(edges.items()):
        if a == b:
            msgs.append(f"{a} lists itself in related ({', '.join(sorted(rels))})")
    pairs = sorted({(min(a, b), max(a, b)) for a, b in edges if a != b})
    for lo, hi in pairs:
        forward = edges.get((lo, hi), set())
        backward = edges.get((hi, lo), set())
        both = forward | backward
        if "conflicts_with" in both and both & set(SUPPORTIVE):
            msgs.append(
                f"{lo} and {hi} conflict and also support each other "
                f"({lo}: {sorted(forward)}, {hi}: {sorted(backward)})"
            )
        if "depends_on" in forward and "depends_on" in backward:
            msgs.append(f"{lo} and {hi} depend on each other")
    return msgs


#: Relation -> its inverse; a relation listed here must be stated on both rules.
INVERSES = {
    "strengthens": "strengthened_by",
    "strengthened_by": "strengthens",
    "checks": "checked_by",
    "checked_by": "checks",
}


def _id_key(ctx: Context) -> Callable[[str], tuple[int, int]]:
    """Sort key for IDs: prefix in ``meta.id_prefixes`` order, then number."""
    prefixes = list(ctx.ds.meta["id_prefixes"])
    return lambda rule_id: id_key(rule_id, prefixes)


def check_inverse_complete(ctx: Context) -> list[str]:
    """A strengthens B needs B strengthened_by A, and so on (``INVERSES``)."""
    rules = ctx.ds.rule_by_id()
    msgs: list[str] = []
    for r in ctx.ds.rules:
        for rel, targets in r["related"].items():
            inverse = INVERSES.get(rel)
            if inverse is None:
                continue
            for t in targets:
                if t in rules and r["id"] not in rules[t]["related"].get(inverse, []):
                    msgs.append(
                        f"{r['id']} {rel} {t}, but {t} does not list "
                        f"{r['id']} under {inverse}"
                    )
    return msgs


def check_conflicts_symmetric(ctx: Context) -> list[str]:
    rules = ctx.ds.rule_by_id()
    return [
        f"{r['id']} conflicts_with {t}, but {t} does not list {r['id']} "
        "under conflicts_with"
        for r in ctx.ds.rules
        for t in r["related"].get("conflicts_with", [])
        if t in rules and r["id"] not in rules[t]["related"].get("conflicts_with", [])
    ]


def check_related_order(ctx: Context) -> list[str]:
    """Keys in ``meta.relation_types`` order; IDs by prefix, then number."""
    order = list(ctx.ds.meta["relation_types"])
    msgs: list[str] = []
    for r in ctx.ds.rules:
        keys = [k for k in r["related"] if k in order]
        if keys != sorted(keys, key=order.index):
            msgs.append(
                f"{r['id']} related keys {keys} are not in relation_types order "
                f"{sorted(keys, key=order.index)}"
            )
        for rel, targets in r["related"].items():
            want = sorted(targets, key=_id_key(ctx))
            if list(targets) != want:
                msgs.append(
                    f"{r['id']} {rel} {list(targets)} is not in ID order {want}"
                )
    return msgs


def check_override_agreement(ctx: Context) -> list[str]:
    """A ``related_text`` override names exactly the IDs of ``related``.

    Non-rule text ("accountability", "(see K7)", qualifiers) is ignored; each
    rule ID counts as often as it occurs.
    """
    # Only rule IDs count: "(see K7)" names a conflict rule, not a relation.
    finder = id_finder({re.sub(r"\d+$", "", r["id"]) for r in ctx.ds.rules})
    key = _id_key(ctx)
    msgs: list[str] = []
    for r in ctx.ds.rules:
        if "related_text" not in r:
            continue
        named = sorted(
            (m.group(0) for m in finder.finditer(r["related_text"])), key=key
        )
        structured = sorted(
            (t for targets in r["related"].values() for t in targets), key=key
        )
        if named != structured:
            msgs.append(
                f"{r['id']} related_text names {named} but related has {structured}"
            )
    return msgs


def check_sources_primary_first(ctx: Context) -> list[str]:
    """Rule and management-form ``sources`` list primary before secondary."""
    msgs: list[str] = []
    for r in ctx.ds.rules:
        lists = [("sources", r["sources"])]
        if r["management"]:
            lists.append(("management.sources", r["management"]["sources"]))
        for where, slugs in lists:
            kinds = [ctx.registry[s]["kind"] for s in slugs if s in ctx.registry]
            if "secondary" in kinds and "primary" in kinds[kinds.index("secondary") :]:
                msgs.append(
                    f"{r['id']} {where} lists a secondary source before a primary one"
                )
    return msgs


def check_primary_source(ctx: Context) -> list[str]:
    exceptions = {
        e["rule"]
        for e in ctx.ds.meta["known_exceptions"]
        if e["check"] == "primary-source"
    }
    msgs: list[str] = []
    for r in ctx.ds.rules:
        if r["id"] in exceptions:
            continue
        kinds = [ctx.registry[s]["kind"] for s in r["sources"] if s in ctx.registry]
        if "primary" not in kinds:
            msgs.append(
                f"{r['id']} has no primary source and is not in meta.known_exceptions"
            )
    return msgs


def check_counterexamples(ctx: Context) -> list[str]:
    return [
        f"{r['id']} is a conditional (C) rule without a counterexample"
        for r in ctx.ds.rules
        if r["class"] == "conditional" and not r.get("counterexample", "").strip()
    ]


def check_conflict_rules(ctx: Context) -> list[str]:
    ids = ctx.ds.all_ids()
    msgs: list[str] = []
    for k in ctx.ds.conflicts:
        named = k["rules"]
        if len(set(named)) < 2:
            msgs.append(f"{k['id']} names fewer than 2 rules ({named})")
        msgs.extend(f"{k['id']} names unknown rule {t}" for t in named if t not in ids)
    return msgs


def check_category_membership(ctx: Context) -> list[str]:
    msgs: list[str] = []
    rules = ctx.ds.rule_by_id()
    listed: dict[str, str] = {}
    for c in ctx.ds.categories:
        for rid in c["rules"]:
            if rid in listed:
                msgs.append(
                    f"{rid} is listed in categories {listed[rid]} and {c['id']}"
                )
            listed[rid] = c["id"]
            if rid in rules and rules[rid]["category"] != c["id"]:
                msgs.append(
                    f"{rid} is listed in category {c['id']} but has category "
                    f"{rules[rid]['category']}"
                )
    for rid, r in rules.items():
        if rid not in listed:
            msgs.append(f"{rid} (category {r['category']}) is listed in no category")
    return msgs


def check_quick_view(ctx: Context) -> list[str]:
    q = ctx.ds.meta["quick_view_questions"]
    msgs: list[str] = []
    if not 5 <= len(q) <= 9:
        msgs.append(f"quick view has {len(q)} questions; it needs 5 to 9")
    cats = {c["id"] for c in ctx.ds.categories}
    msgs.extend(f"quick-view question {k} has no category" for k in q if k not in cats)
    msgs.extend(
        f"category {k} has no quick-view question" for k in sorted(cats - set(q))
    )
    return msgs


def check_id_map(ctx: Context) -> list[str]:
    ids = ctx.ds.all_ids()
    return [
        f"history.id_map: {e['old']} -> {e['new']} points at an unknown rule"
        for e in ctx.ds.history["id_map"]
        if e["new"] not in ids
    ]


def check_citations(ctx: Context) -> list[str]:
    msgs: list[str] = []
    for where, text in cited_texts(ctx):
        try:
            slugs = citation_slugs(text)
        except ValueError as exc:
            msgs.append(f"{where}: {exc}")
            continue
        msgs.extend(
            f"{where}: [@{s}] does not resolve" for s in slugs if s not in ctx.registry
        )
    return msgs


def check_registry_unique(ctx: Context) -> list[str]:
    msgs: list[str] = []
    slugs: dict[str, str] = {}
    urls: dict[str, str] = {}
    for rel, entries in ctx.registries:
        for s in entries:
            if s["slug"] in slugs:
                msgs.append(f"slug {s['slug']} is in {rel} and {slugs[s['slug']]}")
            slugs.setdefault(s["slug"], rel)
            if s["url"] in urls:
                msgs.append(
                    f"URL {s['url']} ({s['slug']}) is in {rel} and {urls[s['url']]}"
                )
            urls.setdefault(s["url"], rel)
    return msgs


CHECKS: dict[str, Callable[[Context], list[str]]] = {
    "schema": check_schema,
    "unique-ids": check_unique_ids,
    "related-targets": check_related_targets,
    "id-references": check_id_references,
    "rule-in-domain": check_rule_in_domain,
    "domain-count": check_domain_count,
    "management-count": check_management_count,
    "slug-references": check_slug_references,
    "source-used": check_source_used,
    "table-columns": check_table_columns,
    "relation-contradictions": check_relation_contradictions,
    "inverse-complete": check_inverse_complete,
    "conflicts-symmetric": check_conflicts_symmetric,
    "related-order": check_related_order,
    "override-agreement": check_override_agreement,
    "sources-primary-first": check_sources_primary_first,
    "primary-source": check_primary_source,
    "counterexamples": check_counterexamples,
    "conflict-rules": check_conflict_rules,
    "category-membership": check_category_membership,
    "quick-view": check_quick_view,
    "id-map": check_id_map,
    "citations": check_citations,
    "registry-unique": check_registry_unique,
}


def make_context(root: Path) -> Context:
    ds = load_dataset(root)
    registries = load_registry_files(root)
    registry: dict[str, Source] = {}
    for _, entries in registries:
        for s in entries:
            registry.setdefault(s["slug"], s)
    return Context(root, ds, registries, registry)


def run_checks(root: Path) -> list[Finding]:
    """Run every check; nothing is raised.

    A file that cannot be read or parsed becomes one ``load`` finding; a check
    that crashes on malformed data becomes a finding of its own.
    """
    try:
        ctx = make_context(root)
    except Exception as exc:
        # The other checks need the whole dataset; the schema check still runs
        # file by file, so every other file is validated too.
        load = Finding("load", f"cannot load the dataset: {type(exc).__name__}: {exc}")
        try:
            schema = [Finding("schema", m) for m in schema_findings(root)]
        except Exception as inner:
            schema = [
                Finding(
                    "schema", f"check could not run: {type(inner).__name__}: {inner}"
                )
            ]
        return [load, *schema]
    findings: list[Finding] = []
    for name, fn in CHECKS.items():
        try:
            findings.extend(Finding(name, m) for m in fn(ctx))
        except Exception as exc:
            findings.append(
                Finding(
                    name,
                    f"check could not run on this data: {type(exc).__name__}: {exc}",
                )
            )
    return findings
