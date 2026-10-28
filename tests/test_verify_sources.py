"""Offline tests for ``taxonomy verify-sources`` (fake transport, fake clock)."""

from __future__ import annotations

import email.message
import gzip
import hashlib
import http.client
import io
import json
import shutil
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from taxonomy import verify_sources as vs
from taxonomy.cli import main
from taxonomy.load import load_registry
from taxonomy.model import Source

FIXTURES = Path(__file__).parent / "fixtures" / "verify"


def make_pdf(text: str) -> bytes:
    """A minimal one-page PDF showing ``text`` (authored here, not third-party)."""
    stream = f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET".encode()
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 600 200] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objs) + 1,
        xref,
    )
    return out


def ok(body: bytes | str, ctype: str = "text/html", **headers: str) -> vs.HttpResponse:
    data = body.encode() if isinstance(body, str) else body
    return vs.HttpResponse(200, {"content-type": ctype, **headers}, data, "")


def status(code: int) -> vs.HttpResponse:
    return vs.HttpResponse(code, {}, b"nope", "")


class FakeTransport:
    """url -> queue of responses (the last one repeats); records calls."""

    def __init__(self, routes: Mapping[str, list[vs.HttpResponse]]) -> None:
        self.routes = {k: list(v) for k, v in routes.items()}
        self.calls: list[tuple[str, dict[str, str]]] = []

    def request(
        self, url: str, headers: Mapping[str, str], timeout: float
    ) -> vs.HttpResponse:
        self.calls.append((url, dict(headers)))
        queue = self.routes.get(url)
        if not queue:
            return vs.HttpResponse(0, {}, b"", url, "no route")
        resp = queue.pop(0) if len(queue) > 1 else queue[0]
        return vs.HttpResponse(resp.status, resp.headers, resp.body, url, resp.error)


class Clock:
    def __init__(self) -> None:
        self.t = 1000.0
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.slept.append(s)
        self.t += s


def fetcher(
    tmp_path: Path,
    routes: Mapping[str, list[vs.HttpResponse]],
    *,
    offline: bool = False,
    now: Callable[[], datetime] | None = None,
) -> tuple[vs.Fetcher, FakeTransport, Clock]:
    clock = Clock()
    transport = FakeTransport(routes)
    f = vs.Fetcher(
        transport,
        vs.Cache(tmp_path / "cache"),
        vs.Throttle(2.0, clock.now, clock.sleep),
        offline=offline,
        now=now or (lambda: datetime(2026, 10, 20, tzinfo=UTC)),
        sleep=clock.sleep,
    )
    return f, transport, clock


def src(url: str, **extra: object) -> Source:
    return {"slug": "s", "title": "S", "url": url, **extra}  # type: ignore[typeddict-item]


# -- normalization ---------------------------------------------------------


def test_normalize_typography() -> None:
    assert vs.normalize("“It’s — fine”") == '"it"s - fine"'
    assert vs.normalize("Simplicity--the art") == "simplicity-the art"
    assert vs.normalize("a…b") == "a...b"


def test_normalize_nfkc_soft_hyphen_and_breaks() -> None:
    assert vs.normalize("ﬁnal") == "final"  # ligature
    assert vs.normalize("exam­ple") == "example"
    assert vs.normalize("exam-\n  ple  and\n\tmore") == "example and more"


def test_hyphen_variants_match() -> None:
    hay = vs.normalize("a state‑of‑the art  exam-\nple")
    assert vs.score_segment("state-of-the-art example", hay) == 1.0


def test_normalize_modifier_letter_apostrophe() -> None:
    # CAIB PDF text spells apostrophes U+02BC; the quote uses a plain one.
    hay = vs.normalize("the Boardʼs findings were clear")
    assert vs.normalize("Board's") == vs.normalize("Boardʼs") == 'board"s'
    assert vs.score_segment("the Board's findings were clear", hay) == 1.0


def test_quoted_segments() -> None:
    text = 'Intro: "First passage here." and “Second one”, "no"'
    assert vs.quoted_segments(text) == ["First passage here.", "Second one"]


def test_ellipsis_split_requires_order() -> None:
    hay = vs.normalize("alpha beta gamma delta epsilon zeta")
    assert vs.score_segment("alpha beta … epsilon zeta", hay) == 1.0
    assert vs.score_segment("alpha beta [...] epsilon zeta", hay) == 1.0
    assert vs.score_segment("epsilon zeta ... alpha beta", hay) < 1.0


def test_near_miss_score() -> None:
    hay = vs.normalize("Filler. The quick brown fox jumps over the lazy dog. More.")
    score = vs.score_segment("The quick brown fox jumped over the lazy dog", hay)
    assert 0.8 <= score < 1.0
    assert vs.score_segment("completely unrelated sentence xyz", hay) < 0.8


# -- extraction ------------------------------------------------------------


def test_html_extraction_drops_script_and_style() -> None:
    body = (FIXTURES / "page.html").read_bytes()
    text = vs.normalize(vs.extract_text(body, "text/html; charset=utf-8"))
    assert "should not appear" not in text and "also hidden" not in text
    assert 'defines "risk appetite" in the context' in text
    assert vs.score_segment("state-of-the-art example stays", text) == 1.0


def test_pdf_extraction() -> None:
    body = make_pdf("Hello verified world")
    text = vs.extract_text(body, "application/pdf")
    assert "Hello verified world" in text


def test_bad_pdf_raises() -> None:
    with pytest.raises(ValueError, match="unreadable PDF"):
        vs.extract_text(b"%PDF-1.4 garbage", "application/pdf")


def test_plain_text() -> None:
    assert vs.extract_text("café".encode(), "text/plain") == "café"


# -- fetching --------------------------------------------------------------


def test_fetch_order_origin_via_archive(tmp_path: Path) -> None:
    snap = "http://web.archive.org/web/20261010101010/https://o.example/doc"
    avail = json.dumps(
        {"archived_snapshots": {"closest": {"available": True, "url": snap}}}
    )
    wb = f"{vs.WAYBACK_API}?url=https%3A%2F%2Fo.example%2Fdoc&timestamp=20261014"
    raw = "https://web.archive.org/web/20261010101010id_/https://o.example/doc"
    f, transport, _ = fetcher(
        tmp_path,
        {
            "https://o.example/doc": [status(403)],
            "https://v.example/doc": [status(503), status(503), status(503)],
            wb: [ok(avail, "application/json")],
            raw: [ok("<p>archived text</p>")],
        },
    )
    got = f.fetch_source(
        src("https://o.example/doc", via={"title": "V", "url": "https://v.example/doc"})
    )
    assert (got.status, got.method) == ("ok", "archive")
    urls = [u for u, _ in transport.calls]
    assert urls[0] == "https://o.example/doc"
    assert urls.count("https://v.example/doc") == 3  # 1 try + 2 retries
    assert urls[-2:] == [wb, raw]
    assert transport.calls[0][1]["User-Agent"] == vs.USER_AGENT


