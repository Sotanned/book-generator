"""Structural validation for a book. Pure functions returning findings."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from bookgen.chapter import (
    MAX_MCQS,
    MAX_WORDS,
    MIN_MCQS,
    MIN_WORDS,
    chapter_filename,
    parse_chapter,
)
from bookgen.lexicon import find_drift, parse_lexicon
from bookgen.syllabus import ChapterEntry, load_syllabus

MERMAID_TYPES = frozenset({
    "graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "journey", "gantt", "pie", "mindmap",
    "timeline", "gitGraph", "quadrantChart", "block-beta",
})


@dataclass(frozen=True)
class Finding:
    where: str
    message: str


def _check_written_chapter(book_dir: Path, entry: ChapterEntry) -> list[Finding]:
    path = book_dir / "chapters" / chapter_filename(entry.id, entry.slug)
    where = str(path.relative_to(book_dir))
    if not path.exists():
        return [Finding(where, f"missing chapter file for status {entry.status!r}")]

    try:
        chapter = parse_chapter(path)
    except ValueError as exc:
        return [Finding(where, str(exc))]

    findings: list[Finding] = []
    if str(chapter.meta.get("chapter")) != entry.id:
        findings.append(
            Finding(where, f"front matter chapter {chapter.meta.get('chapter')!r} != syllabus {entry.id!r}")
        )
    if str(chapter.meta.get("domain")) != entry.domain_id:
        findings.append(
            Finding(where, f"front matter domain {chapter.meta.get('domain')!r} != syllabus {entry.domain_id!r}")
        )
    if str(chapter.meta.get("title")) != entry.title:
        findings.append(
            Finding(where, f"front matter title {chapter.meta.get('title')!r} != syllabus {entry.title!r}")
        )
    if str(chapter.meta.get("status")) != entry.status:
        findings.append(
            Finding(where, f"front matter status {chapter.meta.get('status')!r} != syllabus {entry.status!r}")
        )
    for source in chapter.meta.get("sources") or []:
        if not (book_dir / source).exists():
            findings.append(
                Finding(where, f"front matter lists a missing source: {source}")
            )
    if not MIN_WORDS <= chapter.word_count <= MAX_WORDS:
        findings.append(
            Finding(where, f"word count {chapter.word_count} outside {MIN_WORDS}-{MAX_WORDS}")
        )
    if not MIN_MCQS <= chapter.mcq_count <= MAX_MCQS:
        findings.append(
            Finding(where, f"MCQ count {chapter.mcq_count} outside {MIN_MCQS}-{MAX_MCQS}")
        )
    if chapter.question_count != chapter.mcq_count:
        findings.append(
            Finding(
                where,
                f"question count {chapter.question_count} != answer count {chapter.mcq_count}",
            )
        )
    for block in chapter.mermaid_blocks:
        first_token = _mermaid_type_token(block)
        if first_token not in MERMAID_TYPES:
            findings.append(
                Finding(where, f"mermaid block declares unknown diagram type {first_token!r}")
            )
    return findings


def _mermaid_type_token(block: str) -> str:
    """Return the diagram-type token, skipping leading blank lines and %%-directives."""
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        tokens = stripped.split()
        return tokens[0] if tokens else ""
    return ""


def check_book(book_dir: Path) -> list[Finding]:
    book_dir = Path(book_dir)
    syllabus = load_syllabus(book_dir / "syllabus.yaml")
    findings: list[Finding] = []

    counts = Counter(c.id for c in syllabus.chapters())
    findings += [
        Finding("syllabus.yaml", f"duplicate chapter id {cid!r}")
        for cid, n in sorted(counts.items())
        if n > 1
    ]

    for entry in syllabus.chapters():
        for source in entry.sources:
            if not (book_dir / source).exists():
                findings.append(
                    Finding("syllabus.yaml", f"chapter {entry.id}: missing source {source}")
                )
        if entry.status != "unwritten":
            findings += _check_written_chapter(book_dir, entry)

    findings += [
        Finding("world/lexicon.md", drift)
        for drift in find_drift(parse_lexicon(book_dir / "world" / "lexicon.md"))
    ]
    return findings
