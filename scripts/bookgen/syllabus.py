"""Load, query, and update a book's syllabus.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML

VALID_STATUSES = frozenset({"unwritten", "drafted", "approved"})

_yaml = YAML()  # round-trip mode by default: preserves comments and key order
_yaml.preserve_quotes = True


@dataclass(frozen=True)
class ChapterEntry:
    id: str
    slug: str
    title: str
    domain_id: str
    topics: list[str]
    sources: list[str]
    status: str


@dataclass(frozen=True)
class Domain:
    id: str
    name: str
    weight: float
    chapters: list[ChapterEntry]


@dataclass(frozen=True)
class Syllabus:
    book_id: str
    title: str
    world: str
    exam: dict
    domains: list[Domain]
    path: Path

    def chapters(self) -> list[ChapterEntry]:
        return [c for d in self.domains for c in d.chapters]

    def find(self, chapter_id: str) -> ChapterEntry | None:
        return next((c for c in self.chapters() if c.id == chapter_id), None)

    def next_unwritten(self) -> ChapterEntry | None:
        return next((c for c in self.chapters() if c.status == "unwritten"), None)


def _read(path: Path):
    with path.open(encoding="utf-8") as fh:
        return _yaml.load(fh)


def load_syllabus(path: Path) -> Syllabus:
    raw = _read(Path(path))
    domains = [
        Domain(
            id=str(d["id"]),
            name=str(d["name"]),
            weight=float(d["weight"]),
            chapters=[
                ChapterEntry(
                    id=str(c["id"]),
                    slug=str(c["slug"]),
                    title=str(c["title"]),
                    domain_id=str(d["id"]),
                    topics=[str(t) for t in c.get("topics", [])],
                    sources=[str(s) for s in c.get("sources", [])],
                    status=str(c["status"]),
                )
                for c in d.get("chapters", [])
            ],
        )
        for d in raw.get("domains", [])
    ]
    return Syllabus(
        book_id=str(raw["book_id"]),
        title=str(raw["title"]),
        world=str(raw["world"]),
        exam=dict(raw["exam"]),
        domains=domains,
        path=Path(path),
    )


def set_status(path: Path, chapter_id: str, status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"unknown status {status!r}; expected one of {sorted(VALID_STATUSES)}")
    path = Path(path)
    raw = _read(path)
    for domain in raw.get("domains", []):
        for chapter in domain.get("chapters", []):
            if str(chapter["id"]) == chapter_id:
                chapter["status"] = status
                with path.open("w", encoding="utf-8", newline="\n") as fh:
                    _yaml.dump(raw, fh)
                return
    raise KeyError(f"no chapter with id {chapter_id!r} in {path}")