def test_no_retry_on_404_and_failure_kinds(tmp_path: Path) -> None:
    f, transport, _ = fetcher(tmp_path, {"https://o.example/a": [status(404)]})
    got = f.fetch_source(src("https://o.example/a"))
    assert got.status == "gone"
    assert [u for u, _ in transport.calls].count("https://o.example/a") == 1
    f2, _, _ = fetcher(tmp_path / "x", {"https://o.example/b": [status(403)]})
    assert f2.fetch_source(src("https://o.example/b")).status == "blocked"


def test_conditional_revalidation(tmp_path: Path) -> None:
    url = "https://o.example/doc"
    clock = {"now": datetime(2026, 10, 20, tzinfo=UTC)}
    f, transport, _ = fetcher(
        tmp_path,
        {url: [ok("<p>one</p>", etag='"v1"', **{"last-modified": "Mon"})]},
        now=lambda: clock["now"],
    )
    first = f.get(url, "origin")
    assert not first.from_cache
    # Fresh: no request at all (new Fetcher, same cache).
    f2 = vs.Fetcher(
        FakeTransport({}),
        vs.Cache(tmp_path / "cache"),
        vs.Throttle(),
        now=lambda: clock["now"] + timedelta(hours=1),
    )
    assert f2.get(url, "origin").from_cache
    # Stale: conditional request, 304 reuses the cached body.
    clock["now"] += timedelta(days=8)
    t3 = FakeTransport({url: [status(304)]})
    f3 = vs.Fetcher(
        t3, vs.Cache(tmp_path / "cache"), vs.Throttle(), now=lambda: clock["now"]
    )
    again = f3.get(url, "origin")
    assert again.status == "ok" and again.body == first.body
    sent = t3.calls[0][1]
    assert sent["If-None-Match"] == '"v1"' and sent["If-Modified-Since"] == "Mon"


def test_offline_uses_only_cache(tmp_path: Path) -> None:
    url = "https://o.example/doc"
    f, _, _ = fetcher(tmp_path, {url: [ok("<p>x</p>")]})
    f.get(url, "origin")
    off, transport, _ = fetcher(tmp_path, {}, offline=True)
    assert off.get(url, "origin").from_cache
    assert off.get("https://o.example/other", "origin").status == "timeout"
    assert transport.calls == []


def test_each_url_fetched_once(tmp_path: Path) -> None:
    url = "https://o.example/doc"
    f, transport, _ = fetcher(tmp_path, {url: [ok("<p>x</p>")]})
    f.get(url, "origin")
    f.get(url, "origin")
    assert len(transport.calls) == 1


def test_per_host_spacing_fake_clock() -> None:
    clock = Clock()
    t = vs.Throttle(2.0, clock.now, clock.sleep)
    t.wait("https://a.example/1")
    t.wait("https://b.example/1")  # other host: no wait
    assert clock.slept == []
    t.wait("https://a.example/2")
    assert clock.slept == [2.0]
    clock.t += 5
    t.wait("https://a.example/3")
    assert clock.slept == [2.0]


# -- verification, manifest, CLI ------------------------------------------


def seed_repo(repo: Path, quotes_text: str) -> None:
    (repo / "data" / "quotes.yaml").write_text(quotes_text, encoding="utf-8")


QUOTES = """\
- id: Q1
  rules: [P1]
  source: alpha
  text: 'See "the context of creating, preserving, and realizing value"'
  locator: null
  group: master_rule
- id: Q2
  rules: [P1]
  source: beta
  text: '"never appears in the page at all"'
  locator: null
  group: master_rule
- id: Q3
  rules: [P1]
  source: gamma
  text: '"anything"'
  locator: null
  group: master_rule
- id: Q4
  rules: [P1]
  source: alpha
  text: 'no quote here'
  locator: null
  group: master_rule
  placeholder: true
"""

REGISTRY = """\
- {slug: alpha, title: A, url: 'https://a.example/', kind: primary, paid: false}
- {slug: beta, title: B, url: 'https://b.example/', kind: primary, paid: false}
- {slug: gamma, title: G, url: 'https://g.example/', kind: primary, paid: false}
"""


def repo_with(repo: Path, quotes: str = QUOTES) -> Path:
    shutil.rmtree(repo / "data" / "learn", ignore_errors=True)  # live cases
    seed_repo(repo, quotes)
    (repo / "sources" / "verification.json").unlink(missing_ok=True)
    (repo / "data" / "sources.yaml").write_text(REGISTRY, encoding="utf-8")
    return repo


def run_cli(repo: Path, transport: FakeTransport, *args: str) -> int:
    clock = Clock()
    return vs.run(
        repo,
        cache_dir=repo / "build" / "cache",
        manifest=repo / "sources" / "verification.json",
        report=repo / "build" / "report.md",
        transport=transport,
        throttle=vs.Throttle(0, clock.now, clock.sleep),
        update_manifest="--update-manifest" in args,
        only={a for a in args if a.startswith(("Q", "case-"))} or None,
        sleep=clock.sleep,
        echo=lambda _s: None,
    )


PAGE = (FIXTURES / "page.html").read_text(encoding="utf-8")


def test_exit_zero_when_only_fetch_failures(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {
            "https://a.example/": [ok(PAGE)],
            "https://b.example/": [status(403)],
            "https://g.example/": [status(404)],
        }
    )
    assert run_cli(repo, t) == 0
    report = (repo / "build" / "report.md").read_text(encoding="utf-8")
    assert "failing=0 unchecked=2" in report
    assert "## blocked (1)" in report and "## gone (1)" in report


def test_exit_one_when_quote_not_found(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {
            "https://a.example/": [ok(PAGE)],
            "https://b.example/": [ok(PAGE)],
            "https://g.example/": [ok(PAGE)],
        }
    )
    assert run_cli(repo, t) == 1
    report = (repo / "build" / "report.md").read_text(encoding="utf-8")
    assert "## not-found (2)" in report and "- Q2 `beta`" in report


