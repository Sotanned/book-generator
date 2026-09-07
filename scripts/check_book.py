"""Validate one or more books. Exit 1 if any finding is reported.

Usage:
    python scripts/check_book.py                 # every book under books/
    python scripts/check_book.py databricks-de-associate
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bookgen.checks import check_book  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = REPO_ROOT / "books"


def main(argv: list[str]) -> int:
    if argv:
        book_dirs = [BOOKS_DIR / name for name in argv]
    else:
        book_dirs = sorted(p for p in BOOKS_DIR.iterdir() if (p / "syllabus.yaml").exists())

    total = 0
    for book_dir in book_dirs:
        if not (book_dir / "syllabus.yaml").exists():
            print(f"ERROR {book_dir.name}: no syllabus.yaml")
            total += 1
            continue
        findings = check_book(book_dir)
        for finding in findings:
            print(f"ERROR {book_dir.name}/{finding.where}: {finding.message}")
        total += len(findings)
        if not findings:
            print(f"OK    {book_dir.name}")

    if total:
        print(f"\n{total} problem(s) found.")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
