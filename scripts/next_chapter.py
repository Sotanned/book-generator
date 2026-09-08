"""Resolve the next unwritten chapter and the exact context needed to write it.

Usage:
    python scripts/next_chapter.py databricks-de-associate
Prints a JSON manifest. Exits 2 when the book is finished, 3 on a missing source,
64 on a wrong argument count, and 1 (with a traceback-free message on stderr) on
any other error, including a malformed syllabus.yaml.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bookgen.chapter import chapter_filename  # noqa: E402
from bookgen.syllabus import load_syllabus  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = REPO_ROOT / "books"


class BookFinished(Exception):
    """Raised when a syllabus has no unwritten chapters left."""


def build_manifest(book_dir: Path) -> dict:
    book_dir = Path(book_dir)
    syllabus = load_syllabus(book_dir / "syllabus.yaml")

    entry = syllabus.next_unwritten()
    if entry is None:
        raise BookFinished(f"no unwritten chapters left in {syllabus.book_id}")

    for source in entry.sources:
        if not (book_dir / source).exists():
            raise FileNotFoundError(f"chapter {entry.id} lists a missing source: {source}")

    all_chapters = syllabus.chapters()
    index = all_chapters.index(entry)
    previous_path = None
    for earlier in reversed(all_chapters[:index]):
        candidate = book_dir / "chapters" / chapter_filename(earlier.id, earlier.slug)
        if candidate.exists():
            previous_path = candidate
            break

    domain = next(d for d in syllabus.domains if d.id == entry.domain_id)

    context = [
        book_dir / "world" / "bible.md",
        book_dir / "world" / "lexicon.md",
        book_dir / "world" / "continuity.md",
    ]
    context += [book_dir / s for s in entry.sources]
    if previous_path is not None:
        context.append(previous_path)

    return {
        "book_id": syllabus.book_id,
        "book_dir": book_dir.as_posix(),
        "chapter": {
            "id": entry.id,
            "slug": entry.slug,
            "title": entry.title,
            "domain_id": entry.domain_id,
            "domain_name": domain.name,
            "topics": entry.topics,
            "status": entry.status,
        },
        "output_path": (book_dir / "chapters" / chapter_filename(entry.id, entry.slug)).as_posix(),
        "context_files": [p.as_posix() for p in context if p.exists()],
        "previous_chapter": previous_path.as_posix() if previous_path else None,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python scripts/next_chapter.py <book-id>", file=sys.stderr)
        return 64
    try:
        manifest = build_manifest(BOOKS_DIR / argv[0])
    except BookFinished as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001 - a broken syllabus must be loud, never silent
        print(f"syllabus error: {exc!r}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
