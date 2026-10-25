"""Offline tests for ``taxonomy verify-sources`` (fake transport, fake clock)."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from taxonomy import verify_sources as vs
from taxonomy.cli import main
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
    f3, _, _ = fetcher(
        tmp_path / "y",
        {"https://o.example/c": [ok("<html>Please solve the CAPTCHA</html>")]},
    )
    assert f3.fetch_source(src("https://o.example/c")).status == "blocked"


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
  rules: [U1]
  source: alpha
  text: 'See "the context of creating, preserving, and realizing value"'
  locator: null
  group: master_rule
- id: Q2
  rules: [U1]
  source: beta
  text: '"never appears in the page at all"'
  locator: null
  group: master_rule
- id: Q3
  rules: [U1]
  source: gamma
  text: '"anything"'
  locator: null
  group: master_rule
- id: Q4
  rules: [U1]
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
        only={a for a in args if a.startswith("Q")} or None,
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


def test_javascript_challenge_is_blocked() -> None:
    page = (
        "<html>Please verify that you're not a robot. This requires JavaScript.</html>"
    )
    assert (
        vs.classify(
            vs.HttpResponse(202, {"content-type": "text/html"}, page.encode(), "")
        )[0]
        == "blocked"
    )


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
    for token in ("ISO 22301", "U17 applies", "B2B sales", "R4,", "ISO22301 x"):
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
