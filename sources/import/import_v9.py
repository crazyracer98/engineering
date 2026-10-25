"""One-shot importer: edition-9 Markdown + edition-6 YAML -> ``data/``.

What it does
------------
Reads the two provenance files in ``sources/import/``:

* ``engineering-best-practices.md`` -- edition 9, authoritative for content
  and wording;
* ``engineering-best-practices.yaml`` -- edition 6, the schema seed (field
  names, glossary and rigor-matrix shape, rule field set).

and writes the structured dataset under ``data/`` (one YAML file per
``schema/<name>.schema.json``). Every inline ``[title](url)`` link of
edition 9 becomes a Pandoc citation ``[@slug]`` (or a slug in a ``sources`` /
``references`` list); the link title is kept in ``data/sources.yaml``, and a
title that differs from the canonical one is kept as a per-use override
(``source_titles`` / ``reference_titles``) so that the edition-9 Markdown can
be reproduced byte for byte from ``data/``. Where a table cell cannot be
regenerated from its structured fields, the verbatim cell is kept in a
``*_text`` override field (see the schema descriptions).

Primary/secondary classification, publisher names and faithful-copy (``via``)
records come from the tables in this file (``HOSTS`` and ``URL_OVERRIDES``),
which encode section 1 ("Source quality"), section 12 and the Evidence
columns of edition 9; every judgment is labelled in the source's ``notes``.

From the first import on, ``data/`` is the single source of truth (ADR 0003).
This script is kept only for reproducibility: running it again regenerates
exactly the same files and overwrites any later hand edits in ``data/``.
All post-import fixes live in this script, so a rerun reproduces them.

How to run
----------
From the repository root::

    uv run python sources/import/import_v9.py            # write data/
    uv run python sources/import/import_v9.py --report   # also print the
                                                         # edition-6 vs 9 diff

The output is deterministic: rerunning it leaves ``git status`` clean.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.representer import RoundTripRepresenter
from ruamel.yaml.scalarstring import LiteralScalarString

ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = ROOT / "sources" / "import"
MD_PATH = IMPORT_DIR / "engineering-best-practices.md"
ED6_PATH = IMPORT_DIR / "engineering-best-practices.yaml"
DATA_DIR = ROOT / "data"

EDITION = "1.0.0"

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s()]*(?:\([^\s()]*\)[^\s()]*)*)\)")
ID_RE = re.compile(r"\b[URCK]\d+\b")
LEVELS = ("strong", "moderate", "weak")
RELATIONS = {
    "depends on": "depends_on",
    "strengthens": "strengthens",
    "strengthened by": "strengthened_by",
    "conflicts with": "conflicts_with",
    "checks": "checks",
    "checked by": "checked_by",
    "scaled by": "scaled_by",
}
MASTER = "Master"  # pseudo rule ID for the master rule (as in edition 6)

# Sections whose link titles are preferred as the canonical source title
# (lower rank wins): 9 Sources by rule, 4 Domain index, 12 Method sources,
# 11 Direct quotes, 10 Management forms.
TITLE_RANK = {9: 0, 4: 1, 12: 2, 11: 3, 10: 4}

_FIXED = [
    (
        "incose-se-principles",
        "https://www.incose.org/wp-content/uploads/legacy/professional-development-portal/pdp-pdf-non-webinar-documents/systems_engineering_principles_book_v12_watson.pdf",
    ),
    (
        "sebok-se-principles",
        "https://sebokwiki.org/wiki/Systems_Engineering_Principles",
    ),
    (
        "mann-checklist-manifesto-notes",
        "https://grahammann.net/book-notes/the-checklist-manifesto-atul-gawande",
    ),
    ("wikipedia-academic-use", "https://en.wikipedia.org/wiki/Wikipedia:Academic_use"),
]
FIXED_SLUGS = {url: slug for slug, url in _FIXED}
_SLUG_OVERRIDES = [
    ("hgb-239", "https://dejure.org/gesetze/HGB/239.html"),
    ("iso-9001-2026-launch", "https://www.iso.org/news/2026/09/ISO9001-2026"),
    (
        "toyota-production-system",
        "https://global.toyota/en/company/vision-and-philosophy/production-system/",
    ),
    (
        "nist-sp-800-53-ac-3-2",
        "https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-3/ac-3-2/",
    ),
    ("deming-14-points", "https://deming.org/explore/fourteen-points/"),
]
SLUG_OVERRIDES = {url: slug for slug, url in _SLUG_OVERRIDES}
STOPWORDS = {
    "a",
    "an",
    "the",
    "of",
    "in",
    "on",
    "for",
    "and",
    "to",
    "with",
    "by",
    "is",
    "it",
}

# --------------------------------------------------------------------------
# Source classification tables (the importer's encoding of edition 9's
# section 1 "Source quality", section 12 and the Evidence columns).
# Rows are (kind, publisher, paid, note, host); the URL or host comes last.
# --------------------------------------------------------------------------
P, S = "primary", "secondary"
J = "Classification is the importer's judgment against section 1's definition"

_HOSTS: list[tuple[str, str | None, bool, str | None, str]] = [
    (
        S,
        "Wikipedia",
        False,
        "Encyclopedia (section 1: kept only as a secondary link).",
        "en.wikipedia.org",
    ),
    (
        S,
        "Grokipedia",
        False,
        "Encyclopedia.",
        "grokipedia.com",
    ),
    (
        S,
        "Elsevier (ScienceDirect Topics)",
        False,
        "Topic aggregator page.",
        "www.sciencedirect.com",
    ),
    (
        S,
        "PatSnap",
        False,
        "Vendor page.",
        "eureka.patsnap.com",
    ),
    (
        S,
        "Stell Engineering",
        False,
        "Vendor blog.",
        "stell-engineering.com",
    ),
    (
        S,
        "Swift Navigation",
        False,
        "Vendor glossary page.",
        "www.swiftnav.com",
    ),
    (
        S,
        "Wermac",
        False,
        J + ": reference website, not a standard or original report.",
        "www.wermac.org",
    ),
    (
        S,
        "TV Technology",
        False,
        "Trade publication.",
        "www.tvtechnology.com",
    ),
    (
        S,
        "Chiuvention",
        False,
        "Vendor blog.",
        "chiuvention.com",
    ),
    (
        S,
        "Molecular Devices",
        False,
        "Vendor page.",
        "www.moleculardevices.com",
    ),
    (
        S,
        "Mining Weekly",
        False,
        "News article.",
        "www.miningweekly.com",
    ),
    (
        S,
        "MD+DI",
        False,
        "Trade publication.",
        "www.mddionline.com",
    ),
    (
        S,
        "eg technology",
        False,
        "Vendor page.",
        "www.egtechnology.co.uk",
    ),
    (
        S,
        "ScienceDaily",
        False,
        "News article about the study.",
        "www.sciencedaily.com",
    ),
    (
        S,
        "User Solutions",
        False,
        "Vendor blog.",
        "usersolutions.com",
    ),
    (
        S,
        "ISO Central",
        False,
        "Third-party page, not published by ISO.",
        "isocentral.org",
    ),
    (
        S,
        "Fire Risk Assessment Network",
        False,
        "Blog.",
        "fire-risk-assessment-network.com",
    ),
    (
        S,
        "Jamf",
        False,
        "Vendor blog.",
        "www.jamf.com",
    ),
    (
        S,
        "Palo Alto Networks",
        False,
        "Vendor page.",
        "www.paloaltonetworks.com",
    ),
    (
        S,
        "EBSCO",
        False,
        "Research Starters: topic aggregator.",
        "www.ebsco.com",
    ),
    (
        S,
        "Flight Test Fact",
        False,
        "Blog.",
        "flighttestfact.com",
    ),
    (
        S,
        "Quality Engineers Guide",
        False,
        "Blog.",
        "www.qualityengineersguide.com",
    ),
    (
        S,
        "EPCLand",
        False,
        "Blog.",
        "epcland.com",
    ),
    (
        S,
        "LibreTexts",
        False,
        J + ": open textbook compilation.",
        "eng.libretexts.org",
    ),
    (
        S,
        "The Next Web",
        False,
        "News article.",
        "thenextweb.com",
    ),
    (
        S,
        "Purple Griffon",
        False,
        (
            "Training-vendor blog; edition 9 section 11: secondary, the official "
            "PRINCE2 manual is paid."
        ),
        "purplegriffon.com",
    ),
    (
        S,
        "Presencis",
        False,
        "Edition 9 section 11: secondary; the ISO 45001 text is paid.",
        "cdn.presencis.com",
    ),
    (
        S,
        "Troutman Pepper",
        False,
        (
            "Law-firm article; edition 9 section 11: secondary, describes the primary "
            "Sedona commentary."
        ),
        "www.troutman.com",
    ),
    (
        S,
        "The Jargon File",
        False,
        "Edition 9 section 12: C15 rests on the Jargon File (secondary only).",
        "www.catb.org",
    ),
    (
        S,
        "Electronic Design",
        False,
        (
            "Trade article; edition 9 section 12 (C15 rests on the Jargon File and a "
            "trade article)."
        ),
        "www.electronicdesign.com",
    ),
    (
        S,
        "cat-v.org",
        False,
        (
            "Copy of Parkinson's essay that could not be compared with The Economist's "
            "archive; edition 9 section 12 treats it as secondary."
        ),
        "doc.cat-v.org",
    ),
    (
        S,
        "SINTEF",
        False,
        J + ": blog post of a research institute.",
        "blog.sintef.com",
    ),
    (
        S,
        "Primatech",
        False,
        J + ": consultancy page.",
        "www.primatech.com",
    ),
    (
        S,
        "Graham Mann",
        False,
        "Personal book notes (blog); edition 9 cites Gawande via these notes.",
        "grahammann.net",
    ),
    (
        S,
        "adr.github.io",
        False,
        J + ": community topic page that aggregates ADR resources.",
        "adr.github.io",
    ),
    (
        P,
        "ISO",
        True,
        (
            "ISO catalogue page; the standard text is paid (edition 9 section 12), the "
            "page gives title and summary only."
        ),
        "www.iso.org",
    ),
    (
        P,
        "ISO",
        False,
        "ISO committee news item.",
        "committee.iso.org",
    ),
    (
        P,
        "arXiv",
        False,
        "Original paper (preprint).",
        "arxiv.org",
    ),
    (
        P,
        "US OSHA",
        False,
        "Regulator.",
        "www.osha.gov",
    ),
    (
        P,
        "US FDA",
        False,
        "Regulator.",
        "www.fda.gov",
    ),
    (
        P,
        "Google",
        False,
        J + ": Google's own SRE book, original publication.",
        "sre.google",
    ),
    (
        P,
        "PMI",
        True,
        "Official PMI page; the PMBOK Guide text is paid (edition 9 section 12).",
        "www.pmi.org",
    ),
    (
        P,
        "NSPE",
        False,
        "Professional body.",
        "www.nspe.org",
    ),
    (
        P,
        "NASA",
        False,
        "NASA technical report.",
        "ntrs.nasa.gov",
    ),
    (
        P,
        "SPE (Journal of Petroleum Technology)",
        False,
        J
        + (
            ": magazine of a professional body (SPE); edition 9 rates U29 and U14 as "
            "having primary sources."
        ),
        "jpt.spe.org",
    ),
    (
        P,
        "NIST",
        False,
        "Standards body glossary.",
        "csrc.nist.gov",
    ),
    (
        P,
        "NIST",
        False,
        "Original report.",
        "nvlpubs.nist.gov",
    ),
    (
        P,
        "US SEC (EDGAR)",
        False,
        "Original filing.",
        "www.sec.gov",
    ),
    (
        P,
        "RFC Editor",
        False,
        "Standard (RFC).",
        "www.rfc-editor.org",
    ),
    (
        P,
        "US PHMSA",
        False,
        "Regulator.",
        "www.phmsa.dot.gov",
    ),
    (
        P,
        "US DOE OSTI",
        False,
        "Original report.",
        "www.osti.gov",
    ),
    (
        P,
        "OECD",
        False,
        (
            "Intergovernmental body; edition 9 section 12: only the abstract could be "
            "retrieved."
        ),
        "www.oecd.org",
    ),
    (
        P,
        "OECD",
        False,
        "Intergovernmental body.",
        "search.oecd.org",
    ),
    (
        P,
        "OECD",
        False,
        "Intergovernmental body.",
        "legalinstruments.oecd.org",
    ),
    (
        P,
        "Nobel Prize Outreach",
        False,
        "Official press release.",
        "www.nobelprize.org",
    ),
    (
        P,
        "NERC",
        False,
        "Standard.",
        "www.nerc.com",
    ),
    (
        P,
        "NCBI PubMed Central",
        False,
        "Original paper.",
        "www.ncbi.nlm.nih.gov",
    ),
    (
        P,
        "NCBI PubMed Central",
        False,
        "Original paper.",
        "pmc.ncbi.nlm.nih.gov",
    ),
    (
        P,
        "National Academies",
        False,
        "Original report.",
        "www.nationalacademies.org",
    ),
    (
        P,
        "NASA",
        False,
        "Agency document.",
        "www.nasa.gov",
    ),
    (
        P,
        "NASA",
        False,
        "Standard.",
        "standards.nasa.gov",
    ),
    (
        P,
        "NASA",
        False,
        "Agency handbook.",
        "swehb.nasa.gov",
    ),
    (
        P,
        "NASA",
        False,
        "Original report.",
        "discovery.larc.nasa.gov",
    ),
    (
        P,
        "Melvin Conway",
        False,
        "Author's own copy of the original paper.",
        "www.melconway.com",
    ),
    (
        P,
        "INCOSE",
        False,
        "Professional body.",
        "www.incose.org",
    ),
    (
        P,
        "IAEA",
        False,
        "Intergovernmental body (IAEA Bulletin).",
        "www.iaea.org",
    ),
    (
        P,
        "US FAA",
        False,
        "Regulator.",
        "www.faa.gov",
    ),
    (
        P,
        "US eCFR",
        False,
        "Regulation.",
        "www.ecfr.gov",
    ),
    (
        P,
        "COSO",
        False,
        "Official executive summary of the framework.",
        "www.coso.org",
    ),
    (
        P,
        "Center for Internet Security",
        False,
        "Standard (CIS Controls).",
        "www.cisecurity.org",
    ),
    (
        P,
        "CDC/NIOSH",
        False,
        "Agency.",
        "www.cdc.gov",
    ),
    (
        P,
        "ASME",
        True,
        (
            "Official code page; Classification is the importer's judgment against "
            "section 1's definition: the code text is sold by ASME. Edition 9 section "
            "12: the page confirms procedure qualification only."
        ),
        "www.asme.org",
    ),
    (
        P,
        "American Economic Association",
        False,
        "Original paper (journal page).",
        "www.aeaweb.org",
    ),
    (
        P,
        "US FEMA",
        False,
        "Federal doctrine.",
        "training.fema.gov:443",
    ),
    (
        P,
        "ASTM International",
        True,
        (
            "Standard store page; Classification is the importer's judgment against "
            "section 1's definition: the standard text is sold by ASTM."
        ),
        "store.astm.org",
    ),
    (
        P,
        "IEEE",
        True,
        (
            "Standard page; Classification is the importer's judgment against section "
            "1's definition: the standard text is sold by IEEE."
        ),
        "standards.ieee.org",
    ),
    (
        P,
        "Singapore Attorney-General's Chambers",
        False,
        "Regulation.",
        "sso.agc.gov.sg",
    ),
    (
        P,
        "OpenSSF (SLSA)",
        False,
        "Specification.",
        "slsa.dev",
    ),
    (
        P,
        "MIT Sloan Management Review",
        False,
        "Original article by the authors.",
        "sloanreview.mit.edu",
    ),
    (
        P,
        "SEBoK (INCOSE, IEEE CS, SERC)",
        False,
        J + ": body of knowledge curated by professional bodies.",
        "sebokwiki.org",
    ),
    (
        P,
        "Scrum Guides (Schwaber and Sutherland)",
        False,
        "The Scrum Guide itself.",
        "scrumguides.org",
    ),
    (
        P,
        "Google",
        False,
        J + ": Google's report on its own study.",
        "rework.withgoogle.com",
    ),
    (
        P,
        "NeurIPS",
        False,
        "Original paper.",
        "proceedings.neurips.cc",
    ),
    (
        P,
        "SPE (OnePetro)",
        False,
        "Professional body.",
        "onepetro.org",
    ),
    (
        P,
        "Institution of Civil Engineers",
        False,
        "Professional body.",
        "knowledgehub.ice.org.uk",
    ),
    (
        P,
        "PLOS",
        False,
        "Original paper.",
        "journals.plos.org",
    ),
    (
        P,
        "USPTO",
        False,
        "Patent.",
        "image-ppubs.uspto.gov",
    ),
    (
        P,
        "US FHWA",
        False,
        "Agency.",
        "highways.dot.gov",
    ),
    (
        P,
        "EUR-Lex (European Union)",
        False,
        "Law; edition 9 section 12: Article 19 could not be retrieved.",
        "eur-lex.europa.eu",
    ),
    (
        P,
        "ENEFIRST project",
        False,
        J + ": definitions page of the research project itself.",
        "enefirst.eu",
    ),
    (
        P,
        "DORA (Google Cloud)",
        False,
        J + ": the research programme's own capability page.",
        "dora.dev",
    ),
    (
        P,
        "IZA Institute of Labor Economics",
        False,
        "Original discussion paper.",
        "docs.iza.org",
    ),
    (
        P,
        "UK Ministry of Defence",
        False,
        "Official handbook.",
        "assets.publishing.service.gov.uk",
    ),
    (
        P,
        "ASQ",
        False,
        "Professional body.",
        "asq.org",
    ),
    (
        P,
        "DTIC",
        False,
        "Original report.",
        "apps.dtic.mil",
    ),
    (
        P,
        "Agile Manifesto authors",
        False,
        "The original principles.",
        "agilemanifesto.org",
    ),
    (
        P,
        "The Aerospace Corporation",
        False,
        "Original report.",
        "aerospace.org",
    ),
    (
        P,
        "Business Continuity Institute",
        False,
        "Professional body.",
        "www.thebci.org",
    ),
    (
        P,
        "Institute of Internal Auditors",
        False,
        "Professional body.",
        "www.theiia.org",
    ),
    (
        P,
        "Florida Department of Transportation",
        False,
        "Agency training transcript.",
        "wbt.dot.state.fl.us",
    ),
    (
        P,
        "ICES",
        False,
        J + ": news release of the institute that ran the study.",
        "www.ices.on.ca",
    ),
    (
        P,
        "WHO",
        False,
        J + ": news release of the body that ran the study.",
        "www.who.int",
    ),
    (
        P,
        "Toyota",
        False,
        J + ": the originator's own description of its production system.",
        "global.toyota",
    ),
    (
        P,
        "The W. Edwards Deming Institute",
        False,
        J + ": the 14 points as published by Deming's institute.",
        "deming.org",
    ),
    (
        P,
        "Theory of Constraints Institute",
        False,
        J
        + (
            ": edition 9 section 12 states every rule except C15 has a primary "
            "source; for C8 only this page can be it."
        ),
        "www.tocinstitute.org",
    ),
    (
        P,
        "Harvard Business Review",
        False,
        "Original article; edition 9 section 12: only available as a summary.",
        "hbr.org",
    ),
    (
        P,
        "Hebrew University of Jerusalem",
        False,
        "Abstract page of the original paper.",
        "cris.huji.ac.il",
    ),
    (
        P,
        None,
        False,
        "DOI of the original paper; publisher not stated in edition 9.",
        "doi.org",
    ),
    (
        P,
        "University of Portland",
        False,
        J
        + (
            ": university course document; it is C1's only source and edition 9 says "
            "every rule except C15 has a primary source."
        ),
        "faculty.up.edu",
    ),
    (
        P,
        "Penn State University",
        False,
        J + ": university course document (treated like the Portland handout).",
        "www.me.psu.edu",
    ),
    (
        P,
        "UC San Diego",
        False,
        J + ": university lecture notes (treated like the Portland handout).",
        "cseweb.ucsd.edu",
    ),
    (
        P,
        "Columbia Business School",
        False,
        "Author's original paper.",
        "business.columbia.edu",
    ),
    (
        P,
        "MIT",
        False,
        "Original paper.",
        "web.mit.edu",
    ),
    (
        P,
        "GlobalSecurity.org",
        False,
        J + ": copy of the CAIB report text.",
        "www.globalsecurity.org",
    ),
]
HOSTS = {h[4]: h[:4] for h in _HOSTS}

# Rows are (partial overrides: kind, publisher, paid, note, via = copy host
# name; URL).
_URL_OVERRIDES: list[tuple[dict[str, Any], str]] = [
    (
        {
            "paid": False,
            "note": "ISO news release on the ISO 9001:2026 launch.",
        },
        "https://www.iso.org/news/2026/09/ISO9001-2026",
    ),
    (
        {
            "kind": P,
            "publisher": "NIST",
            "via": "CSF Tools",
            "note": "Faithful copy (edition 9 section 12: NIST via CSF Tools).",
        },
        "https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-3/ac-3-2/",
    ),
    (
        {
            "kind": P,
            "publisher": "IMO",
            "via": "imorules.com",
            "note": "Faithful copy (edition 9 section 12: IMO SOLAS via imorules.com).",
        },
        "https://www.imorules.com/solas/02_chapter_II-1.html",
    ),
    (
        {
            "kind": P,
            "publisher": "The Joint Commission",
            "via": "KFF",
            "note": (
                "Faithful copy (edition 9 section 12: The Joint Commission via KFF)."
            ),
        },
        "https://www.kff.org/wp-content/uploads/sites/2/2013/04/sea_50_alarms_4_5_13_final1.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "United Nations",
            "via": "World Bank ICSID archive",
            "note": (
                "Faithful copy (edition 9 section 12: the Rio Declaration via the World"
                " Bank ICSID archive)."
            ),
        },
        "https://icsid.worldbank.org/sites/default/files/parties_publications/C8394/Respondent%27s%20documents/RL%20-%20Legal%20Authorities/RL-0150-ENG%201992-06-13.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Communications of the ACM",
            "via": "worrydream.com",
            "note": (
                "Faithful copy (edition 9 section 12: Hoare's lecture via "
                "worrydream.com)."
            ),
        },
        "https://worrydream.com/refs/Hoare_1981_-_The_Emperors_Old_Clothes.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Administrative Science Quarterly",
            "via": "MIT",
            "note": "Faithful copy (edition 9 section 12: Edmondson via MIT).",
        },
        "https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Group_Performance/Edmondson%20Psychological%20safety.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Organizational Behavior and Human Performance",
            "via": "gwern.net",
            "note": "Faithful copy (edition 9 section 12: Staw via gwern.net).",
        },
        "https://Www.Gwern.net/doc/psychology/cognitive-bias/sunk-cost/1976-staw.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Journal of Applied Psychology",
            "via": "gwern.net",
            "note": "Faithful copy (edition 9 section 12: Sackett via gwern.net).",
        },
        "https://www.Gwern.net/doc/statistics/meta-analysis/2021-sackett.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Journal of MultiDisciplinary Evaluation",
            "via": "Journal of MultiDisciplinary Evaluation (2011 reprint)",
            "note": (
                "Faithful copy (edition 9 section 12: Campbell via a 2011 journal "
                "reprint; the quote itself was checked on Wikipedia)."
            ),
        },
        "https://jmde.journals.publicknowledgeproject.org/index.php/jmde_1/article/view/297",
    ),
    (
        {
            "kind": P,
            "publisher": "German Commercial Code (HGB)",
            "via": "dejure.org",
            "note": "Faithful copy (edition 9 section 12: § 239 HGB via dejure.org).",
        },
        "https://dejure.org/gesetze/HGB/239.html",
    ),
    (
        {
            "kind": P,
            "publisher": "European Union",
            "via": "charteredaccountants.ie",
            "note": (
                "Faithful copy (edition 9 section 12: Regulation (EU) No 537/2014 via "
                "charteredaccountants.ie)."
            ),
        },
        "https://www.charteredaccountants.ie/chariotindex/text/ec_2014_537/17.html",
    ),
    (
        {
            "kind": P,
            "publisher": "European Union",
            "via": "gdpr-info.eu",
            "note": (
                "Text copy of the GDPR; Classification is the importer's judgment "
                "against section 1's definition: faithful copy."
            ),
        },
        "https://gdpr-info.eu/art-5-gdpr/",
    ),
    (
        {
            "kind": P,
            "publisher": "US Army",
            "via": "Federation of American Scientists (irp.fas.org)",
            "note": J + ": faithful copy of the doctrine publication.",
        },
        "https://irp.fas.org/doddir/army/adp6_0.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "American Psychologist",
            "via": "University of Minnesota",
            "note": (
                "Copy (edition 9 title); Classification is the importer's judgment "
                "against section 1's definition: faithful copy."
            ),
        },
        "https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Harvard Business Review",
            "via": "ieanea.org",
            "note": (
                "Copy (edition 9 title); Classification is the importer's judgment "
                "against section 1's definition: faithful copy."
            ),
        },
        "https://ieanea.org/wp-content/uploads/2019/05/FairProcessArticle.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Harvard Business Review",
            "via": "UCSF",
            "note": (
                "Copy (edition 9 title); Classification is the importer's judgment "
                "against section 1's definition: faithful copy."
            ),
        },
        "https://fcm.ucsf.edu/sites/g/files/tkssra17611/files/Kotter_WhyTransformationEffortsFail.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Harvard Business Review",
            "via": "NYU Stern",
            "note": J + ": faithful copy of the HBR article.",
        },
        "https://web-docs.stern.nyu.edu/executive/The%20Surprising%20Power%20of%20Online%20Experiments.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": None,
            "via": "gapimprove.org",
            "note": J + ": faithful copy of the original paper.",
        },
        "https://www.gapimprove.org/_files/ugd/cd8b34_2d04bd540ca04019986c3ba54ae8631e.pdf?index=true",
    ),
    (
        {
            "kind": P,
            "publisher": "Management Science",
            "via": "Bilkent University",
            "note": J + ": faithful copy of the original paper.",
        },
        "https://courses.ie.bilkent.edu.tr/ie102/wp-content/uploads/sites/12/2019/02/Lee-Padmanabhan-Whang-1997-MS.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "Operations Research",
            "via": "Project Production Institute (reprint)",
            "note": (
                "Reprint (edition 9 title); Classification is the importer's judgment "
                "against section 1's definition: faithful copy."
            ),
        },
        "https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/",
    ),
    (
        {
            "kind": P,
            "publisher": "ACM CHI",
            "via": "interruptions.net",
            "note": J + ": faithful copy of the original paper.",
        },
        "https://www.interruptions.net/literature/Mark-CHI08.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": None,
            "via": "OMDEC",
            "note": J + ": faithful copy of the original report.",
        },
        "https://www.omdec.com/wikifiles/nowlanHeap.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "US Department of Defense",
            "via": "corrdesa.com",
            "note": J + ": faithful copy of the standard.",
        },
        "https://corrdesa.com/wp-content/uploads/2024/04/MIL-STD-889D-2021-Release.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": None,
            "via": "flighttestsafety.org",
            "note": J + ": faithful copy of the handbook.",
        },
        "https://www.flighttestsafety.org/images/STPA_Handbook.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": None,
            "via": "MIT course site",
            "note": J + ": faithful copy of the book.",
        },
        "https://introcontrol.mit.edu/_static/fall21/extras/Feedback%20Systems%20Murray.pdf",
    ),
    (
        {
            "note": J + ": original review article, hosted on an MIT course page.",
        },
        "https://web.mit.edu/2.70/Reading%20Materials/Kinematic%20coupling%20review%20article.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "ISO",
            "paid": True,
            "via": "iTeh Standards (sample)",
            "note": "Sample pages of the standard; the full text is paid.",
        },
        "https://cdn.standards.iteh.ai/samples/59970/06ad76004ab746ff90b82cf44a8b0752/ISO-13850-2015.pdf",
    ),
    (
        {
            "kind": P,
            "publisher": "ISO",
            "paid": True,
            "via": "iTeh Standards (sample)",
            "note": "Sample pages of the standard; the full text is paid.",
        },
        "https://cdn.standards.iteh.ai/samples/35179/19d75d1dcdd147d4b630728954acc86d/ISO-139-2005.pdf",
    ),
    (
        {
            "note": "Author's own copy of the original paper.",
        },
        "https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf",
    ),
]
URL_OVERRIDES = {url: ov for ov, url in _URL_OVERRIDES}

# Reasons for "Checked without a separate row" (importer's classification of
# the verbatim note; judgment).
_CHECKED_REASONS = [
    ("no-source", "Regenerative medicine"),
    ("blocked", "Composite materials"),
    ("covered-elsewhere", "Computational materials"),
    ("covered-elsewhere", "Material characterization"),
    ("no-source", "Sports engineering"),
    ("covered-elsewhere", "Thermal engineering"),
    (
        "covered-elsewhere",
        (
            "Surface engineering, industrial plant, power plant, project, information, "
            "facilities"
        ),
    ),
    ("umbrella", "Applied engineering, electromechanics, mechatronics"),
    ("no-source", "Geomatics"),
    ("out-of-scope", "Explosives and military engineering"),
    ("not-researched", "Sales and marketing management"),
    ("not-researched", "Customer service management"),
    (
        "not-researched",
        "Facility management (ISO 41001), energy management (ISO 50001)",
    ),
    ("covered-elsewhere", "Treasury, tax, legal departments"),
    ("covered-elsewhere", "Public administration"),
    ("no-source", "Non-profit management"),
    ("out-of-scope", "Self-management and time management"),
]
CHECKED_REASONS = {domain: reason for reason, domain in _CHECKED_REASONS}

HOW_TO_READ_KEYS = [
    "sentence_structure",
    "rule_classes",
    "classification_test",
    "applicability",
    "ids",
    "strength_keywords",
    "relation_keywords",
    "source_quality",
    "evidence_strength",
    "source_domain",
    "rule_names",
    "scope",
]
SECTION_KEYS = {
    1: "how_to_read",
    2: "master_rule",
    3: "overview",
    4: "domain_index",
    5: "glossary",
    6: "rigor_matrix",
    7: "rules",
    8: "conflicts",
    9: "sources_by_rule",
    10: "management_forms",
    11: "quotes",
    12: "method",
}


class ImportError_(Exception):
    """Raised when edition 9 does not have the shape the importer expects."""


# --------------------------------------------------------------------------
# Markdown block tokenizer
# --------------------------------------------------------------------------
@dataclass
class Block:
    kind: str  # "h1", "h2", "h3", "table", "para"
    lines: list[str]
    blank_before: int
    lineno: int

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def heading(self) -> str:
        return self.lines[0].lstrip("#").strip()

    def rows(self) -> list[list[str]]:
        out = []
        for i, line in enumerate(self.lines):
            if i == 1:  # separator row
                continue
            cells = line.strip()[1:-1].split("|")
            out.append([c.strip() for c in cells])
        return out


def tokenize(lines: list[str]) -> list[Block]:
    blocks: list[Block] = []
    blank = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            blank += 1
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(Block("h1", [line], blank, i + 1))
            i += 1
        elif line.startswith("## "):
            blocks.append(Block("h2", [line], blank, i + 1))
            i += 1
        elif line.startswith("### "):
            blocks.append(Block("h3", [line], blank, i + 1))
            i += 1
        elif line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            blocks.append(Block("table", lines[i:j], blank, i + 1))
            i = j
        else:
            j = i
            while (
                j < len(lines)
                and lines[j].strip()
                and not lines[j].startswith(("#", "|"))
            ):
                j += 1
            blocks.append(Block("para", lines[i:j], blank, i + 1))
            i = j
        blank = 0
    return blocks


# --------------------------------------------------------------------------
# Source registry
# --------------------------------------------------------------------------
@dataclass
class Use:
    title: str
    section: int
    lineno: int


@dataclass
class Registry:
    uses: dict[str, list[Use]] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)
    slug: dict[str, str] = field(default_factory=dict)
    title: dict[str, str] = field(default_factory=dict)
    quoted: set[str] = field(default_factory=set)

    def add(self, url: str, title: str, section: int, lineno: int) -> None:
        if url not in self.uses:
            self.uses[url] = []
            self.order.append(url)
        self.uses[url].append(Use(title, section, lineno))

    def finalize(self) -> None:
        for url in self.order:
            best = min(
                self.uses[url], key=lambda u: (TITLE_RANK.get(u.section, 9), u.lineno)
            )
            self.title[url] = best.title
        taken: set[str] = set(FIXED_SLUGS.values()) | set(SLUG_OVERRIDES.values())
        for url in self.order:
            if url in FIXED_SLUGS:
                self.slug[url] = FIXED_SLUGS[url]
                continue
            if url in SLUG_OVERRIDES:
                self.slug[url] = SLUG_OVERRIDES[url]
                continue
            base = slugify(self.title[url])
            cand, n = base, 2
            while cand in taken:
                cand = f"{base}-{n}"
                n += 1
            taken.add(cand)
            self.slug[url] = cand
        if len(set(self.slug.values())) != len(self.slug):
            raise ImportError_("duplicate slugs")

    def cite(self, cell: str, sep: str) -> tuple[list[str], dict[str, str], str | None]:
        """Return (slugs in order, per-use title overrides, text override).

        The text override is the cell with each link replaced by ``[@slug]``;
        it is returned only when the cell is not exactly the ``sep``-joined
        links.
        """
        slugs: list[str] = []
        titles: dict[str, str] = {}
        links = list(LINK_RE.finditer(cell))
        for m in links:
            title, url = m.group(1), m.group(2)
            slug = self.slug[url]
            if slug not in slugs:
                slugs.append(slug)
            if title != self.title[url]:
                if titles.get(slug, title) != title:
                    raise ImportError_(f"two titles for {slug} in one cell: {cell}")
                titles[slug] = title
            elif slug in titles:
                raise ImportError_(f"mixed titles for {slug} in one cell: {cell}")
        plain = sep.join(m.group(0) for m in links)
        text: str | None = None
        if cell != plain or len(slugs) != len(links):
            text = LINK_RE.sub(lambda m: f"[@{self.slug[m.group(2)]}]", cell)
        return slugs, titles, text


def slugify(title: str) -> str:
    t = re.sub(r"\([^()]*\)", " ", title)
    t = t.replace("&", " ").replace("'", "").replace("\u2019", "")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    words = [w for w in re.split(r"[^a-z0-9]+", t.lower()) if w]
    kept = [w for w in words if w not in STOPWORDS] or words
    return "-".join(kept[:5])


def year_of(title: str) -> int | None:
    parens = re.findall(r"\(([^()]*)\)", title)
    for p in reversed(parens):
        m = re.search(r"\b(19\d\d|20\d\d)\b", p)
        if m:
            return int(m.group(1))
    m = re.search(r":(19\d\d|20\d\d)\b", title)
    return int(m.group(1)) if m else None


# --------------------------------------------------------------------------
# Cell parsers
# --------------------------------------------------------------------------
def balanced_suffix(rest: str) -> str | None:
    """If ``rest`` is ``(...)`` with the first paren closing at the end."""
    if not (rest.startswith("(") and rest.endswith(")")):
        return None
    depth = 0
    for i, ch in enumerate(rest):
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0 and i != len(rest) - 1:
            return None
    return rest[1:-1]


def parse_evidence(cell: str) -> tuple[str, str | None, str | None]:
    level = cell.split(" ", 1)[0].rstrip(";")
    if level not in LEVELS:
        raise ImportError_(f"evidence level: {cell}")
    if cell == level:
        return level, None, None
    note = balanced_suffix(cell[len(level) + 1 :]) if cell[len(level)] == " " else None
    if note is not None:
        return level, note, None
    return level, None, cell


def render_related(rel: dict[str, list[str]]) -> str:
    inv = {v: k for k, v in RELATIONS.items()}
    return "; ".join(f"{inv[k]} {', '.join(v)}" for k, v in rel.items())


def parse_related(cell: str) -> tuple[dict[str, list[str]], str | None]:
    rel: dict[str, list[str]] = {}
    for seg in cell.split("; "):
        for phrase in sorted(RELATIONS, key=len, reverse=True):
            if seg.startswith(phrase + " "):
                key = RELATIONS[phrase]
                rest = seg[len(phrase) + 1 :]
                rest = re.sub(r" \(see K\d+\)$", "", rest)
                ids = []
                for tok in rest.split(", "):
                    m = re.match(r"^([URC]\d+)\b", tok)
                    if m:
                        ids.append(m.group(1))
                if ids:
                    rel.setdefault(key, []).extend(ids)
                break
        else:
            raise ImportError_(f"relation: {seg}")
    text = None if render_related(rel) == cell else cell
    return rel, text


# --------------------------------------------------------------------------
# YAML helpers
# --------------------------------------------------------------------------
def to_yaml(obj: Any) -> Any:
    if isinstance(obj, dict):
        m = CommentedMap()
        for k, v in obj.items():
            m[k] = to_yaml(v)
        return m
    if isinstance(obj, list):
        return CommentedSeq([to_yaml(v) for v in obj])
    if isinstance(obj, str) and "\n" in obj:
        return LiteralScalarString(obj)
    return obj


def represent_none(rep: RoundTripRepresenter, _data: None) -> Any:
    return rep.represent_scalar("tag:yaml.org,2002:null", "null")


def dump(name: str, obj: Any, desc: str) -> None:
    yaml = YAML()
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=2, offset=0)
    yaml.representer.add_representer(type(None), represent_none)
    data = to_yaml(obj)
    data.yaml_set_start_comment(
        f"{desc}\n"
        f"Schema: schema/{name}.schema.json. data/ is the single source of truth"
        " (ADR 0003);\nseeded once by sources/import/import_v9.py from edition 9."
    )
    path = DATA_DIR / f"{name}.yaml"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        yaml.dump(data, fh)


# --------------------------------------------------------------------------
# Import
# --------------------------------------------------------------------------
def opt(d: dict[str, Any], key: str, value: Any) -> None:
    """Set an optional override field only when it carries information."""
    if value:
        d[key] = value


def run(report: bool) -> None:
    md_lines = MD_PATH.read_text(encoding="utf-8").split("\n")
    if md_lines[-1] != "":
        raise ImportError_("edition 9 must end with a newline")
    md_lines = md_lines[:-1]
    ed6 = YAML().load(ED6_PATH.read_text(encoding="utf-8"))

    # ---- split into sections --------------------------------------------
    blocks = tokenize(md_lines)
    sections: dict[int, list[Block]] = {0: []}
    sec_heading: dict[int, Block] = {}
    cur = 0
    for b in blocks:
        m = re.match(r"^## (\d+)\. ", b.lines[0]) if b.kind == "h2" else None
        if m:
            cur = int(m.group(1))
            sections[cur] = []
            sec_heading[cur] = b
        else:
            sections.setdefault(cur, []).append(b)

    # layout quirks: any block not preceded by exactly one blank line
    quirks: list[dict[str, Any]] = []
    for idx, b in enumerate(blocks):
        if idx == 0:
            continue
        if b.blank_before != 1:
            sec = 0
            for n, h in sec_heading.items():
                if h.lineno <= b.lineno:
                    sec = max(sec, n)
            quirks.append(
                {
                    "section": sec,
                    "line": b.lineno,
                    "block": b.kind,
                    "starts_with": b.lines[0][:60],
                    "blank_lines_before": b.blank_before,
                }
            )

    # ---- source registry ------------------------------------------------
    reg = Registry()
    sec_of_line: list[int] = []
    cur = 0
    for line in md_lines:
        m = re.match(r"^## (\d+)\. ", line)
        if m:
            cur = int(m.group(1))
        sec_of_line.append(cur)
    for n, line in enumerate(md_lines):
        for m in LINK_RE.finditer(line):
            reg.add(m.group(2), m.group(1), sec_of_line[n], n + 1)
    reg.finalize()

    # ---- header & contents ---------------------------------------------
    head = sections[0]
    title = head[0].heading()
    version_line = head[1].text
    vm = re.match(r"^Version (\S+) · (\S+) · ", version_line)
    if not vm:
        raise ImportError_("version line")
    date = vm.group(2)
    contents_items = [re.sub(r"^\d+\. ", "", ln) for ln in head[3].lines]

    section_meta: list[dict[str, Any]] = []
    for n in range(1, 13):
        heading = sec_heading[n].heading().split(". ", 1)[1]
        entry: dict[str, Any] = {"key": SECTION_KEYS[n], "number": n, "title": heading}
        if contents_items[n - 1] != heading:
            entry["contents_title"] = contents_items[n - 1]
        section_meta.append(entry)
    smeta = {e["number"]: e for e in section_meta}

    # ---- section 1: how to read ------------------------------------------
    s1 = sections[1]
    bullets: list[list[str]] = []
    for ln in s1[0].lines:
        if ln.startswith("- "):
            bullets.append([ln[2:]])
        else:
            bullets[-1].append(ln)
    if len(bullets) != len(HOW_TO_READ_KEYS):
        raise ImportError_("section 1 bullets")
    how_to_read = [
        {"key": k, "text": "\n".join(b)}
        for k, b in zip(HOW_TO_READ_KEYS, bullets, strict=True)
    ]
    btext = {k: b for k, b in zip(HOW_TO_READ_KEYS, bullets, strict=True)}

    def sub_items(lines: list[str], pattern: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for ln in lines[1:]:
            m = re.match(pattern, ln)
            if not m:
                raise ImportError_(f"sub-bullet: {ln}")
            out[m.group(1)] = m.group(2)
        return out

    prefixes = {}
    for ln in btext["rule_classes"][1:]:
        m = re.match(r"^  - \*\*([URCK]) = ([^.]+)\.\*\* (.*)$", ln)
        if not m:
            raise ImportError_(f"prefix: {ln}")
        prefixes[m.group(1)] = {"name": m.group(2), "description": m.group(3)}
    strengths = sub_items(
        btext["strength_keywords"], r"^  - \*\*(MUST|SHOULD)\*\* = (.*)$"
    )
    relkw = sub_items(btext["relation_keywords"], r"^  - \*\*([a-z ]+)\*\* = (.*)$")
    ed6_rel = ed6["meta"]["relation_types"]
    relation_types: dict[str, str] = {}
    for phrase, rel_desc in relkw.items():
        key = RELATIONS[phrase]
        rel_main = re.sub(
            r" \*\*(strengthened by|checked by)\*\* is the inverse\.$", "", rel_desc
        )
        relation_types[key] = rel_main
        if rel_main != rel_desc:
            inv = "strengthened_by" if key == "strengthens" else "checked_by"
            relation_types[inv] = ed6_rel[inv]
    evid = sub_items(
        btext["evidence_strength"], r"^  - \*\*(strong|moderate|weak)\*\* = (.*)$"
    )

    def after_label(lines: list[str]) -> str:
        return re.sub(r"^\*\*[^*]+\*\* ", "", lines[0])

    classification_test = after_label(btext["classification_test"])
    applicability_note = after_label(btext["applicability"])

    # ---- section 2: master rule -----------------------------------------
    s2 = sections[2]
    steps = s2[0].lines
    regions = {r[0]: r[1] for r in s2[1].rows()[1:]}
    terms = [
        {"engineering": r[0], "management": r[1], "source": r[2]}
        for r in s2[3].rows()[1:]
    ]
    master_sources_cell = None

    # ---- section 3: overview --------------------------------------------
    s3 = sections[3]
    smeta[3]["intro"] = s3[0].text
    qv_title = s3[1].heading()
    qv_intro = s3[2].text
    quick_view = {r[0].split(".", 1)[0]: r[1] for r in s3[3].rows()[1:]}
    am_title = s3[4].heading()
    am_intro = s3[5].text
    analogy = [
        {"engineering": r[0], "management": r[1], "role": r[2]}
        for r in s3[6].rows()[1:]
    ]
    rpc_title = s3[7].heading()
    rpc_lines = s3[8].lines
    smeta[3]["subsections"] = {"rules_per_category": rpc_title}

    # ---- section 7: rules -----------------------------------------------
    s7 = sections[7]
    categories: list[dict[str, Any]] = []
    rules: dict[str, dict[str, Any]] = {}
    i = 0
    while i < len(s7):
        h = s7[i]
        cid, cname = h.heading().split(". ", 1)
        desc = s7[i + 1].text
        main, detail = s7[i + 2].rows(), s7[i + 3].rows()
        ids = []
        for r in main[1:]:
            rid, name, strength, cond, then, because, example = r
            ids.append(rid)
            rules[rid] = {
                "id": rid,
                "name": name,
                "strength": strength,
                "category": cid,
                "if": cond,
                "then": then,
                "because": because,
                "example": example,
            }
        for r in detail[1:]:
            rid, cls, check, violation, related, evidence, sdomain = r
            cname_, note = cls.split(": ", 1)
            rules[rid].update(
                {
                    "class": cname_,
                    "class_note": note,
                    "check": check,
                    "violation": violation,
                    "related_cell": related,
                    "evidence_cell": evidence,
                    "source_domain": sdomain,
                }
            )
        categories.append({"id": cid, "name": cname, "description": desc, "rules": ids})
        i += 4
    tables = {
        "rules_main": s7[2].rows()[0],
        "rules_detail": s7[3].rows()[0],
    }

    # cross-check section 3 "Rules per category"
    rpc_issues: list[str] = []
    cat_iter = iter(categories)
    cur_cat: dict[str, Any] | None = None
    listed: list[str] = []
    for ln in rpc_lines:
        m = re.match(r"^- \*\*([A-K])\. ([^*]+)\*\* — (.*)$", ln)
        if m:
            if cur_cat is not None and listed != cur_cat["rules"]:
                rpc_issues.append(
                    f"section 3 order/membership differs for {cur_cat['id']}"
                )
            if m.group(1) == "K":
                cur_cat = None
                continue
            cur_cat = next(cat_iter)
            listed = []
            if (m.group(2), m.group(3)) != (cur_cat["name"], cur_cat["description"]):
                rpc_issues.append(f"section 3 heading differs for {m.group(1)}")
            continue
        m = re.match(r"^  - (\S+) (.*) \((MUST|SHOULD)\)$", ln)
        if not m:
            raise ImportError_(f"rules per category: {ln}")
        rid = m.group(1)
        listed.append(rid)
        if (m.group(2), m.group(3)) != (rules[rid]["name"], rules[rid]["strength"]):
            rpc_issues.append(f"section 3 name/strength differs for {rid}")

    # ---- section 9: sources by rule --------------------------------------
    s9 = sections[9]
    tables["sources_by_rule"] = s9[0].rows()[0]
    s9_order: list[str] = []
    for r in s9[0].rows()[1:]:
        rid, cell = r
        slugs, titles, text = reg.cite(cell, "; ")
        if text is not None:
            raise ImportError_(f"section 9 cell is not a plain list: {rid}")
        if rid == "Master rule":
            master_sources_cell = (slugs, titles)
            continue
        s9_order.append(rid)
        rules[rid]["sources"] = slugs
        rules[rid]["source_titles"] = titles

    # ---- section 10: management forms ------------------------------------
    s10 = sections[10]
    smeta[10]["intro"] = s10[0].text
    mf_headers: dict[str, list[str]] = {}
    mf_title_overrides: dict[str, str] = {}
    mf_order: dict[str, list[str]] = {}
    i = 1
    while i < len(s10):
        cid, ctitle = s10[i].heading().split(". ", 1)
        cat = next(c for c in categories if c["id"] == cid)
        if ctitle != cat["name"]:
            mf_title_overrides[cid] = ctitle
        rows = s10[i + 1].rows()
        mf_headers[cid] = rows[0]
        mf_order[cid] = []
        for r in rows[1:]:
            rid, rname, mname, form, example, scell, ecell = r
            slugs, titles, text = reg.cite(scell, "; ")
            level, enote, etext = parse_evidence(ecell)
            mgmt: dict[str, Any] = {
                "name": rname,
                "form_name": mname,
                "form": form,
                "example": example,
                "sources": slugs,
            }
            opt(mgmt, "source_titles", titles)
            opt(mgmt, "sources_text", text)
            mgmt["evidence"] = level
            mgmt["evidence_note"] = enote
            opt(mgmt, "evidence_text", etext)
            rules[rid]["management"] = mgmt
            mf_order[cid].append(rid)
        i += 2
    # default header = the most common one; others are per-category overrides
    common = Counter(tuple(h) for h in mf_headers.values()).most_common(1)[0][0]
    mf_default = list(common)
    mf_header_overrides = {c: h for c, h in mf_headers.items() if h != mf_default}
    tables["management_forms"] = mf_default
    smeta[10]["header_overrides"] = mf_header_overrides
    smeta[10]["category_titles"] = mf_title_overrides
    mf_issues: list[str] = []
    for cid, order in mf_order.items():
        cat_rules = [
            r
            for r in next(c for c in categories if c["id"] == cid)["rules"]
            if r in order
        ]
        if cat_rules != order:
            mf_issues.append(f"section 10 order differs from category order in {cid}")
    for rid, rec in rules.items():
        if "management" in rec and rec["management"]["name"] != rec["name"]:
            mf_issues.append(f"section 10 rule name differs for {rid}")

    # ---- finish rules ------------------------------------------------------
    rule_out: list[dict[str, Any]] = []
    for rid in s9_order:
        rec = rules[rid]
        rel, rel_text = parse_related(rec["related_cell"])
        level, enote, etext = parse_evidence(rec["evidence_cell"])
        o: dict[str, Any] = {
            "id": rid,
            "name": rec["name"],
            "class": rec["class"],
            "class_note": rec["class_note"],
            "strength": rec["strength"],
            "category": rec["category"],
            "if": rec["if"],
            "then": rec["then"],
            "because": rec["because"],
            "example": rec["example"],
            "check": rec["check"],
            "violation": rec["violation"],
            "related": rel,
        }
        opt(o, "related_text", rel_text)
        o["evidence"] = level
        o["evidence_note"] = enote
        opt(o, "evidence_text", etext)
        o["source_domain"] = rec["source_domain"]
        if rec["class"] == "conditional":
            if not rec["class_note"].startswith("counterexample: "):
                raise ImportError_(f"counterexample: {rid}")
            o["counterexample"] = rec["class_note"][len("counterexample: ") :]
        o["notes"] = None
        o["sources"] = rec["sources"]
        opt(o, "source_titles", rec["source_titles"])
        o["management"] = rec.get("management")
        rule_out.append(o)
    if set(s9_order) != set(rules):
        raise ImportError_("section 9 does not list every rule")

    # ---- section 8: conflicts ---------------------------------------------
    s8 = sections[8]
    tables["conflicts"] = s8[0].rows()[0]
    conflicts = []
    for r in s8[0].rows()[1:]:
        kid, cond, then, because, example, basis = r
        ids = []
        for t in ID_RE.findall(cond):
            if t not in ids:
                ids.append(t)
        conflicts.append(
            {
                "id": kid,
                "if": cond,
                "then": then,
                "because": because,
                "example": example,
                "basis": basis,
                "rules": ids,
            }
        )

    # ---- section 4: domains -----------------------------------------------
    s4 = sections[4]
    intro_paras: list[str] = []
    k = 0
    while s4[k].kind == "para":
        intro_paras.append(s4[k].text)
        k += 1
    smeta[4]["intro"] = "\n\n".join(intro_paras)
    domains: list[dict[str, Any]] = []
    checked: list[dict[str, Any]] = []
    branch = ""
    names = {r["id"]: r["name"] for r in rule_out}
    while k < len(s4):
        b = s4[k]
        if b.kind == "h3":
            branch = b.heading()
            k += 1
            continue
        if b.kind == "para":  # intro of "Checked without a separate row"
            smeta[4]["checked_without_row"] = {"title": branch, "intro": b.text}
            k += 1
            continue
        rows = b.rows()
        if branch == "Checked without a separate row":
            tables["checked_without_row"] = rows[0]
            for r in rows[1:]:
                checked.append(
                    {
                        "domain": r[0],
                        "reason": CHECKED_REASONS[r[0]],
                        "note": r[1],
                        "applicable": r[2],
                    }
                )
        else:
            tables["domains"] = rows[0]
            for r in rows[1:]:
                dname, rcell, refcell = r
                rids: list[str] = []
                supports: list[str] = []
                rendered = []
                for item in rcell.split("; "):
                    m = re.match(r"^(Master rule|[URC]\d+)\b", item)
                    if not m:
                        raise ImportError_(f"domain rule: {item}")
                    rid = MASTER if m.group(1) == "Master rule" else m.group(1)
                    rids.append(rid)
                    sup = item.endswith(" (supports)")
                    if sup:
                        supports.append(rid)
                    label = "Master rule" if rid == MASTER else f"{rid} {names[rid]}"
                    rendered.append(label + (" (supports)" if sup else ""))
                slugs, titles, text = reg.cite(refcell, " ")
                if text is not None:
                    raise ImportError_(f"domain refs not plain: {dname}")
                d: dict[str, Any] = {"branch": branch, "domain": dname, "rules": rids}
                opt(d, "supports", supports)
                if "; ".join(rendered) != rcell:
                    d["rules_text"] = rcell
                d["references"] = slugs
                opt(d, "reference_titles", titles)
                domains.append(d)
        k += 1

    # ---- section 5: glossary ----------------------------------------------
    s5 = sections[5]
    smeta[5]["intro"] = s5[0].text
    tables["glossary"] = s5[1].rows()[0]
    glossary = {r[0]: {"meaning": r[1], "not_same_as": r[2]} for r in s5[1].rows()[1:]}

    # ---- section 6: rigor matrix ------------------------------------------
    s6 = sections[6]
    smeta[6]["intro"] = s6[0].text
    rm_rows = s6[1].rows()
    tables["rigor_matrix"] = rm_rows[0]
    rigor = []
    for r in rm_rows[1:]:
        cons = re.match(r"^\*\*(Low|High) consequence\*\*$", r[0])
        if not cons:
            raise ImportError_("rigor row")
        for unc, cell in zip(("low", "high"), r[1:], strict=True):
            m = re.match(r"^(.*)\. Checker level: (\w+) \(U8\)\.$", cell)
            if not m:
                raise ImportError_(f"rigor cell: {cell}")
            rigor.append(
                {
                    "consequence": cons.group(1).lower(),
                    "uncertainty": unc,
                    "apply": m.group(1).split(", "),
                    "checker_level": m.group(2),
                }
            )

    # ---- section 11: quotes -----------------------------------------------
    s11 = sections[11]
    smeta[11]["intro"] = s11[0].text
    groups: list[dict[str, Any]] = []
    quotes: list[dict[str, Any]] = []
    qn = 0
    k = 1
    group_keys = ["master_rule", "management_rules", "management_other"]
    while k < len(s11):
        gtitle = s11[k].heading()
        rows = s11[k + 1].rows()
        gkey = group_keys[len(groups)]
        groups.append({"key": gkey, "title": gtitle, "header": rows[0]})
        for r in rows[1:]:
            label, scell, qtext = r
            qn += 1
            rids = []
            if label.startswith("Master rule"):
                rids.append(MASTER)
            for t in ID_RE.findall(label):
                if t not in rids:
                    rids.append(t)
            slugs, titles, text = reg.cite(scell, "; ")
            for m in LINK_RE.finditer(scell):
                reg.quoted.add(m.group(2))
            q: dict[str, Any] = {
                "id": f"Q{qn}",
                "rules": rids,
                "source": slugs[0] if slugs else None,
                "text": qtext,
                "locator": None,
                "group": gkey,
            }
            if label != ", ".join(rids):
                q["rule_label"] = label
            opt(q, "extra_sources", slugs[1:])
            opt(q, "source_titles", titles)
            opt(q, "sources_text", text)
            quotes.append(q)
        k += 2
    smeta[11]["groups"] = groups

    # ---- section 12: method -----------------------------------------------
    s12 = sections[12]
    method = []
    k = 0
    while k < len(s12):
        stitle = s12[k].heading()
        parts = []
        k += 1
        while k < len(s12) and s12[k].kind != "h3":
            parts.append(
                LINK_RE.sub(lambda m: f"[@{reg.slug[m.group(2)]}]", s12[k].text)
            )
            for m in LINK_RE.finditer(s12[k].text):
                if m.group(1) != reg.title[m.group(2)]:
                    raise ImportError_("section 12 link title is not canonical")
            k += 1
        method.append({"section": stitle, "text": "\n\n".join(parts)})

    # ---- master rule tables -------------------------------------------------
    tables["master_rule_regions"] = s2[1].rows()[0]
    tables["master_rule_terms"] = s2[3].rows()[0]
    tables["quick_view"] = s3[3].rows()[0]
    tables["analogy_map"] = s3[6].rows()[0]
    if not steps[0].startswith("1. ") or not steps[1].startswith("2. "):
        raise ImportError_("master rule steps")
    assert master_sources_cell is not None
    master_rule: dict[str, Any] = {
        "scale": steps[0][3:],
        "alarp": steps[1][3:],
        "risk_regions": regions,
        "sources": master_sources_cell[0],
    }
    opt(master_rule, "source_titles", master_sources_cell[1])
    master_rule["management_intro"] = s2[2].text
    master_rule["management_terms"] = terms

    # ---- sources.yaml ---------------------------------------------------------
    source_out = []
    for url in reg.order:
        host = url.split("/")[2].lower()
        ov = URL_OVERRIDES.get(url, {})
        if host not in HOSTS and "kind" not in ov:
            raise ImportError_(f"no classification for {url}")
        kind, publisher, paid, src_note = HOSTS.get(host, (P, None, False, None))
        kind = ov.get("kind", kind)
        publisher = ov.get("publisher", publisher)
        paid = ov.get("paid", paid)
        src_note = ov.get("note", src_note)
        src: dict[str, Any] = {
            "slug": reg.slug[url],
            "title": reg.title[url],
            "url": url,
            "kind": kind,
            "publisher": publisher,
            "year": year_of(reg.title[url]),
        }
        if "via" in ov:
            src["via"] = {"title": ov["via"], "url": url}
        src["paid"] = paid
        src["accessed"] = "2026-10-14" if url in reg.quoted else None
        src["notes"] = src_note
        source_out.append(src)

    # ---- meta.yaml -------------------------------------------------------------
    meta: dict[str, Any] = {
        "title": title,
        "edition": EDITION,
        "date": date,
        "master_rule": master_rule,
        "sentence_structure": ed6["meta"]["sentence_structure"],
        "id_prefixes": prefixes,
        "classification_test": classification_test,
        "applicability_note": applicability_note,
        "quick_view_questions": quick_view,
        "strength_keywords": strengths,
        "relation_types": relation_types,
        "evidence_levels": evid,
        "how_to_read": how_to_read,
        "known_exceptions": [
            {
                "rule": "C15",
                "check": "primary-source",
                "reason": (
                    "secondary only; the primary source, Brooks's 1975 book, "
                    "is not online"
                ),
            }
        ],
        "sections": section_meta,
        "quick_view": {"title": qv_title, "intro": qv_intro},
        "analogy_map": {"title": am_title, "intro": am_intro, "rows": analogy},
        "tables": tables,
        "layout_quirks": quirks,
    }

    history = {
        "editions": [
            {
                "edition": EDITION,
                "date": date,
                "summary": (
                    "First published edition of the taxonomy: 83 rules (58 universal, "
                    "9 risk-scaled, 16 conditional) and 8 conflict rules "
                    "in 9 categories."
                ),
            }
        ],
        "id_map": [],
    }

    DATA_DIR.mkdir(exist_ok=True)
    dump("meta", meta, "Taxonomy metadata, section prose and layout.")
    dump("categories", categories, "Rule categories A-I in lifecycle order.")
    dump("rules", rule_out, "The 83 rules (U, R, C), in ID order.")
    dump("conflicts", conflicts, "Conflict rules (K).")
    dump("sources", source_out, "Source registry; prose cites these as [@slug].")
    dump("quotes", quotes, "Direct quotes (section 11), verbatim.")
    dump(
        "domains", {"domains": domains, "checked_without_row": checked}, "Domain index."
    )
    dump("glossary", glossary, "Glossary: one meaning per term.")
    dump("rigor_matrix", rigor, "Rigor matrix: which rules apply in which cell.")
    dump("method", method, "Section 12, method and limits, as ordered prose blocks.")
    dump("history", history, "Edition history and old-to-new ID map.")

    if report:
        print_report(
            ed6,
            rule_out,
            categories,
            conflicts,
            glossary,
            domains,
            checked,
            meta,
            rigor,
            reg,
            rpc_issues + mf_issues,
        )


# --------------------------------------------------------------------------
# Edition-6 vs edition-9 report
# --------------------------------------------------------------------------
def unescape(s: str) -> str:
    return s.replace("\\<", "<").replace("\\[", "[").replace("\\]", "]")


def print_report(
    ed6: Any,
    rules: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    glossary: dict[str, Any],
    domains: list[dict[str, Any]],
    checked: list[dict[str, Any]],
    meta: dict[str, Any],
    rigor: list[dict[str, Any]],
    reg: Registry,
    issues: list[str],
) -> None:
    out = sys.stdout.write
    out("== edition 6 vs edition 9 (edition 9 kept everywhere) ==\n")
    r9 = {r["id"]: r for r in rules}
    r6 = {r["id"]: r for r in ed6["rules"]}
    out(
        f"rules: ed6 {len(r6)}, ed9 {len(r9)}; "
        f"added in ed9: {sorted(set(r9) - set(r6))}\n"
    )
    for rid, a in r6.items():
        b = r9[rid]
        for f in (
            "name",
            "class",
            "class_note",
            "strength",
            "category",
            "if",
            "then",
            "because",
            "example",
            "check",
            "violation",
            "source_domain",
            "evidence",
        ):
            va, vb = str(a.get(f)), str(b.get(f))
            if va != vb:
                kind = "escape-only" if va == unescape(vb) else "text"
                out(f"  {rid}.{f} [{kind}]: ed6={va!r} | ed9={vb!r}\n")
        en6 = a.get("evidence_note")
        en9 = b.get("evidence_note") or b.get("evidence_text")
        if str(en6) != str(en9):
            out(f"  {rid}.evidence_note: ed6={en6!r} | ed9={en9!r}\n")
        rel6 = {k: sorted(v) for k, v in (a.get("related") or {}).items()}
        rel9 = {k: sorted(v) for k, v in b["related"].items()}
        if rel6 != rel9:
            out(f"  {rid}.related: ed6={rel6} | ed9={rel9}\n")
        elif list(a.get("related") or {}) != list(b["related"]):
            out(
                f"  {rid}.related order: ed6={list(a['related'])} "
                f"| ed9={list(b['related'])}\n"
            )
        u6 = list(a.get("sources") or [])
        slug_url = {v: k for k, v in reg.slug.items()}
        u9 = [slug_url[s] for s in b["sources"]]
        if u6 != u9:
            out(
                f"  {rid}.sources: removed={[u for u in u6 if u not in u9]} "
                f"added={[u for u in u9 if u not in u6]}\n"
            )
    for c6 in ed6["categories"]:
        c9 = next(c for c in categories if c["id"] == c6["id"])
        for f in ("name", "description"):
            if c6[f] != c9[f]:
                out(f"  category {c6['id']}.{f}: {c6[f]!r} | {c9[f]!r}\n")
        if c6["rules"] != c9["rules"]:
            out(
                f"  category {c6['id']}.rules: "
                f"+{[r for r in c9['rules'] if r not in c6['rules']]}\n"
            )
    m6 = ed6["meta"]
    for k6, v6 in m6["quick_view_questions"].items():
        if v6 != meta["quick_view_questions"][k6]:
            out(f"  quick_view {k6}: {v6!r} | {meta['quick_view_questions'][k6]!r}\n")
    for f in ("strength_keywords", "evidence_levels", "relation_types", "id_prefixes"):
        out(f"  meta.{f}: ed6={dict(m6[f])} | ed9={meta[f]}\n")
    for f in ("classification_test", "applicability_note"):
        if m6[f] != meta[f]:
            out(f"  meta.{f}: ed6={m6[f]!r} | ed9={meta[f]!r}\n")
    mr6 = m6["master_rule"]
    for f in ("scale", "alarp"):
        if mr6[f] != meta["master_rule"][f]:
            out(f"  master_rule.{f} differs\n")
    if dict(mr6["risk_regions"]) != meta["master_rule"]["risk_regions"]:
        out("  master_rule.risk_regions differs\n")
    if m6["title"] != meta["title"]:
        out("  title differs\n")
    for term, v in glossary.items():
        g6 = ed6["glossary"].get(term)
        if g6 is None:
            out(f"  glossary + {term!r}\n")
        elif (g6["meaning"], g6["not_same_as"]) != (v["meaning"], v["not_same_as"]):
            out(f"  glossary {term!r}: ed6={dict(g6)} | ed9={v}\n")
    for term in ed6["glossary"]:
        if term not in glossary:
            out(f"  glossary - {term!r}\n")
    rm6 = [
        (c["consequence"], c["uncertainty"], list(c["apply"]), c["checker_level"])
        for c in ed6["rigor_matrix"]
    ]
    rm9 = [
        (c["consequence"], c["uncertainty"], c["apply"], c["checker_level"])
        for c in rigor
    ]
    for a6, a9 in zip(rm6, rm9, strict=True):
        if a6 != a9:
            out(f"  rigor_matrix {a6[0]}/{a6[1]}: ed6={a6[2]} | ed9={a9[2]}\n")
    k9 = {c["id"]: c for c in conflicts}
    for c6 in ed6["conflict_rules"]:
        for f in ("if", "then", "because", "example", "basis"):
            if c6[f] != k9[c6["id"]][f]:
                out(f"  {c6['id']}.{f}: {c6[f]!r} | {k9[c6['id']][f]!r}\n")
    out(f"  conflicts: ed6 {len(ed6['conflict_rules'])}, ed9 {len(conflicts)}\n")
    d6 = {(d["branch"], d["domain"]): d for d in ed6["domains"]}
    d9 = {(d["branch"], d["domain"]): d for d in domains}
    out(
        f"  domains: ed6 {len(d6)} rows, ed9 {len(d9)} rows; "
        f"added {len(set(d9) - set(d6))}, removed {sorted(set(d6) - set(d9))}\n"
    )
    slug_url = {v: k for k, v in reg.slug.items()}
    for key in sorted(set(d6) & set(d9)):
        a, b = d6[key], d9[key]
        if list(a["rules"]) != b["rules"]:
            out(
                f"  domain {key[1]!r}.rules: "
                f"ed6={list(a['rules'])} | ed9={b['rules']}\n"
            )
        ref6 = [(x["title"], x["url"]) for x in a["references"]]
        ref9 = [
            (b.get("reference_titles", {}).get(s, reg.title[slug_url[s]]), slug_url[s])
            for s in b["references"]
        ]
        if ref6 != ref9:
            out(f"  domain {key[1]!r}.references: ed6={ref6} | ed9={ref9}\n")
    order6 = [k for k in d6]
    order9 = [k for k in d9 if k in d6]
    if [k for k in order6 if k in d9] != order9:
        out("  domains: row order differs (edition 9 table order kept)\n")
    c6 = {c["domain"]: c for c in ed6["domains_checked_without_row"]}
    for c in checked:
        a = c6.get(c["domain"])
        if a is None:
            out(f"  checked_without_row + {c['domain']!r}\n")
        elif (a["reason"], a["applicable_by_cross_reference"]) != (
            c["note"],
            c["applicable"],
        ):
            out(f"  checked_without_row {c['domain']!r} differs\n")
    out(
        "  dropped ed6 fields: rules[].sources_wikipedia_only, rules[].former_id, "
        "id_map_v5_to_v6, meta.version\n"
    )
    out("== title variants (URL used under more than one title) ==\n")
    for url in reg.order:
        titles = []
        for u in reg.uses[url]:
            if u.title not in titles:
                titles.append(u.title)
        if len(titles) > 1:
            out(f"  {reg.slug[url]} <{url}>\n")
            for t in titles:
                secs = sorted({u.section for u in reg.uses[url] if u.title == t})
                mark = "*" if t == reg.title[url] else " "
                out(f"    {mark} {t!r} (sections {secs})\n")
    out("== cross-checks inside edition 9 ==\n")
    for s in issues:
        out(f"  {s}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0] if __doc__ else None
    )
    parser.add_argument(
        "--report", action="store_true", help="print the edition-6 vs 9 report"
    )
    args = parser.parse_args()
    run(args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
