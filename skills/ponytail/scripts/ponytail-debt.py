#!/usr/bin/env python3
"""ponytail-debt — harvest deferred `ponytail:` shortcuts into pending.md.

Deterministic core of /ponytail-debt (see ../SKILL.md). Scans git-tracked
files for `ponytail:` marker comments across all comment styles, dedups
against the entries already in pending.md, and appends only NEW ones under
a "Ponytail debt" grouping. Running it twice adds nothing.

Usage:
    python3 ponytail-debt.py [--dry-run] [--repo-root PATH]

Dedup key: (file path, marker text). Line numbers are recorded for display
but deliberately excluded from the key — lines drift as files change, and
keying on them would re-append the same shortcut after every edit above it.

Exit codes: 0 = ok (including "nothing new"), 1 = error.
"""

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

# Comment prefixes: #, //, --, ;, <!--, /*, or a leading * (block-comment body).
MARKER_RE = re.compile(
    r"""(?:\#|//|--|;|<!--|/\*|^\s*\*)\s*ponytail:\s*(?P<text>.+)""",
    re.IGNORECASE,
)
# Strip comment closers off the captured text.
CLOSER_RE = re.compile(r"\s*(?:-->|\*/)\s*$")

# Files/dirs that legitimately contain the string but are not debt.
SKIP_PARTS = {".git", "node_modules", "archives", "knowledge", "__pycache__"}
SKIP_PATHS = {
    ".claude/skills/ponytail",  # the skill itself (format examples)
    "references/ponytail.md",   # the doctrine page
    "pending.md",               # the ledger we append to
}

# Existing pending.md entry, as written by this script.
ENTRY_RE = re.compile(
    r"ponytail-debt\s+—\s+`(?P<path>[^:`]+):(?P<line>\d+)`\s+—\s+(?P<text>.+?)\s*$"
)


def git_files(root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    return [root / line for line in out.splitlines() if line]


def skippable(rel: str) -> bool:
    parts = rel.split("/")
    if any(p in SKIP_PARTS for p in parts):
        return True
    return any(rel == s or rel.startswith(s + "/") for s in SKIP_PATHS)


def scan(root: Path) -> list[tuple[str, int, str]]:
    """Return (relative path, line number, marker text) for every marker."""
    found = []
    for f in git_files(root):
        rel = f.relative_to(root).as_posix()
        if skippable(rel) or not f.is_file():
            continue
        try:
            raw = f.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:8192]:  # binary
            continue
        text = raw.decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            m = MARKER_RE.search(line)
            if not m:
                continue
            marker = CLOSER_RE.sub("", m.group("text")).strip()
            if not marker or marker.startswith("<what this skips"):
                continue  # empty or the format template itself
            found.append((rel, i, marker))
    return found


def existing_keys(pending: Path) -> set[tuple[str, str]]:
    if not pending.exists():
        return set()
    keys = set()
    for line in pending.read_text(encoding="utf-8").splitlines():
        m = ENTRY_RE.search(line)
        if m:
            keys.add((m.group("path"), m.group("text").strip()))
    return keys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="print, don't write")
    ap.add_argument("--repo-root", default=None, help="repo root (default: git toplevel)")
    args = ap.parse_args()

    if args.repo_root:
        root = Path(args.repo_root).resolve()
    else:
        root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
        )
    pending = root / "pending.md"

    markers = scan(root)
    known = existing_keys(pending)
    new = [(p, ln, txt) for (p, ln, txt) in markers if (p, txt) not in known]
    malformed = [(p, ln, txt) for (p, ln, txt) in markers if "," not in txt]

    today = datetime.date.today().isoformat()
    lines = [
        f"- [ ] {today} | [servy] ponytail-debt — `{p}:{ln}` — {txt}"
        for (p, ln, txt) in new
    ]

    print(f"markers found: {len(markers)} | already in pending.md: "
          f"{len(markers) - len(new)} | new: {len(new)}")
    for line in lines:
        print(("WOULD APPEND: " if args.dry_run else "APPEND: ") + line)
    if malformed:
        print(f"\nNOTE — {len(malformed)} marker(s) lack a clear "
              f"'<ceiling>, <upgrade path>' (no comma); fix the format:")
        for p, ln, txt in malformed:
            print(f"  {p}:{ln} — {txt}")

    if not new or args.dry_run:
        return 0

    text = pending.read_text(encoding="utf-8") if pending.exists() else ""
    block = ""
    if "## Ponytail debt" not in text:
        block += "\n## Ponytail debt — deferred shortcuts harvested from `ponytail:` markers\n"
    block += "\n".join(lines) + "\n"
    with pending.open("a", encoding="utf-8") as fh:
        if text and not text.endswith("\n"):
            fh.write("\n")
        fh.write(block)
    print(f"\nappended {len(new)} entrie(s) to {pending}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
