"""Parse a generated chapter file into front matter and measurable body."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from ruamel.yaml import YAML

MIN_WORDS = 2000
MAX_WORDS = 3000
MIN_MCQS = 3
MAX_MCQS = 5
UNVERIFIED_MARKER = '!!! warning "Unverified"'

_FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_FENCED = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
_MERMAID = re.compile(r"^```mermaid\r?\n(.*?)^```", re.DOTALL | re.MULTILINE)
_ANSWER = re.compile(r"<summary>\s*Answer\s*</summary>", re.IGNORECASE)

_yaml = YAML(typ="safe")


@dataclass(frozen=True)
class Chapter:
    path: Path
    meta: dict
    body: str

    @cached_property
    def word_count(self) -> int:
        return len(_FENCED.sub("", self.body).split())

    @cached_property
    def mcq_count(self) -> int:
        return len(_ANSWER.findall(self.body))

    @cached_property
    def mermaid_blocks(self) -> list[str]:
        return [block.strip() for block in _MERMAID.findall(self.body)]

    @cached_property
    def unverified_count(self) -> int:
        return self.body.count(UNVERIFIED_MARKER)


def parse_chapter(path: Path) -> Chapter:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER.match(text)
    if match is None:
        raise ValueError(f"{path} has no YAML front matter")
    meta = _yaml.load(match.group(1)) or {}
    return Chapter(path=path, meta=dict(meta), body=text[match.end():])


def chapter_filename(chapter_id: str, slug: str) -> str:
    return f"{chapter_id}-{slug}.md"
