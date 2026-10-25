"""Command line: ``taxonomy check | build [--check] | site | paper``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from taxonomy import build as build_mod
from taxonomy import render_paper, render_site
from taxonomy.load import find_root
from taxonomy.validate import run_checks


def _root(arg: str | None) -> Path:
    return Path(arg).resolve() if arg else find_root()


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
    args = parser.parse_args(argv)

    if args.command == "check":
        return cmd_check(_root(args.root))
    if args.command == "build":
        return cmd_build(_root(args.root), args.check)
    try:
        if args.command == "site":
            render_site.build(args.out)
        else:
            render_paper.build(args.out)
    except NotImplementedError as exc:
        print(f"taxonomy {args.command}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
