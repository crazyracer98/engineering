"""Check that each quote in ``data/quotes.yaml`` appears in its fetched source.

``run`` backs ``taxonomy verify-sources``. Per source it tries the cache, the
origin URL, ``via.url`` and finally the Internet Archive snapshot closest to
:data:`CHECKED_TIMESTAMP`, extracts the text (HTML, PDF or plain), normalizes
both sides and tests containment. Fetched text lives only in the git-ignored
cache; the committed manifest records hashes and results, never text.
"""

from __future__ import annotations

import hashlib
import http.client
import io
import json
import logging
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Protocol, cast

from pypdf import PdfReader

from taxonomy.load import load_registry, load_yaml
from taxonomy.model import Source

logging.getLogger("pypdf").setLevel(logging.ERROR)  # font warnings drown the report

USER_AGENT = (
    "engineering-taxonomy-verifier/1.0 (+https://github.com/crazyracer98/engineering)"
)
#: The date the quotes were checked; the archive snapshot nearest to it is used.
CHECKED_TIMESTAMP = "20261014"
WAYBACK_API = "https://archive.org/wayback/available"
ACCEPT = "text/html,application/xhtml+xml,application/pdf,text/plain;q=0.9,*/*;q=0.5"
MIN_HOST_INTERVAL = 2.0
TIMEOUT = 15.0
#: Wall-clock limit for one download (a socket timeout alone lets a trickle run on).
DEADLINE = 60.0
MAX_RETRIES = 2
MAX_BYTES = 40 * 1024 * 1024
FRESH_SECONDS = 24 * 3600
NEAR_MISS_MIN = 0.8
#: Bump when normalization or extraction changes: invalidates cached ``.text``.
TEXT_VERSION = "v3"
EXPLAIN_CHARS = 400
MIN_SEGMENT_CHARS = 4

#: Results that fail the job: the source was read and lacks the quote.
FAILING = ("not-found", "near-miss")
#: Results that only get reported: the quote could not be checked.
UNCHECKED = ("blocked", "gone", "timeout", "paid", "unreadable")
RESULT_ORDER = ("matched", *FAILING, *UNCHECKED, "no-quote")

BLOCK_MARKERS = (
    "captcha",
    "cf-challenge",
    "just a moment...",
    "access denied",
    "verify you are human",
    "are you a robot",
    "not a robot",
    "this requires javascript",
)
BLOCK_TAGS = frozenset(
    "address article aside blockquote br dd div dl dt figcaption figure footer "
    "h1 h2 h3 h4 h5 h6 header hr li main nav ol p pre section table td th tr ul".split()
)


# --------------------------------------------------------------------------
# Normalization and matching
# --------------------------------------------------------------------------

_QUOTE_MAP = str.maketrans(
    {
        "'": '"',
        "‘": '"',
        "’": '"',
        "‚": '"',
        "‛": '"',
        "′": '"',
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "″": '"',
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
        "―": "-",
        "−": "-",
    }
)
#: Private-use code points are font glyphs (Wingdings bullets), not text.
_PRIVATE_USE = re.compile("[\ue000-\uf8ff]")
_HYPHEN_BREAK = re.compile(r"(\w)-[ \t]*\r?\n\s*(\w)")
_DASHES = re.compile(r"-{2,}")
_SPACE = re.compile(r"\s+")
_ELLIPSIS = re.compile(r"\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…)\s*")
_QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')


def normalize(text: str) -> str:
    """Fold typography so a quote and its source compare equal.

    NFKC, soft hyphens and private-use glyphs dropped, hyphenated line breaks
    joined, lowercase,
    dashes to ASCII, every kind of quote mark (single or double, straight or
    curly) to ``"`` so that nested-quote and apostrophe variants compare
    equal, whitespace collapsed.
    """
    text = unicodedata.normalize("NFKC", text).replace("­", "")
    text = _PRIVATE_USE.sub("", text)
    text = _HYPHEN_BREAK.sub(r"\1\2", text).lower().translate(_QUOTE_MAP)
    text = _DASHES.sub("-", text)
    return _SPACE.sub(" ", text).strip()


def _relaxed(text: str) -> str:
    """A normalized text without hyphens and spaces (spacing around dashes)."""
    return text.replace("-", "").replace(" ", "")


def quoted_segments(text: str) -> list[str]:
    """The double-quoted passages of a quote cell, in order."""
    out: list[str] = []
    for m in _QUOTED.finditer(text):
        seg = (m.group(1) or m.group(2) or "").strip()
        if sum(c.isalnum() for c in seg) >= MIN_SEGMENT_CHARS:
            out.append(seg)
    return out