def test_cli_entry_and_only(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_with(repo)
    monkeypatch.setattr(vs, "UrllibTransport", lambda: FakeTransport({}))
    code = main(["--root", str(repo), "verify-sources", "--offline", "--only", "Q1"])
    assert code == 0  # not in cache offline -> unchecked, not a failure


def test_paid_source_is_unverifiable_not_failed(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(
        REGISTRY.replace("paid: false}\n- {slug: gamma", "paid: true}\n- {slug: gamma"),
        encoding="utf-8",
    )
    t = FakeTransport(
        {"https://a.example/": [ok(PAGE)], "https://b.example/": [ok("<p>summary</p>")]}
    )
    assert run_cli(repo, t, "Q1", "Q2") == 0
    assert "## paid (1)" in (repo / "build" / "report.md").read_text(encoding="utf-8")


def test_manifest_deterministic_and_merged(repo: Path) -> None:
    repo_with(repo)
    routes = {
        "https://a.example/": [ok(PAGE)],
        "https://b.example/": [status(403)],
        "https://g.example/": [status(403)],
    }
    run_cli(repo, FakeTransport(routes), "--update-manifest")
    path = repo / "sources" / "verification.json"
    first = path.read_text(encoding="utf-8")
    data = json.loads(first)
    assert [e["id"] for e in data] == ["Q1", "Q2", "Q3"]
    assert list(data[0]) == sorted(data[0])
    assert data[0]["result"] == "matched" and data[0]["score"] == 1.0
    assert data[0]["method"] == "origin" and len(data[0]["sha256"]) == 64
    assert data[1]["result"] == "blocked" and data[1]["sha256"] is None
    # Same inputs (now served from the cache) -> byte-identical file.
    run_cli(repo, FakeTransport(routes), "--update-manifest")
    assert path.read_text(encoding="utf-8") == first
    # --only merges into, not replaces, the existing manifest.
    run_cli(repo, FakeTransport(routes), "--update-manifest", "Q2")
    assert [e["id"] for e in json.loads(path.read_text(encoding="utf-8"))] == [
        "Q1",
        "Q2",
        "Q3",
    ]


CASES = """\
- id: case-demo
  title: Demo
  year: 2000
  summary: s
  rules: [P1]
  lessons: [{rule: P1, text: t}]
  quotes:
  - source: alpha
    text: the context of creating, preserving, and realizing value
  - source: beta
    text: this sentence is not in the page at all
"""


def seed_cases(repo: Path) -> None:
    cases = repo / "data" / "learn" / "cases"
    cases.mkdir(parents=True)
    (cases / "1.yaml").write_text(CASES, encoding="utf-8")


def test_case_quotes_are_collected_and_keyed(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    got = vs.case_quotes(repo)
    assert [q["id"] for q in got] == ["case-demo#1", "case-demo#2"]
    assert got[0]["source"] == "alpha" and got[0]["verbatim"]
    assert vs.case_quotes(repo / "nowhere") == []


def test_case_quote_ids_sort_numerically() -> None:
    ids = ["case-b#1", "case-a#10", "case-a#2", "Q10", "Q2"]
    assert sorted(ids, key=vs._id_key) == [
        "Q2",
        "Q10",
        "case-a#2",
        "case-a#10",
        "case-b#1",
    ]


def test_case_quotes_verified_and_recorded(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    t = FakeTransport(
        {
            "https://a.example/": [ok(PAGE)],
            "https://b.example/": [ok(PAGE)],
            "https://g.example/": [status(403)],
        }
    )
    # The unfound case quote fails the job like a rule quote.
    assert run_cli(repo, t, "--update-manifest", "case-demo#1", "case-demo#2") == 1
    data = {
        e["id"]: e
        for e in json.loads(
            (repo / "sources" / "verification.json").read_text(encoding="utf-8")
        )
    }
    assert set(data) == {"case-demo#1", "case-demo#2"}
    assert data["case-demo#1"]["result"] == "matched"
    assert data["case-demo#1"]["score"] == 1.0
    assert data["case-demo#1"]["source"] == "alpha"
    assert data["case-demo#2"]["result"] in ("near-miss", "not-found")


def test_cases_only_skips_rule_quotes(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    t = FakeTransport(
        {"https://a.example/": [ok(PAGE)], "https://b.example/": [ok(PAGE)]}
    )
    code = vs.run(
        repo,
        cache_dir=repo / "build" / "cache",
        manifest=repo / "sources" / "verification.json",
        update_manifest=True,
        cases_only=True,
        transport=t,
        throttle=vs.Throttle(0, Clock().now, Clock().sleep),
        echo=lambda _s: None,
    )
    assert code == 1
    ids = [
        e["id"]
        for e in json.loads(
            (repo / "sources" / "verification.json").read_text(encoding="utf-8")
        )
    ]
    assert ids == ["case-demo#1", "case-demo#2"]


def test_manifest_prunes_removed_case_quotes(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    path = repo / "sources" / "verification.json"
    path.write_text(
        json.dumps([{"id": "case-gone#1", "result": "matched"}]), encoding="utf-8"
    )
    t = FakeTransport({"https://a.example/": [ok(PAGE)]})
    run_cli(repo, t, "--update-manifest", "case-demo#1")
    ids = [e["id"] for e in json.loads(path.read_text(encoding="utf-8"))]
    assert ids == ["case-demo#1"]


def test_manifest_not_written_without_flag(repo: Path) -> None:
    repo_with(repo)
    run_cli(repo, FakeTransport({"https://a.example/": [ok(PAGE)]}))
    assert not (repo / "sources" / "verification.json").exists()


def test_inflate_gzip_and_deflate() -> None:
    import gzip
    import zlib

    raw = b"<p>payload</p>"
    assert vs._inflate(gzip.compress(raw), {"content-encoding": "gzip"}) == raw
    assert vs._inflate(zlib.compress(raw), {"content-encoding": "deflate"}) == raw
    assert vs._inflate(b"not gzip", {"content-encoding": "gzip"}) == b"not gzip"


def test_challenge_heuristic_is_separate_from_fetch() -> None:
    page = (
        "<html>Please verify that you're not a robot. This requires JavaScript.</html>"
    )
    resp = vs.HttpResponse(202, {"content-type": "text/html"}, page.encode(), "")
    assert vs.classify(resp)[0] == "ok"
    assert vs.looks_like_challenge(page.encode(), "text/html")
    assert not vs.looks_like_challenge(page.encode(), "application/pdf")
    assert not vs.looks_like_challenge(b"<p>plain</p>", "text/html")


def test_single_and_double_quotes_are_equivalent() -> None:
    hay = vs.normalize('Minimizing "finger-pointing" and \u201cblame\u201d here')
    assert vs.score_segment("Minimizing 'finger-pointing'", hay) == 1.0
    assert vs.score_segment("Minimizing \u2018finger-pointing\u2019", hay) == 1.0
    assert vs.score_segment("and \u2018blame\u2019 here", hay) == 1.0
    assert vs.normalize("Commander's") == vs.normalize("Commander\u2019s")


def test_footnote_markers_stripped() -> None:
    strip = vs.strip_footnote_markers
    assert strip("unified command12 establishes") == "unified command establishes"
    assert strip("objectives.3 Next") == "objectives.3 Next"  # not glued to a letter
    assert strip("done, see note7.") == "done, see note."
    assert strip("operations123") == "operations"


def test_footnote_strip_leaves_identifiers_alone() -> None:
    strip = vs.strip_footnote_markers
    for token in ("ISO 22301", "P57 applies", "B2B sales", "P68,", "ISO22301 x"):
        assert strip(token) == token


def test_pdf_footnote_marker_only_removed_for_pdf() -> None:
    pdf = make_pdf("the unified command12 establishes objectives")
    assert "command establishes" in vs.extract_text(pdf, "application/pdf")
    html = vs.extract_text(b"<p>the unified command12 establishes</p>", "text/html")
    assert "command12" in html


def test_explain_prints_window_only(repo: Path) -> None:
    repo_with(repo)
    lines: list[str] = []
    clock = Clock()
    code = vs.run(
        repo,
        cache_dir=repo / "build" / "cache",
        manifest=repo / "sources" / "verification.json",
        explain={"Q2"},
        transport=FakeTransport({"https://b.example/": [ok(PAGE)]}),
        throttle=vs.Throttle(0, clock.now, clock.sleep),
        echo=lines.append,
    )
    out = "\n".join(lines)
    assert code == 0 and "== Q2" in out and "score" in out
    assert not (repo / "sources" / "verification.json").exists()


def test_private_use_glyphs_dropped() -> None:
    hay = vs.normalize("of \uf06c Competence. \uf06c Mutual trust. \uf06c Shared")
    assert vs.score_segment("Competence. Mutual trust. Shared", hay) == 1.0
    assert vs.normalize("a\ue000b") == "ab"


def test_archive_tried_when_origin_lacks_passage(repo: Path) -> None:
    repo_with(repo)
    snap = "http://web.archive.org/web/20261010101010/https://a.example/"
    avail = json.dumps(
        {"archived_snapshots": {"closest": {"available": True, "url": snap}}}
    )
    wb = f"{vs.WAYBACK_API}?url=https%3A%2F%2Fa.example%2F&timestamp=20261014"
    raw = "https://web.archive.org/web/20261010101010id_/https://a.example/"
    t = FakeTransport(
        {
            # Origin answers 200 but is truncated; the snapshot has the text.
            "https://a.example/": [ok("<p>teaser only</p>")],
            wb: [ok(avail, "application/json")],
            raw: [ok(PAGE)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 0
    entry = json.loads((repo / "sources" / "verification.json").read_text("utf-8"))[0]
    assert (entry["result"], entry["method"]) == ("matched", "archive")
    assert "web.archive.org" in entry["final_url"]


def test_archive_missing_keeps_origin_failure(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {
            "https://b.example/": [ok(PAGE)],
            vs.WAYBACK_API: [ok("{}", "application/json")],
        }
    )
    assert run_cli(repo, t, "Q2") == 1
    report = (repo / "build" / "report.md").read_text("utf-8")
    assert "## not-found (1)" in report


def test_paid_source_missing_passage_after_archive(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(
        REGISTRY.replace("paid: false}\n- {slug: gamma", "paid: true}\n- {slug: gamma"),
        encoding="utf-8",
    )
    t = FakeTransport({"https://b.example/": [ok(PAGE)]})
    assert run_cli(repo, t, "Q2") == 0


# -- robustness -------------------------------------------------------------


class _FakeResp:
    """A urlopen() result; ``read`` serves ``body`` or raises ``error``."""

    def __init__(self, body: bytes = b"", error: Exception | None = None) -> None:
        self._body, self._error = body, error
        self.status = 200
        self.headers = email.message.Message()
        self.headers["Content-Type"] = "text/html"

    def __enter__(self) -> _FakeResp:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def geturl(self) -> str:
        return "https://x.example/"

    def read(self, n: int = -1) -> bytes:
        if self._error is not None:
            raise self._error
        out, self._body = self._body, b""
        return out


class _BrokenFp(io.BytesIO):
    def read(self, n: int | None = -1) -> bytes:
        raise http.client.IncompleteRead(b"par")


def test_truncated_reads_do_not_abort_the_run(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_with(repo)

    def fake_urlopen(req: urllib.request.Request, timeout: float) -> _FakeResp:
        url = req.full_url
        if url.startswith("https://a.example"):
            return _FakeResp(error=http.client.IncompleteRead(b"par"))
        if url.startswith("https://b.example"):
            raise urllib.error.HTTPError(
                url, 403, "Forbidden", email.message.Message(), _BrokenFp()
            )
        if url.startswith("https://g.example"):
            return _FakeResp(PAGE.encode())
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    clock = Clock()
    code = vs.run(
        repo,
        cache_dir=repo / "build" / "cache",
        manifest=repo / "sources" / "verification.json",
        report=repo / "build" / "report.md",
        update_manifest=True,
        transport=vs.UrllibTransport(),
        throttle=vs.Throttle(0, clock.now, clock.sleep),
        sleep=clock.sleep,
        echo=lambda _s: None,
    )
    data = json.loads((repo / "sources" / "verification.json").read_text("utf-8"))
    by_id = {e["id"]: e["result"] for e in data}
    assert by_id == {"Q1": "timeout", "Q2": "blocked", "Q3": "not-found"}
    assert (repo / "build" / "report.md").is_file() and code == 1


def test_inflate_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vs, "MAX_BYTES", 100)
    bomb = gzip.compress(b"a" * 10_000)
    with pytest.raises(vs.ResponseTooLarge):
        vs._inflate(bomb, {"content-encoding": "gzip"})
    small = gzip.compress(b"a" * 50)
    assert vs._inflate(small, {"content-encoding": "gzip"}) == b"a" * 50


def test_oversized_body_is_unreadable_and_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(vs, "MAX_BYTES", 100)
    bomb = gzip.compress(b"a" * 10_000)
    calls: list[str] = []

    def fake_urlopen(req: urllib.request.Request, timeout: float) -> _FakeResp:
        calls.append(req.full_url)
        resp = _FakeResp(bomb)
        resp.headers["Content-Encoding"] = "gzip"
        return resp

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    clock = Clock()
    f = vs.Fetcher(
        vs.UrllibTransport(),
        vs.Cache(tmp_path),
        vs.Throttle(0, clock.now, clock.sleep),
        sleep=clock.sleep,
    )
    got = f.get("https://o.example/big", "origin")
    assert got.status == "unreadable" and "exceeds" in got.detail
    assert calls == ["https://o.example/big"]


def test_captcha_word_on_a_matching_page_is_not_blocked(repo: Path) -> None:
    repo_with(repo)
    page = PAGE + "<p>We use a CAPTCHA to protect forms.</p>"
    assert run_cli(repo, FakeTransport({"https://a.example/": [ok(page)]}), "Q1") == 0
    report = (repo / "build" / "report.md").read_text("utf-8")
    assert "failing=0 unchecked=0" in report


def test_challenge_page_without_the_passage_is_blocked(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {"https://b.example/": [ok("<html>Please solve the CAPTCHA</html>")]}
    )
    assert run_cli(repo, t, "Q2") == 0
    report = (repo / "build" / "report.md").read_text("utf-8")
    assert "## blocked (1)" in report and "challenge page" in report


def test_via_equal_to_origin_is_fetched_once_with_right_method(
    tmp_path: Path,
) -> None:
    url = "https://o.example/doc"
    f, transport, _ = fetcher(tmp_path, {url: [status(503)]})
    got = f.fetch_source(src(url, via={"title": "V", "url": url}))
    assert got.status == "timeout"
    assert [u for u, _ in transport.calls].count(url) == 3  # one fetch, 2 retries
    f2, _, _ = fetcher(tmp_path / "ok", {url: [ok("<p>x</p>")]})
    assert f2.fetch_source(src(url, via={"title": "V", "url": url})).method == "origin"


def test_method_is_per_caller_not_per_first_fetch(tmp_path: Path) -> None:
    url = "https://o.example/doc"
    f, transport, _ = fetcher(tmp_path, {url: [ok("<p>x</p>")]})
    assert f.get(url, "origin").method == "origin"
    assert f.get(url, "via").method == "via"
    assert len(transport.calls) == 1


def test_manifest_prunes_stale_entries(repo: Path) -> None:
    repo_with(repo)
    path = repo / "sources" / "verification.json"
    path.parent.mkdir(exist_ok=True)
    stale = [
        {"id": "Q99", "result": "matched"},  # no such quote
        {"id": "Q4", "result": "matched"},  # now a placeholder
        {"id": "Q3", "result": "matched"},  # still valid, not re-run
    ]
    path.write_text(json.dumps(stale), encoding="utf-8")
    run_cli(
        repo,
        FakeTransport({"https://a.example/": [ok(PAGE)]}),
        "--update-manifest",
        "Q1",
    )
    ids = [e["id"] for e in json.loads(path.read_text("utf-8"))]
    assert ids == ["Q1", "Q3"]
    assert vs.render_manifest([], stale, {"Q3"}).count('"id"') == 1


def test_inflate_truncated_stream_raises() -> None:
    import gzip

    data = gzip.compress(b"x" * 5000)
    with pytest.raises(EOFError):
        vs._inflate(data[: len(data) // 2], {"content-encoding": "gzip"})


# -- alternatives on a content miss ---------------------------------------

VIA_REGISTRY = REGISTRY.replace(
    "kind: primary, paid: false}\n- {slug: beta",
    "kind: primary, paid: false, via: {title: V, url: 'https://v.example/'}}\n"
    "- {slug: beta",
    1,
)
WB_A = f"{vs.WAYBACK_API}?url=https%3A%2F%2Fa.example%2F&timestamp=20261014"
RAW_A = "https://web.archive.org/web/20261010101010id_/https://a.example/"
AVAIL_A = json.dumps(
    {
        "archived_snapshots": {
            "closest": {
                "available": True,
                "url": "http://web.archive.org/web/20261010101010/https://a.example/",
            }
        }
    }
)


def manifest_of(repo: Path) -> dict[str, dict[str, object]]:
    data = json.loads((repo / "sources" / "verification.json").read_text("utf-8"))
    return {e["id"]: e for e in data}


def test_via_tried_before_archive_on_content_miss(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    t = FakeTransport(
        {
            "https://a.example/": [ok("<p>teaser only</p>")],
            "https://v.example/": [ok(PAGE)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 0
    entry = manifest_of(repo)["Q1"]
    assert (entry["result"], entry["method"]) == ("matched", "via")
    assert not any("archive.org" in u for u, _ in t.calls)


def test_archive_after_via_when_via_also_misses(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    t = FakeTransport(
        {
            "https://a.example/": [ok("<p>teaser only</p>")],
            "https://v.example/": [ok("<p>another teaser</p>")],
            WB_A: [ok(AVAIL_A, "application/json")],
            RAW_A: [ok(PAGE)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 0
    assert manifest_of(repo)["Q1"]["method"] == "archive"
    urls = [u for u, _ in t.calls]
    assert urls.index("https://v.example/") < urls.index(WB_A)


def test_via_equal_to_fetched_url_is_not_refetched_on_miss(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(
        VIA_REGISTRY.replace("https://v.example/", "https://a.example/"),
        encoding="utf-8",
    )
    t = FakeTransport({"https://a.example/": [ok("<p>teaser only</p>")]})
    assert run_cli(repo, t, "Q1") == 1
    assert [u for u, _ in t.calls].count("https://a.example/") == 1


# -- challenge pages --------------------------------------------------------


def test_unextractable_challenge_page_is_blocked_not_unreadable(repo: Path) -> None:
    repo_with(repo)
    # Served as HTML, looks like a PDF, so no text can be extracted.
    body = b"%PDF-1.4 <html>Please solve the CAPTCHA</html>"
    t = FakeTransport({"https://b.example/": [ok(body, "text/html")]})
    assert run_cli(repo, t, "--update-manifest", "Q2") == 0
    assert manifest_of(repo)["Q2"]["result"] == "blocked"


def test_unextractable_non_challenge_stays_unreadable(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {"https://b.example/": [ok(b"%PDF-1.4 garbage", "application/pdf")]}
    )
    assert run_cli(repo, t, "--update-manifest", "Q2") == 0
    assert manifest_of(repo)["Q2"]["result"] == "unreadable"


def test_blocked_result_records_no_fetch_data(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {
            "https://b.example/": [ok("<html>Please solve the CAPTCHA</html>")],
            "https://a.example/": [ok(PAGE)],
        }
    )
    run_cli(repo, t, "--update-manifest", "Q1", "Q2")
    entries = manifest_of(repo)
    challenge = entries["Q2"]
    assert challenge["result"] == "blocked"
    for key in ("method", "final_url", "fetched_at", "sha256"):
        assert challenge[key] is None, key
    assert entries["Q1"]["sha256"] is not None  # a real match keeps its hash


# -- verdict attribution ----------------------------------------------------

EXTRA_QUOTE = """\
- id: Q1
  rules: [P1]
  source: alpha
  extra_sources: [gamma]
  text: 'See "the context of creating, preserving, and realizing value"'
  locator: null
  group: master_rule
"""
EVIDENCE = ("method", "final_url", "fetched_at", "sha256")


def test_challenge_origin_with_clean_partial_alternative_stays_blocked(
    repo: Path,
) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    partial = "<p>the context of creating, preserving and realising values</p>"
    t = FakeTransport(
        {
            "https://a.example/": [ok("<html>Please solve the CAPTCHA</html>")],
            "https://v.example/": [ok(partial)],
        }
    )
    run_cli(repo, t, "--update-manifest", "Q1")
    entry = manifest_of(repo)["Q1"]
    assert entry["result"] == "blocked"
    assert all(entry[k] is None for k in EVIDENCE)


def test_challenge_origin_with_full_alternative_is_matched(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    t = FakeTransport(
        {
            "https://a.example/": [ok("<html>Please solve the CAPTCHA</html>")],
            "https://v.example/": [ok(PAGE)],
        }
    )
    run_cli(repo, t, "--update-manifest", "Q1")
    entry = manifest_of(repo)["Q1"]
    assert (entry["result"], entry["method"]) == ("matched", "via")


def test_unreadable_primary_is_not_rescued_by_extra_sources(repo: Path) -> None:
    repo_with(repo, EXTRA_QUOTE)
    garbage = b"%PDF-1.4 garbage"
    t = FakeTransport(
        {
            "https://a.example/": [ok(garbage, "application/pdf")],
            "https://g.example/": [ok(PAGE)],
        }
    )
    run_cli(repo, t, "--update-manifest", "Q1")
    entry = manifest_of(repo)["Q1"]
    assert entry["result"] == "unreadable"
    # The verdict came from the primary fetch, so its evidence is kept.
    assert entry["method"] == "origin"
    assert entry["final_url"] == "https://a.example/"
    assert entry["sha256"] == hashlib.sha256(garbage).hexdigest()
    assert not any(u.startswith("https://g.example") for u, _ in t.calls)


def test_unreadable_primary_matched_in_full_by_archive(repo: Path) -> None:
    repo_with(repo)
    t = FakeTransport(
        {
            "https://a.example/": [ok(b"%PDF-1.4 garbage", "application/pdf")],
            WB_A: [ok(AVAIL_A, "application/json")],
            RAW_A: [ok(PAGE)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 0
    entry = manifest_of(repo)["Q1"]
    assert (entry["result"], entry["method"]) == ("matched", "archive")
    assert "web.archive.org" in str(entry["final_url"])
    assert entry["sha256"] == hashlib.sha256(PAGE.encode()).hexdigest()


def test_unreadable_primary_with_partial_alternative_stays_unreadable(
    repo: Path,
) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    garbage = b"%PDF-1.4 garbage"
    partial = "<p>the context of creating, preserving and realising values</p>"
    t = FakeTransport(
        {
            "https://a.example/": [ok(garbage, "application/pdf")],
            "https://v.example/": [ok(partial)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 0
    entry = manifest_of(repo)["Q1"]
    assert entry["result"] == "unreadable"
    assert entry["method"] == "origin"
    assert entry["sha256"] == hashlib.sha256(garbage).hexdigest()


def test_extra_sources_do_not_help_an_alternative_of_an_unreadable_primary(
    repo: Path,
) -> None:
    repo_with(repo, EXTRA_QUOTE)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    t = FakeTransport(
        {
            "https://a.example/": [ok(b"%PDF-1.4 garbage", "application/pdf")],
            "https://v.example/": [ok("<p>teaser only</p>")],
            "https://g.example/": [ok(PAGE)],
        }
    )
    run_cli(repo, t, "--update-manifest", "Q1")
    assert manifest_of(repo)["Q1"]["result"] == "unreadable"
    assert not any(u.startswith("https://g.example") for u, _ in t.calls)


def test_failing_alternative_leaves_primary_evidence(repo: Path) -> None:
    repo_with(repo)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    origin_body = "<p>teaser only</p>"
    t = FakeTransport(
        {
            "https://a.example/": [ok(origin_body)],
            "https://v.example/": [ok("<p>the context of creating, preserving</p>")],
            WB_A: [ok(AVAIL_A, "application/json")],
            RAW_A: [ok("<p>another teaser</p>")],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 1
    entry = manifest_of(repo)["Q1"]
    assert entry["result"] == "not-found"
    assert entry["method"] == "origin"
    assert entry["final_url"] == "https://a.example/"
    assert entry["sha256"] == hashlib.sha256(origin_body.encode()).hexdigest()


def test_pending_extra_sources_skip_the_fallbacks(repo: Path) -> None:
    repo_with(repo, EXTRA_QUOTE)
    (repo / "data" / "sources.yaml").write_text(VIA_REGISTRY, encoding="utf-8")
    t = FakeTransport(
        {
            "https://a.example/": [ok("<p>teaser only</p>")],
            "https://g.example/": [status(403)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "Q1") == 0
    entry = manifest_of(repo)["Q1"]
    assert entry["result"] == "blocked"
    assert all(entry[k] is None for k in EVIDENCE)
    assert not any(
        u.startswith(("https://v.example", "https://web.archive.org"))
        or "archive.org" in u
        for u, _ in t.calls
        if "g.example" not in u
    )


def test_forget_fetch_clears_from_cache() -> None:
    res = vs.QuoteResult(
        "Q1", "s", "u", "blocked", method="origin", sha256="x", from_cache=True
    )
    vs._forget_fetch(res)
    assert not res.from_cache and res.sha256 is None and res.method is None


# -- hardening (issues #25, #34, #19) ---------------------------------------


def test_segment_without_scorable_part_never_scores_one() -> None:
    hay = vs.normalize("ab cd and much more text")
    assert vs.split_ellipsis("ab … cd") == []
    assert vs.score_segment("ab … cd", hay) == 0.0
    assert vs.score_segment("ab", hay) == 0.0


def test_out_of_order_parts_stay_below_one(monkeypatch: pytest.MonkeyPatch) -> None:
    hay = vs.normalize("alpha beta gamma delta epsilon zeta")
    assert vs.score_segment("epsilon zeta ... alpha beta", hay) < 1.0
    # Even if every part matched perfectly on its own, out of order is not a match.
    monkeypatch.setattr(vs, "best_ratio", lambda needle, haystack: 1.0)
    score = vs.score_segment("epsilon zeta ... alpha beta", hay)
    assert score == vs.PARTIAL_MAX < 1.0


def test_too_short_passage_is_no_quote_not_matched(repo: Path) -> None:
    quotes = QUOTES.replace(
        "'\"never appears in the page at all\"'", '\'"good words here" "ab … cd"\''
    )
    repo_with(repo, quotes)
    t = FakeTransport({"https://b.example/": [ok(PAGE)]})
    assert run_cli(repo, t, "--update-manifest", "Q2") == 0
    entry = manifest_of(repo)["Q2"]
    assert entry["result"] == "no-quote"
    report = (repo / "build" / "report.md").read_text("utf-8")
    assert "passage too short to verify" in report
    assert not t.calls  # nothing fetched for an unverifiable quote


def test_verbatim_no_quote_detail_is_not_about_double_quotes(repo: Path) -> None:
    repo_with(repo)
    res = vs.Verifier(
        fetcher(repo, {})[0], {"alpha": src("https://a.example/")}
    ).verify({"id": "c#1", "source": "alpha", "text": "!!", "verbatim": True})
    assert res.result == "no-quote"
    assert "double-quoted" not in res.detail and "too short" in res.detail


def test_case_quote_missing_source_or_text_names_case_and_index(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    path = repo / "data" / "learn" / "cases" / "1.yaml"
    no_text = CASES.replace("    text: this sentence", "    txt: this sentence")
    path.write_text(no_text, encoding="utf-8")
    with pytest.raises(ValueError, match=r"case case-demo: quote 2 has no `text`"):
        vs.case_quotes(repo)
    no_source = CASES.replace("  - source: alpha\n", "  - sourc: alpha\n")
    path.write_text(no_source, encoding="utf-8")
    with pytest.raises(ValueError, match=r"case case-demo: quote 1 has no `source`"):
        vs.case_quotes(repo)


def test_unknown_slug_is_a_clear_error(repo: Path) -> None:
    repo_with(repo)
    verifier = vs.Verifier(fetcher(repo, {})[0], {})
    quote = {"id": "Q9", "source": "nope", "text": '"some long enough text"'}
    with pytest.raises(vs.UnknownSourceError, match="Q9.*'nope'"):
        verifier.verify(quote)
    with pytest.raises(vs.UnknownSourceError, match="Q9.*'nope'"):
        verifier.explain(quote)
    f, _, _ = fetcher(repo, {"https://a.example/": [ok(PAGE)]})
    verifier = vs.Verifier(f, {"alpha": src("https://a.example/")})
    extra = {**quote, "source": "alpha", "extra_sources": ["ghost"]}
    with pytest.raises(vs.UnknownSourceError, match="'ghost'"):
        verifier.verify(extra)


def _run_ids(repo: Path, **kwargs: object) -> tuple[int, list[str], list[str]]:
    out: list[str] = []
    err: list[str] = []
    code = vs.run(
        repo,
        cache_dir=repo / "build" / "cache",
        manifest=repo / "sources" / "verification.json",
        transport=FakeTransport({"https://a.example/": [ok(PAGE)]}),
        throttle=vs.Throttle(0, Clock().now, Clock().sleep),
        echo=out.append,
        echo_err=err.append,
        **kwargs,  # type: ignore[arg-type]
    )
    return code, out, err


def test_unknown_ids_exit_two_and_are_named(repo: Path) -> None:
    repo_with(repo)
    code, out, err = _run_ids(repo, only={"Q1", "Q99"})
    assert code == 2 and not out and "--only" in err[0] and "Q99" in err[0]
    assert "Q1," not in err[0]
    # Q4 is a placeholder: not verifiable, so named too.
    code, out, err = _run_ids(repo, explain={"Q98", "Q4"})
    assert code == 2 and not out and "--explain" in err[0]
    assert "Q4" in err[0] and "Q98" in err[0]


def test_cli_unknown_only_exits_two(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo_with(repo)
    monkeypatch.setattr(vs, "UrllibTransport", lambda: FakeTransport({}))
    code = main(["--root", str(repo), "verify-sources", "--offline", "--only", "Q77"])
    assert code == 2
    assert "Q77" in capsys.readouterr().err
    code = main(["--root", str(repo), "verify-sources", "--explain", "Q77,Q1"])
    assert code == 2


def test_explain_honours_cases_only(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    code, out, err = _run_ids(repo, explain={"Q1"}, cases_only=True)
    assert code == 2 and "Q1" in err[0] and not out
    code, out, _ = _run_ids(repo, explain={"case-demo#1"}, cases_only=True)
    assert code == 0 and out[0] == "== case-demo#1"
    assert not any(line.startswith("== Q") for line in out)


def test_manifest_stores_quote_hash_and_check_date(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    t = FakeTransport(
        {"https://a.example/": [ok(PAGE)], "https://b.example/": [ok(PAGE)]}
    )
    run_cli(repo, t, "--update-manifest", "Q1", "case-demo#1")
    data = manifest_of(repo)
    assert data["Q1"]["quote_sha256"] == vs.quote_hash(
        'See "the context of creating, preserving, and realizing value"'
    )
    assert data["Q1"]["checked"] == data["Q1"]["fetched_at"]
    assert data["case-demo#1"]["checked"] == data["case-demo#1"]["fetched_at"]
    assert len(str(data["case-demo#1"]["quote_sha256"])) == 64


def test_checked_is_the_run_date_not_a_constant(repo: Path) -> None:
    repo_with(repo)
    quote = {"id": "Q40", "source": "alpha", "text": '"the context of creating"'}
    registry = {"alpha": src("https://a.example/")}
    fetched, _, _ = fetcher(
        repo,
        {"https://a.example/": [ok(PAGE)]},
        now=lambda: datetime(2026, 11, 3, 23, 59, tzinfo=UTC),
    )
    run_clock = lambda: datetime(2026, 11, 4, 1, 0, tzinfo=UTC)  # noqa: E731
    res = vs.Verifier(fetched, registry, now=run_clock).verify(quote)
    assert res.fetched_at == "2026-11-03"
    assert vs.manifest_entry(res)["checked"] == "2026-11-03"
    # No fetch date (offline, nothing cached): the run clock's UTC date.
    (repo / "empty").mkdir()
    offline, _, _ = fetcher(repo / "empty", {}, offline=True)
    res = vs.Verifier(offline, registry, now=run_clock).verify(quote)
    assert res.fetched_at is None
    assert vs.manifest_entry(res)["checked"] == "2026-11-04"
    # The archive lookup constants do not leak into the manifest.
    assert vs.manifest_entry(res)["checked"] not in {"2026-10-14", "2026-10-27"}


def test_manifest_drift_stale_and_orphaned() -> None:
    quotes: list[dict[str, object]] = [
        {"id": "Q1", "text": '"alpha beta"'},
        {"id": "case-x#1", "text": "gamma delta", "verbatim": True},
        {"id": "Q3", "text": '"unchanged text"'},
    ]
    entries: list[dict[str, object]] = [
        {"id": "Q1", "quote_sha256": vs.quote_hash('"alpha beta gamma"')},
        {"id": "case-x#1", "quote_sha256": vs.quote_hash("GAMMA  delta")},
        {"id": "Q3"},  # no hash: legacy entry, re-verify
        {"id": "Q7", "quote_sha256": vs.quote_hash("gone")},
        {"id": "case-y#2", "quote_sha256": vs.quote_hash("gone")},
    ]
    drift = vs.manifest_drift(entries, quotes)
    assert drift.stale == ["Q1", "Q3"]
    assert drift.orphaned == ["Q7", "case-y#2"]


def test_run_reports_stale_and_orphaned_entries(repo: Path) -> None:
    repo_with(repo)
    path = repo / "sources" / "verification.json"
    path.write_text(
        json.dumps(
            [
                {"id": "Q1", "quote_sha256": "0" * 64},
                {
                    "id": "Q2",
                    "quote_sha256": vs.quote_hash('"never appears in the page at all"'),
                },
                {"id": "Q42", "quote_sha256": "0" * 64},
            ]
        ),
        encoding="utf-8",
    )
    code, out, _ = _run_ids(repo, only={"Q3"})
    text = "\n".join(out)
    assert "stale manifest entries (re-verify needed): Q1" in text
    assert "Q2" not in text.split("orphaned")[0]
    assert "orphaned manifest entries: Q42" in text
    # Re-verifying a stale quote with --update-manifest clears it.
    code, out, _ = _run_ids(repo, only={"Q1"}, update_manifest=True)
    assert not any("stale" in line for line in out)


def test_case_quotes_use_their_own_archive_timestamp(repo: Path) -> None:
    repo_with(repo)
    seed_cases(repo)
    snap = "http://web.archive.org/web/20261010101010/https://a.example/"
    avail = json.dumps(
        {"archived_snapshots": {"closest": {"available": True, "url": snap}}}
    )
    raw = "https://web.archive.org/web/20261010101010id_/https://a.example/"
    wb = f"{vs.WAYBACK_API}?url=https%3A%2F%2Fa.example%2F&timestamp=20261027"
    t = FakeTransport(
        {
            "https://a.example/": [ok("<p>teaser only</p>")],
            wb: [ok(avail, "application/json")],
            raw: [ok(PAGE)],
        }
    )
    assert run_cli(repo, t, "--update-manifest", "case-demo#1") == 0
    entry = manifest_of(repo)["case-demo#1"]
    assert (entry["result"], entry["method"]) == ("matched", "archive")
    assert any("timestamp=20261027" in u for u, _ in t.calls)


def test_real_case_quotes_resolve_to_registered_sources() -> None:
    root = Path(__file__).resolve().parent.parent
    registry = load_registry(root)
    quotes = vs.case_quotes(root)
    assert quotes, "the real data/learn/cases/ must carry quotes"
    unknown = [q["id"] for q in quotes if q["source"] not in registry]
    assert not unknown, f"case quotes with unregistered sources: {unknown}"


def test_source_copy_order_lives_in_one_place(tmp_path: Path) -> None:
    f, _, _ = fetcher(tmp_path, {})
    plain = src("https://o.example/")
    assert f.copies(plain) == [
        ("origin", "https://o.example/"),
        ("archive", "https://o.example/"),
    ]
    via = src("https://o.example/", via={"title": "V", "url": "https://v.example/"})
    assert [m for m, _ in f.copies(via)] == ["origin", "via", "archive"]
    same = src("https://o.example/", via={"title": "V", "url": "https://o.example/"})
    assert [m for m, _ in f.copies(same)] == ["origin", "archive"]


def test_alternatives_are_the_copies_after_the_primary(tmp_path: Path) -> None:
    snap = "http://web.archive.org/web/20261010101010/https://o.example/"
    avail = json.dumps(
        {"archived_snapshots": {"closest": {"available": True, "url": snap}}}
    )
    wb = f"{vs.WAYBACK_API}?url=https%3A%2F%2Fo.example%2F&timestamp=20261014"
    raw = "https://web.archive.org/web/20261010101010id_/https://o.example/"
    routes = {
        "https://o.example/": [ok("<p>o</p>")],
        "https://v.example/": [ok("<p>v</p>")],
        wb: [ok(avail, "application/json")],
        raw: [ok("<p>a</p>")],
    }
    f, _, _ = fetcher(tmp_path, routes)
    s = src("https://o.example/", via={"title": "V", "url": "https://v.example/"})
    primary = f.fetch_source(s)
    assert primary.method == "origin"
    assert [a.method for a in f.alternatives(s, primary)] == ["via", "archive"]
    via_primary = f.get("https://v.example/", "via")
    assert [a.method for a in f.alternatives(s, via_primary)] == ["archive"]
    arch = f.archive("https://o.example/")
    assert list(f.alternatives(s, arch)) == []
