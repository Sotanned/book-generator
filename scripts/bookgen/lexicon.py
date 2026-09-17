"""Parse the concept/story-element lexicon and detect metaphor drift."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")


@dataclass(frozen=True)
class LexiconEntry:
    concept: str
    story_element: str
    first_appears: str


def parse_lexicon(path: Path) -> list[LexiconEntry]:
    path = Path(path)
    if not path.exists():
        return []
    entries: list[LexiconEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or _SEPARATOR.match(line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3 or cells[0].lower() == "concept":
            continue
        entries.append(LexiconEntry(cells[0], cells[1], cells[2]))
    return entries


def find_drift(entries: list[LexiconEntry]) -> list[str]:
    by_concept: dict[str, set[str]] = defaultdict(set)
    by_element: dict[str, set[str]] = defaultdict(set)
    for entry in entries:
        by_concept[entry.concept].add(entry.story_element)
        by_element[entry.story_element].add(entry.concept)

    drift = [
        f"concept {concept!r} maps to multiple story elements: {sorted(elements)}"
        for concept, elements in by_concept.items()
        if len(elements) > 1
    ]
    drift += [
        f"story element {element!r} is reused for multiple concepts: {sorted(concepts)}"
        for element, concepts in by_element.items()
        if len(concepts) > 1
    ]
    return sorted(drift)