def split_ellipsis(segment: str) -> list[str]:
    """Parts of a segment around ``...``, ``…`` and ``[...]``, edges trimmed."""
    parts: list[str] = []
    for raw in _ELLIPSIS.split(segment):
        part = re.sub(r"^\W+|\W+$", "", normalize(raw))
        if sum(c.isalnum() for c in part) >= MIN_SEGMENT_CHARS:
            parts.append(part)
    return parts


def find_parts(parts: Sequence[str], haystack: str) -> bool:
    """Whether every part occurs in ``haystack`` (normalized), in order."""
    for variant, relax in ((haystack, False), (_relaxed(haystack), True)):
        pos = 0
        for part in parts:
            needle = _relaxed(part) if relax else part
            idx = variant.find(needle, pos)
            if idx < 0:
                break
            pos = idx + len(needle)
        else:
            return True
    return False


def best_window(needle: str, haystack: str) -> tuple[float, int]:
    """Best ``SequenceMatcher`` ratio of ``needle`` over windows of ``haystack``.

    Returns ``(ratio, window start)``. Only windows around occurrences of the
    needle's longest words are scored, so a megabyte page costs a few hundred
    comparisons, not tens of thousands. ``(0.0, -1)`` when no anchor occurs.
    """
    n = len(needle)
    if not n or not haystack:
        return 0.0, -1
    words = sorted(set(re.findall(r"\w{5,}", needle)), key=len, reverse=True)[:6]
    starts: set[int] = set()
    for word in words:
        offset = needle.find(word)
        pos = haystack.find(word)
        hits = 0
        while pos >= 0 and hits < 60:
            starts.add(max(0, pos - offset - n // 10) // max(1, n // 8))
            pos = haystack.find(word, pos + 1)
            hits += 1
    matcher = SequenceMatcher(None, autojunk=False)
    matcher.set_seq2(needle)
    width = n + n // 4
    best, best_start = 0.0, -1
    for bucket in sorted(starts)[:400]:
        start = bucket * max(1, n // 8)
        matcher.set_seq1(haystack[start : start + width])
        if matcher.real_quick_ratio() <= best or matcher.quick_ratio() <= best:
            continue
        ratio = matcher.ratio()
        if ratio > best:
            best, best_start = ratio, start
        if best >= 0.999:
            break
    return best, best_start


def best_ratio(needle: str, haystack: str) -> float:
    """The ratio of :func:`best_window`."""
    return best_window(needle, haystack)[0]


def score_segment(segment: str, haystack: str) -> float:
    """1.0 when the segment (all its ellipsis parts, in order) is contained."""
    parts = split_ellipsis(segment)
    if not parts:
        return 1.0
    if find_parts(parts, haystack):
        return 1.0
    return min(best_ratio(p, haystack) for p in parts)


# --------------------------------------------------------------------------
# Text extraction
# --------------------------------------------------------------------------


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in BLOCK_TAGS:
            self.chunks.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag in BLOCK_TAGS:
            self.chunks.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.chunks.append(data)


def decode(body: bytes, content_type: str) -> str:
    """Decode bytes using the declared charset, else UTF-8, never raising."""
    m = re.search(r"charset=([\w-]+)", content_type, re.I)
    for enc in ((m.group(1),) if m else ()) + ("utf-8",):
        try:
            return body.decode(enc)
        except UnicodeDecodeError, LookupError:
            continue
    return body.decode("utf-8", errors="replace")


def extract_html(markup: str) -> str:
    parser = _TextExtractor()
    parser.feed(markup)
    parser.close()
    return "".join(parser.chunks)


#: A footnote marker glued to a word: 3+ lowercase letters, then 1-3 digits,
#: then whitespace, punctuation or the end. "U17", "B2B", "ISO 22301" stay.
_FOOTNOTE = re.compile(r"(?<=[a-z]{3})\d{1,3}(?=[\s.,;:!?)\]]|$)")


def strip_footnote_markers(text: str) -> str:
    """Drop footnote markers such as ``command12`` -> ``command`` (PDF text only)."""
    return _FOOTNOTE.sub("", text)


def extract_pdf(body: bytes) -> str:
    reader = PdfReader(io.BytesIO(body))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return strip_footnote_markers(text)


def extract_text(body: bytes, content_type: str, url: str = "") -> str:
    """Plain text of an HTML page, a PDF, or any other (text) payload.

    Raises ``ValueError`` when a PDF cannot be parsed.
    """
    ctype = content_type.lower()
    if (
        body[:5] == b"%PDF-"
        or "pdf" in ctype
        or urllib.parse.urlparse(url).path.lower().endswith(".pdf")
    ):
        try:
            return extract_pdf(body)
        except Exception as exc:
            raise ValueError(f"unreadable PDF: {type(exc).__name__}: {exc}") from exc
    text = decode(body, content_type)
    if (
        "html" in ctype
        or "xml" in ctype
        or re.search(r"<(?:html|body|p|div)\b", text[:4096], re.I)
    ):
        return extract_html(text)
    return text


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class HttpResponse:
    """A response; ``status`` 0 means the request itself failed (see ``error``)."""

    status: int
    headers: Mapping[str, str]
    body: bytes
    final_url: str
    error: str = ""


class Transport(Protocol):
    def request(
        self, url: str, headers: Mapping[str, str], timeout: float
    ) -> HttpResponse: ...


class ResponseTooLarge(Exception):
    """A (decompressed) body exceeds ``MAX_BYTES``."""


#: Prefix of ``HttpResponse.error`` for a body that cannot be used (no retry).
UNREADABLE = "unreadable: "

#: What a truncated, reset or stalled body read can raise.
READ_ERRORS = (http.client.HTTPException, OSError, EOFError, ValueError)


def _read_limited(resp: Any) -> bytes:
    """Read a body up to ``MAX_BYTES``; ``TimeoutError`` after ``DEADLINE`` seconds."""
    end = time.monotonic() + DEADLINE
    chunks: list[bytes] = []
    size = 0
    while chunk := resp.read(65536):
        chunks.append(chunk)
        size += len(chunk)
        if size >= MAX_BYTES:
            break
        if time.monotonic() > end:
            raise TimeoutError(f"download exceeded {DEADLINE:.0f}s")
    return b"".join(chunks)[:MAX_BYTES]


def _inflate(body: bytes, headers: Mapping[str, str]) -> bytes:
    """Undo ``Content-Encoding: gzip | deflate``, streaming, capped at ``MAX_BYTES``.

    Returns the raw bytes if they do not decompress; raises ``ResponseTooLarge``
    when the decompressed size exceeds the cap and ``EOFError`` when the
    compressed stream is truncated.
    """
    encoding = headers.get("content-encoding", "").lower()
    wbits_options: tuple[int, ...]
    if encoding in ("gzip", "x-gzip"):
        wbits_options = (16 + zlib.MAX_WBITS,)
    elif encoding == "deflate":
        wbits_options = (zlib.MAX_WBITS, -zlib.MAX_WBITS)  # zlib-wrapped, then raw
    else:
        return body
    for wbits in wbits_options:
        inflater = zlib.decompressobj(wbits)
        try:
            out = inflater.decompress(body, MAX_BYTES + 1)
        except zlib.error:
            continue
        if len(out) > MAX_BYTES:
            raise ResponseTooLarge(f"decompressed body exceeds {MAX_BYTES} bytes")
        if not inflater.eof:
            raise EOFError("compressed body is truncated")
        return out
    return body


class UrllibTransport:
    """Stdlib transport; HTTP errors become responses, network errors status 0."""

    def request(
        self, url: str, headers: Mapping[str, str], timeout: float
    ) -> HttpResponse:
        safe = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%~-._")
        if urllib.parse.urlparse(safe).scheme not in ("http", "https"):
            return HttpResponse(0, {}, b"", url, "unsupported URL scheme")
        req = urllib.request.Request(
            safe, headers={"Accept-Encoding": "gzip, deflate", **headers}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                hdrs = {k.lower(): v for k, v in resp.headers.items()}
                body = _inflate(_read_limited(resp), hdrs)
                return HttpResponse(resp.status, hdrs, body, resp.geturl())
        except urllib.error.HTTPError as exc:
            hdrs = {k.lower(): v for k, v in exc.headers.items()}
            try:
                body = _inflate(_read_limited(exc), hdrs)
            except (ResponseTooLarge, *READ_ERRORS):
                body = b""  # the status code still tells what happened
            return HttpResponse(exc.code, hdrs, body, exc.geturl() or url)
        except ResponseTooLarge as exc:
            return HttpResponse(0, {}, b"", url, UNREADABLE + str(exc))
        except (urllib.error.URLError, *READ_ERRORS) as exc:
            return HttpResponse(0, {}, b"", url, f"{type(exc).__name__}: {exc}")


class Throttle:
    """Keeps requests to one host at least ``interval`` seconds apart."""

    def __init__(
        self,
        interval: float = MIN_HOST_INTERVAL,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.interval = interval
        self._clock = clock
        self._sleep = sleep
        self._last: dict[str, float] = {}

    def wait(self, url: str) -> None:
        host = urllib.parse.urlparse(url).netloc.lower()
        last = self._last.get(host)
        if last is not None:
            delay = last + self.interval - self._clock()
            if delay > 0:
                self._sleep(delay)
        self._last[host] = self._clock()


def looks_like_challenge(body: bytes, content_type: str) -> bool:
    """A short HTML page with a captcha / "access denied" marker.

    Only consulted after a passage failed to match: a real page that happens to
    mention "captcha" and still contains the quote is fine.
    """
    if "html" not in content_type.lower() or len(body) >= 40_000:
        return False
    low = body.decode("utf-8", errors="replace").lower()
    return any(marker in low for marker in BLOCK_MARKERS)


def classify(resp: HttpResponse) -> tuple[str, str]:
    """``(status, detail)`` with status ok | blocked | gone | timeout."""
    code = resp.status
    if code == 0:
        if resp.error.startswith(UNREADABLE):
            return "unreadable", resp.error[len(UNREADABLE) :]
        return "timeout", resp.error or "request failed"
    if code in (404, 410):
        return "gone", f"HTTP {code}"
    if code >= 500:
        return "timeout", f"HTTP {code}"
    if code >= 400:
        return "blocked", f"HTTP {code}"
    if not 200 <= code < 300:
        return "blocked", f"HTTP {code}"
    if not resp.body:
        return "gone", "empty body"
    return "ok", f"HTTP {code}"


# --------------------------------------------------------------------------
# Cache and fetching
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Fetched:
    """The outcome of fetching one source (``status`` ok when ``body`` is set)."""

    status: str
    method: str = ""
    url: str = ""
    final_url: str = ""
    fetched_at: str = ""
    sha256: str = ""
    content_type: str = ""
    body: bytes = b""
    detail: str = ""
    from_cache: bool = False


class Cache:
    """``<dir>/<sha256(key)>.{body,meta.json}``."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _paths(self, key: str) -> tuple[Path, Path]:
        stem = hashlib.sha256(key.encode()).hexdigest()
        return self.directory / f"{stem}.body", self.directory / f"{stem}.meta.json"

    def load(self, key: str) -> tuple[dict[str, Any], bytes] | None:
        body_path, meta_path = self._paths(key)
        try:
            meta = cast("dict[str, Any]", json.loads(meta_path.read_text("utf-8")))
            return meta, body_path.read_bytes()
        except OSError, ValueError:
            return None

    def load_text(self, sha256: str) -> str | None:
        """Normalized text extracted earlier from a body with this hash."""
        try:
            return (self.directory / f"{sha256}.{TEXT_VERSION}.text").read_text("utf-8")
        except OSError:
            return None

    def store_text(self, sha256: str, text: str) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / f"{sha256}.{TEXT_VERSION}.text").write_text(
            text, encoding="utf-8"
        )

    def store(self, key: str, meta: dict[str, Any], body: bytes) -> None:
        body_path, meta_path = self._paths(key)
        self.directory.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(body)
        meta_path.write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Fetcher:
    """Cache -> origin -> via -> archive, each unique URL fetched once."""

    def __init__(
        self,
        transport: Transport,
        cache: Cache,
        throttle: Throttle,
        *,
        offline: bool = False,
        now: Callable[[], datetime] = _utcnow,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.transport = transport
        self.cache = cache
        self.throttle = throttle
        self.offline = offline
        self._now = now
        self._sleep = sleep
        self._memo: dict[str, Fetched] = {}

    # -- single URL ---------------------------------------------------------

    def _request(self, url: str, headers: Mapping[str, str]) -> HttpResponse:
        hdrs = {
            "User-Agent": USER_AGENT,
            "Accept": ACCEPT,
            **headers,
        }
        resp = HttpResponse(0, {}, b"", url, "not requested")
        for attempt in range(MAX_RETRIES + 1):
            self.throttle.wait(url)
            resp = self.transport.request(url, hdrs, TIMEOUT)
            retryable = (
                resp.status == 0 and not resp.error.startswith(UNREADABLE)
            ) or resp.status >= 500
            if not retryable or attempt == MAX_RETRIES:
                break
            self._sleep(2.0 * (attempt + 1))
        return resp

    def _from_cache(
        self,
        meta: dict[str, Any],
        body: bytes,
        url: str,
        method: str,
        *,
        from_cache: bool,
    ) -> Fetched:
        return Fetched(
            "ok",
            method=method,
            url=url,
            final_url=str(meta.get("final_url", url)),
            fetched_at=str(meta.get("fetched_at", "")),
            sha256=hashlib.sha256(body).hexdigest(),
            content_type=str(meta.get("content_type", "")),
            body=body,
            from_cache=from_cache,
        )

    def _fresh(self, meta: dict[str, Any]) -> bool:
        try:
            when = datetime.fromisoformat(str(meta["fetched_at"]))
        except KeyError, ValueError:
            return False
        return (self._now() - when).total_seconds() < FRESH_SECONDS

    def _store(self, key: str, url: str, resp: HttpResponse, method: str) -> Fetched:
        ctype = resp.headers.get("content-type", "")
        meta = {
            "url": url,
            "final_url": resp.final_url,
            "status": resp.status,
            "etag": resp.headers.get("etag"),
            "last_modified": resp.headers.get("last-modified"),
            "fetched_at": self._now().isoformat(timespec="seconds"),
            "via": method,
            "content_type": ctype,
        }
        self.cache.store(key, meta, resp.body)
        return self._from_cache(meta, resp.body, url, method, from_cache=False)

    def get(self, url: str, method: str) -> Fetched:
        """Fetch ``url`` once (cached, revalidated, or from the network)."""
        if url not in self._memo:
            self._memo[url] = self._get(url, method)
        # One fetch per URL, but the method is how *this* caller reached it.
        return replace(self._memo[url], method=method)

    def _get(self, url: str, method: str) -> Fetched:
        cached = self.cache.load(url)
        if cached and (self.offline or self._fresh(cached[0])):
            return self._from_cache(*cached, url, method, from_cache=True)
        if self.offline:
            return Fetched("timeout", method, url, detail="not in cache (offline)")
        headers: dict[str, str] = {}
        if cached:
            if cached[0].get("etag"):
                headers["If-None-Match"] = str(cached[0]["etag"])
            if cached[0].get("last_modified"):
                headers["If-Modified-Since"] = str(cached[0]["last_modified"])
        resp = self._request(url, headers)
        if resp.status == 304 and cached:
            meta = dict(cached[0])
            meta["fetched_at"] = self._now().isoformat(timespec="seconds")
            self.cache.store(url, meta, cached[1])
            return self._from_cache(meta, cached[1], url, method, from_cache=True)
        status, detail = classify(resp)
        if status != "ok":
            return Fetched(status, method, url, resp.final_url, detail=detail)
        return self._store(url, url, resp, method)

    # -- archive ------------------------------------------------------------

    def archive(self, url: str) -> Fetched:
        """The Wayback snapshot of ``url`` closest to :data:`CHECKED_TIMESTAMP`."""
        key = "archive:" + url
        if key in self._memo:
            return self._memo[key]
        out = self._archive(key, url)
        self._memo[key] = out
        return out

    def _archive(self, key: str, url: str) -> Fetched:
        cached = self.cache.load(key)
        if cached:  # snapshots are immutable
            return self._from_cache(*cached, url, "archive", from_cache=True)
        if self.offline:
            return Fetched("timeout", "archive", url, detail="not in cache (offline)")
        query = urllib.parse.urlencode({"url": url, "timestamp": CHECKED_TIMESTAMP})
        lookup = self._request(f"{WAYBACK_API}?{query}", {"Accept": "application/json"})
        status, detail = classify(lookup)
        if status != "ok":
            return Fetched(status, "archive", url, detail=f"archive lookup: {detail}")
        try:
            data = json.loads(lookup.body)
            closest = data["archived_snapshots"]["closest"]
            snapshot = str(closest["url"])
            if not closest.get("available"):
                raise KeyError("available")
        except ValueError, KeyError, TypeError:
            return Fetched("gone", "archive", url, detail="no archive snapshot")
        raw = re.sub(r"/web/(\d+)/", r"/web/\1id_/", snapshot, count=1)
        raw = re.sub(r"^http://", "https://", raw)
        resp = self._request(raw, {})
        status, detail = classify(resp)
        if status != "ok":
            return Fetched(status, "archive", url, raw, detail=f"snapshot: {detail}")
        return self._store(key, url, resp, "archive")

    # -- one source ---------------------------------------------------------

    def fetch_source(self, src: Source) -> Fetched:
        """Origin, then ``via.url``, then the archive; the first failure if none."""
        url = src["url"]
        failures: list[Fetched] = []
        candidates = [("origin", url)]
        via_url = src.get("via", {}).get("url")
        if via_url:
            candidates.append(("via", via_url))
        for method, candidate in candidates:
            got = self.get(candidate, method)
            if got.status == "ok":
                return got
            failures.append(got)
        got = self.archive(url)
        if got.status == "ok":
            return got
        first = failures[0]
        return Fetched(
            first.status,
            first.method,
            url,
            first.final_url,
            detail=f"{first.detail}; archive: {got.detail}",
        )


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------


@dataclass
class QuoteResult:
    id: str
    source: str
    url: str
    result: str
    score: float | None = None
    method: str | None = None
    final_url: str | None = None
    fetched_at: str | None = None
    sha256: str | None = None
    detail: str = ""
    from_cache: bool = False
    missing: list[str] = field(default_factory=list)


def _forget_fetch(res: QuoteResult) -> None:
    """Drop what a blocked/challenge fetch must not leave in the manifest."""
    res.method = res.final_url = res.fetched_at = res.sha256 = None
    res.from_cache = False


def _id_key(qid: str) -> tuple[int, str]:
    m = re.fullmatch(r"Q(\d+)", qid)
    return (int(m.group(1)) if m else 10**9, qid)


class Verifier:
    def __init__(self, fetcher: Fetcher, registry: Mapping[str, Source]) -> None:
        self.fetcher = fetcher
        self.registry = registry
        self._text: dict[str, str | None] = {}

    def _normalized(self, fetched: Fetched) -> str | None:
        """Normalized text of a fetched source; ``None`` if unreadable."""
        key = fetched.sha256 + fetched.url
        if key not in self._text:
            cached = self.fetcher.cache.load_text(fetched.sha256)
            if cached is not None:
                self._text[key] = cached
                return cached
            try:
                raw = extract_text(
                    fetched.body, fetched.content_type, fetched.final_url or fetched.url
                )
                self._text[key] = normalize(raw)
                self.fetcher.cache.store_text(fetched.sha256, self._text[key] or "")
            except ValueError:
                self._text[key] = None
        return self._text[key]

    def verify(self, quote: Mapping[str, Any]) -> QuoteResult:
        qid = str(quote["id"])
        slug = str(quote["source"])
        src = self.registry[slug]
        res = QuoteResult(qid, slug, src["url"], "matched")
        segments = quoted_segments(str(quote["text"]))
        if not segments:
            res.result = "no-quote"
            res.detail = "no double-quoted passage in the cell"
            return res
        primary = self.fetcher.fetch_source(src)
        res.method, res.final_url = primary.method or None, primary.final_url or None
        res.fetched_at = primary.fetched_at[:10] or None
        res.sha256 = primary.sha256 or None
        res.from_cache = primary.from_cache
        if primary.status != "ok":
            res.result, res.detail = primary.status, primary.detail
            _forget_fetch(res)
            return self._paid(res, src)
        challenge = looks_like_challenge(primary.body, primary.content_type)
        text = self._normalized(primary)
        if text is None:
            if challenge:
                res.result, res.detail = "blocked", "challenge page"
                _forget_fetch(res)
                return self._paid(res, src)
            # Unreadable: another copy may still match in full (extra sources
            # never rescue it). Otherwise the verdict, and its evidence, stay
            # the primary's.
            for alt in self._alternatives(src, primary):
                alt_text = self._normalized(alt)
                if alt_text is None:
                    continue
                if self._judge(quote, segments, alt_text, use_extras=False)[0] >= 1.0:
                    res.score, res.missing, res.result = 1.0, [], "matched"
                    self._adopt(res, alt)
                    return self._paid(res, src)
            res.result = "unreadable"
            res.detail = "source text could not be extracted"
            return self._paid(res, src)

        score, missing, pending = self._judge(quote, segments, text)
        res.score, res.missing = score, missing
        # Unresolved extra sources are not fixed by another copy of this source,
        # unless the page itself is a challenge page.
        if score < 1.0 and (challenge or not pending):
            # The page was fetched but lacks the passage (truncated, paywalled,
            # changed since, or a challenge page): try the other copies --
            # `via.url` if it differs, then the archive snapshot closest to the
            # checked date. Only a copy that fully matches wins and replaces
            # the recorded evidence; the verdict otherwise stays the original
            # fetch's (including its challenge status).
            for alt in self._alternatives(src, primary):
                alt_text = self._normalized(alt)
                if alt_text is None:
                    continue
                a_score, _, _ = self._judge(quote, segments, alt_text)
                if a_score >= 1.0:
                    score, missing, pending = a_score, [], []
                    res.score, res.missing = score, missing
                    self._adopt(res, alt)
                    break
        if score >= 1.0:
            res.result = "matched"
        elif challenge:
            res.result, res.detail = "blocked", "challenge page"
            _forget_fetch(res)
        elif pending:
            res.result = "blocked"
            res.detail = "extra source(s) could not be fetched: " + ", ".join(pending)
            _forget_fetch(res)
        elif score >= NEAR_MISS_MIN:
            res.result = "near-miss"
        else:
            res.result = "not-found"
        return self._paid(res, src)

    @staticmethod
    def _adopt(res: QuoteResult, alt: Fetched) -> None:
        """Record ``alt`` as the fetch that produced the verdict."""
        res.method, res.final_url = alt.method, alt.final_url or None
        res.fetched_at = alt.fetched_at[:10] or None
        res.sha256 = alt.sha256 or None
        res.from_cache = alt.from_cache

    def _alternatives(self, src: Source, primary: Fetched) -> Iterator[Fetched]:
        """Other fetched copies of a source, tried lazily after a content miss.

        ``via.url`` when it is a different URL than the one already read, then
        the archive snapshot (unless the primary already is one). Fetch
        failures are skipped.
        """
        via_url = src.get("via", {}).get("url")
        if via_url and via_url != primary.url and primary.method != "via":
            alt = self.fetcher.get(via_url, "via")
            if alt.status == "ok":
                yield alt
        if primary.method != "archive":
            alt = self.fetcher.archive(src["url"])
            if alt.status == "ok":
                yield alt

    def _judge(
        self,
        quote: Mapping[str, Any],
        segments: Sequence[str],
        text: str,
        *,
        use_extras: bool = True,
    ) -> tuple[float, list[str], list[str]]:
        """``(score, missing passages, failed extra sources)`` against ``text``.

        A passage missing from the main text is also looked for in the quote's
        ``extra_sources`` (unless ``use_extras`` is false).
        """
        texts = [text]
        pending: list[str] = []
        extras_loaded = False
        scores: list[float] = []
        missing: list[str] = []
        for seg in segments:
            score = score_segment(seg, text)
            if score < 1.0 and use_extras:
                if not extras_loaded:
                    extras_loaded = True
                    for extra in quote.get("extra_sources", []):
                        got = self.fetcher.fetch_source(self.registry[extra])
                        extra_text = (
                            self._normalized(got) if got.status == "ok" else None
                        )
                        if extra_text is None:
                            pending.append(f"{extra}: {got.status}")
                        else:
                            texts.append(extra_text)
                for other in texts[1:]:
                    score = max(score, score_segment(seg, other))
            scores.append(score)
            if score < 1.0:
                missing.append(seg)
        return min(scores), missing, pending

    def explain(self, quote: Mapping[str, Any]) -> list[str]:
        """Per passage, the best-matching window of each source text (stdout only)."""
        qid = str(quote["id"])
        slugs = [str(quote["source"]), *map(str, quote.get("extra_sources", []))]
        lines = [f"== {qid}"]
        texts: list[tuple[str, str]] = []
        for slug in slugs:
            got = self.fetcher.fetch_source(self.registry[slug])
            text = self._normalized(got) if got.status == "ok" else None
            if text is None:
                lines.append(
                    f"source {slug}: not available ({got.status}: {got.detail})"
                )
            else:
                texts.append((slug, text))
        for seg in quoted_segments(str(quote["text"])):
            lines.append(f"passage: {_snippet(seg, 600)}")
            for part in split_ellipsis(seg):
                lines.append(f"  part (normalized): {part}")
                for slug, text in texts:
                    exact = text.find(part)
                    if exact >= 0:
                        score, start = 1.0, exact
                    else:
                        score, start = best_window(part, text)
                    if start < 0:
                        lines.append(f"  [{slug}] score 0.00: no similar text found")
                        continue
                    window = text[start : start + EXPLAIN_CHARS]
                    lines.append(f"  [{slug}] score {score:.2f}, best window:")
                    lines.append(f"    {window}")
        return lines

    @staticmethod
    def _paid(res: QuoteResult, src: Source) -> QuoteResult:
        """A paid source that could not confirm the quote is unverifiable."""
        if src.get("paid") and res.result != "matched":
            res.detail = f"{res.result}: {res.detail}".strip(": ")
            res.result = "paid"
        return res


def verifiable_quotes(
    quotes: Sequence[Mapping[str, Any]], only: set[str] | None = None
) -> list[Mapping[str, Any]]:
    """Quotes with a source that are not placeholders, optionally restricted."""
    return [
        q
        for q in quotes
        if not q.get("placeholder")
        and q.get("source")
        and (only is None or q["id"] in only)
    ]


# --------------------------------------------------------------------------
# Manifest and report
# --------------------------------------------------------------------------


def manifest_entry(r: QuoteResult) -> dict[str, Any]:
    return {
        "id": r.id,
        "source": r.source,
        "url": r.url,
        "final_url": r.final_url,
        "method": r.method,
        "fetched_at": r.fetched_at,
        "sha256": r.sha256,
        "result": r.result,
        "score": None if r.score is None else round(r.score, 3),
    }


def render_manifest(
    results: Sequence[QuoteResult],
    previous: Sequence[Mapping[str, Any]] = (),
    valid_ids: set[str] | None = None,
) -> str:
    """Deterministic JSON: entries by quote number, keys sorted. Merges ``previous``.

    ``valid_ids`` (when given) prunes previous entries of quotes that no longer
    exist or are now placeholders.
    """
    entries = {
        str(e["id"]): dict(e)
        for e in previous
        if valid_ids is None or str(e["id"]) in valid_ids
    }
    for r in results:
        entries[r.id] = manifest_entry(r)
    ordered = [entries[k] for k in sorted(entries, key=_id_key)]
    return json.dumps(ordered, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _snippet(text: str, n: int = 90) -> str:
    one = _SPACE.sub(" ", text).strip()
    return one if len(one) <= n else one[: n - 1] + "…"


def render_report(results: Sequence[QuoteResult]) -> str:
    by: dict[str, list[QuoteResult]] = {k: [] for k in RESULT_ORDER}
    for r in results:
        by.setdefault(r.result, []).append(r)
    failing = sum(len(by[k]) for k in FAILING)
    unchecked = sum(len(by[k]) for k in UNCHECKED)
    lines = [
        f"<!-- verify-sources: failing={failing} unchecked={unchecked} -->",
        "# Source verification",
        "",
        f"{len(results)} quote(s) checked: {len(by['matched'])} matched, "
        f"{failing} failing, {unchecked} unverifiable.",
        "",
        "| Result | Count |",
        "| --- | ---: |",
        *(f"| {k} | {len(by[k])} |" for k in RESULT_ORDER if by[k]),
        "",
    ]
    for kind in (*FAILING, *UNCHECKED, "no-quote"):
        rows = sorted(by[kind], key=lambda r: _id_key(r.id))
        if not rows:
            continue
        lines += [f"## {kind} ({len(rows)})", ""]
        for r in rows:
            score = (
                f" ({r.score:.2f})" if r.score is not None and kind in FAILING else ""
            )
            lines.append(f"- {r.id} `{r.source}`{score}: {r.url}")
            if r.detail:
                lines.append(f"  - {r.detail}")
            lines += [f'  - missing: "{_snippet(m)}"' for m in r.missing]
        lines.append("")
    archived = sorted(
        (r for r in by["matched"] if r.method == "archive"), key=lambda r: _id_key(r.id)
    )
    if archived:
        lines += [f"## Verified via archive ({len(archived)})", ""]
        lines += [f"- {r.id} `{r.source}`: {r.final_url}" for r in archived]
        lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def _load_quotes(root: Path) -> list[Mapping[str, Any]]:
    return cast("list[Mapping[str, Any]]", load_yaml(root / "data" / "quotes.yaml"))


def run(
    root: Path,
    *,
    cache_dir: Path,
    offline: bool = False,
    only: set[str] | None = None,
    manifest: Path,
    update_manifest: bool = False,
    report: Path | None = None,
    explain: set[str] | None = None,
    transport: Transport | None = None,
    throttle: Throttle | None = None,
    sleep: Callable[[float], None] = time.sleep,
    echo: Callable[[str], None] = print,
) -> int:
    """Verify quotes; 0 when nothing fetched contradicts a quote, else 1."""
    registry = load_registry(root)
    fetcher = Fetcher(
        transport or UrllibTransport(),
        Cache(cache_dir),
        throttle or Throttle(),
        offline=offline,
        sleep=sleep,
    )
    verifier = Verifier(fetcher, registry)
    if explain:
        for q in verifiable_quotes(_load_quotes(root), explain):
            for line in verifier.explain(q):
                echo(line)
        return 0
    all_quotes = _load_quotes(root)
    quotes = verifiable_quotes(all_quotes, only)
    results: list[QuoteResult] = []
    for q in quotes:
        results.append(verifier.verify(q))
        echo(f"  {results[-1].id} {results[-1].source}: {results[-1].result}")

    text = render_report(results)
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(text, encoding="utf-8")
    if update_manifest:
        previous: list[Mapping[str, Any]] = []
        if manifest.is_file():
            previous = json.loads(manifest.read_text("utf-8"))
        manifest.parent.mkdir(parents=True, exist_ok=True)
        valid = {str(q["id"]) for q in verifiable_quotes(all_quotes)}
        manifest.write_text(render_manifest(results, previous, valid), encoding="utf-8")
    counts = {k: sum(1 for r in results if r.result == k) for k in RESULT_ORDER}
    echo(
        "taxonomy verify-sources: "
        + ", ".join(f"{n} {k}" for k, n in counts.items() if n)
    )
    return 1 if any(r.result in FAILING for r in results) else 0
