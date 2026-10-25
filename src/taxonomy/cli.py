"""Command line: ``taxonomy check | build | site | paper | verify-sources``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from taxonomy import build as build_mod
from taxonomy import render_paper, render_site, verify_sources
from taxonomy.load import find_root
from taxonomy.validate import run_checks


def _root(arg: str | None) -> Path:
    """The repository root from ``--root`` or the cwd; raises ``FileNotFoundError``."""
    if arg:
        root = Path(arg).resolve()
        if not (root / "data" / "meta.yaml").is_file():
            raise FileNotFoundError(f"{root} has no data/meta.yaml")
        return root
    return find_root()


def cmd_check(root: Path) -> int:
    findings = run_checks(root)
    for f in findings:
        print(f, file=sys.stderr)
    if findings:
        print(f"taxonomy check: {len(findings)} problem(s)", file=sys.stderr)
        return 1
    print("taxonomy check: ok")
    return 0


def cmd_build(root: Path, check: bool) -> int:
    if check:
        paths = build_mod.stale(root)
        if paths:
            print(
                "publication/ is stale; run `uv run taxonomy build`:", file=sys.stderr
            )
            for p in paths:
                print(f"  publication/{p}", file=sys.stderr)
            return 1
        print("taxonomy build --check: publication/ is up to date")
        return 0
    changed = build_mod.write(root)
    print(f"taxonomy build: {len(changed)} file(s) written")
    for p in changed:
        print(f"  publication/{p}")
    return 0


def _ids(arg: str | None) -> set[str] | None:
    return {i.strip() for i in arg.split(",") if i.strip()} if arg else None


def cmd_verify_sources(root: Path, args: argparse.Namespace) -> int:
    return verify_sources.run(
        root,
        cache_dir=root / args.cache_dir,
        offline=args.offline,
        only=_ids(args.only),
        explain=_ids(args.explain),
        manifest=root / args.manifest,
        update_manifest=args.update_manifest,
        report=root / args.report if args.report else None,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="taxonomy", description=__doc__)
    parser.add_argument("--root", help="repository root (default: found from the cwd)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="run the dataset integrity checks")
    b = sub.add_parser("build", help="write publication/")
    b.add_argument("--check", action="store_true", help="fail if publication/ is stale")
    s = sub.add_parser("site", help="build the site")
    s.add_argument("--out", type=Path, default=Path("build/site"))
    p = sub.add_parser("paper", help="build the PDF paper")
    p.add_argument("--out", type=Path, default=Path("build/paper.pdf"))
    v = sub.add_parser(
        "verify-sources", help="check that each quote appears in its fetched source"
    )
    v.add_argument("--cache-dir", type=Path, default=Path("build/source-cache"))
    v.add_argument("--offline", action="store_true", help="use only the cache")
    v.add_argument("--only", help="comma-separated quote IDs, e.g. Q12,Q13")
    v.add_argument("--manifest", type=Path, default=Path("sources/verification.json"))
    v.add_argument("--update-manifest", action="store_true", help="write the manifest")
    v.add_argument(
        "--explain",
        help="print the best-matching source window for these IDs (stdout only)",
    )
    v.add_argument("--report", type=Path, help="write a Markdown report here")
    args = parser.parse_args(argv)

    try:
        root = _root(args.root)
    except FileNotFoundError as exc:
        print(f"taxonomy {args.command}: {exc}", file=sys.stderr)
        return 1
    try:
        if args.command == "check":
            return cmd_check(root)
        if args.command == "build":
            return cmd_build(root, args.check)
        if args.command == "verify-sources":
            return cmd_verify_sources(root, args)
        if args.command == "site":
            render_site.build(args.out, root)
        else:
            render_paper.build(args.out, root)
    except NotImplementedError as exc:
        print(f"taxonomy {args.command}: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"taxonomy {args.command}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
