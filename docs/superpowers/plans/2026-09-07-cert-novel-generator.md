# Story-Driven Certification Study Guide — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pipeline that turns a certification syllabus into a serialised LitRPG novel — one command writes the next chapter from grounded sources, validates it, commits it, and a static site serves it to a phone.

**Architecture:** Deterministic work lives in Python (resolve which chapter is next, gather its context, validate the result). Creative work lives in a Claude Code skill that calls those scripts around a prose-generation step. Content lives in `books/<book-id>/` as plain Markdown plus a YAML syllabus that doubles as the progress tracker. MkDocs Material renders the chapters.

**Tech Stack:** Python 3.13, pytest, ruamel.yaml (round-trip YAML that preserves the human comments in `syllabus.yaml`), MkDocs Material, Cloudflare Pages.

**Spec:** `docs/superpowers/specs/2026-09-07-story-driven-cert-guide-design.md`

## Global Constraints

- **Book id for this plan:** `databricks-de-associate`. All paths are `books/databricks-de-associate/...` unless stated otherwise.
- **Chapter length:** 2000–3000 words, measured after fenced code blocks are stripped.
- **MCQs per chapter:** 3–5, each with a collapsed answer.
- **Chapter status values:** exactly `unwritten`, `drafted`, `approved`. No others.
- **Ungrounded-claim marker:** the literal string `!!! warning "Unverified"` (MkDocs Material admonition).
- **One concept, one metaphor, permanently.** A concept appearing in `world/lexicon.md` maps to exactly one story element, and a story element to exactly one concept.
- **Chapter filenames:** `<id>-<slug>.md` where `<id>` is a zero-padded 3-digit string.
- **No API keys.** Generation runs on the Claude Code subscription. Nothing in this plan may introduce an `ANTHROPIC_API_KEY` dependency.
- **One story world per certification.** Do not create `books/aws-sa-pro/` content in this plan.
- **Encoding:** all file reads and writes pass `encoding="utf-8"` explicitly. The dev machine is Windows and defaults to cp1252, which will crash on the em dashes and arrows in generated prose.

---

## File Structure

| Path | Responsibility |
|---|---|
| `books/databricks-de-associate/sources/` | Ground truth documents. Read-only input. |
| `books/databricks-de-associate/syllabus.yaml` | Domains, chapter map, per-chapter status. The plan and the progress tracker. |
| `books/databricks-de-associate/world/bible.md` | Setting, cast, rules. Hand-authored. |
| `books/databricks-de-associate/world/lexicon.md` | Concept ↔ story-element table. Append-only. |
| `books/databricks-de-associate/world/continuity.md` | Append-only log of events per chapter. |
| `books/databricks-de-associate/chapters/` | Generated chapters. |
| `scripts/bookgen/syllabus.py` | Load/save `syllabus.yaml`; find next unwritten chapter; set status. |
| `scripts/bookgen/chapter.py` | Parse a chapter file into front matter + body; derive word count, MCQ count, Mermaid blocks. |
| `scripts/bookgen/lexicon.py` | Parse `lexicon.md`; detect metaphor drift. |
| `scripts/bookgen/checks.py` | All validation rules. Pure functions returning findings. |
| `scripts/check_book.py` | CLI wrapper over `checks.py`. Exit 1 on any error. |
| `scripts/next_chapter.py` | CLI that emits the JSON context manifest for the next unwritten chapter. |
| `.claude/skills/generate-next-chapter/SKILL.md` | The generation skill: calls the scripts, writes the prose. |
| `mkdocs.yml` | Site config. At repo root, not in `site/` — see Task 9. |
| `tests/` | pytest suite. |

---

## Task 1: Ground truth — the real exam guide and syllabus

The spec names this the first task: the domain weightings in the original blueprint (6/21/22/16/10/10/15) are **unverified**, and the live exam guide PDF is dated 25 July 2025, not 2026. Weightings decide how many chapters each domain gets, so everything downstream depends on getting this right. Do not guess them.

**Files:**
- Create: `books/databricks-de-associate/sources/exam-guide.pdf`
- Create: `books/databricks-de-associate/syllabus.yaml`
- Create: `.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces: `syllabus.yaml` conforming to the schema below. Every later task reads it.

- [ ] **Step 1: Locate the official exam guide**

Use WebSearch for `Databricks Certified Data Engineer Associate exam guide pdf site:databricks.com`. Do not guess a URL — follow a search result. Then WebFetch the PDF.

If it cannot be retrieved programmatically (Databricks sometimes gates these behind a form), stop and ask the user to download it manually and save it to `books/databricks-de-associate/sources/exam-guide.pdf`. Do not proceed on a guessed syllabus.

- [ ] **Step 2: Extract the real domains and weightings**

Read the PDF and write down, verbatim from the document:
- The guide revision date printed on it.
- Each domain's exact name.
- Each domain's exact percentage.
- The number of scored questions, time limit, and pass mark.

- [ ] **Step 3: Report the diff against the blueprint**

Show the user a table comparing the blueprint's assumed weightings to the actual ones:

| Domain | Assumed | Actual |
|---|---|---|

If they differ materially, say so plainly. This is the whole point of the task.

- [ ] **Step 4: Write `.gitignore`**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.venv/
_site/
```

- [ ] **Step 5: Write `syllabus.yaml`**

Allocate chapters proportionally to weight — roughly one chapter per 2.5% of the exam, so a 21% domain gets about 8 chapters and a 6% domain gets 2. Aim for 35–45 chapters total. Use the exact domain names and weights from Step 2.

Slugs and titles at this stage are **technical**, not story titles (`unity-catalog-namespace`, not `the-guild-registry`). Task 7 renames them once the world exists — the story cannot be named before it is invented.

`sources` lists only files that exist. At this stage that is `sources/exam-guide.pdf` for every chapter; Task 8 onward can add product docs.

```yaml
book_id: databricks-de-associate
title: "TBD - named in Task 7"
world: world/bible.md
exam:
  name: "Databricks Certified Data Engineer Associate"
  guide_version: "2025-07-25"   # replace with the date printed on the PDF
  questions: 45
  duration_minutes: 90
  pass_mark: 0.70

domains:
  - id: D1
    name: "Databricks Intelligence Platform"   # exact name from the PDF
    weight: 0.06                               # exact weight from the PDF
    chapters:
      - id: "001"
        slug: unity-catalog-namespace
        title: "Unity Catalog Namespace"
        topics:
          - "three-level namespace: catalog.schema.table"
          - "metastore vs catalog vs schema"
        sources:
          - sources/exam-guide.pdf
        status: unwritten
```

The `title: "TBD - named in Task 7"` at the top level is the one intentional placeholder in this repo, and Task 7 removes it. Chapter titles must be real.

- [ ] **Step 6: Commit**

```bash
git add .gitignore books/databricks-de-associate/
git commit -m "feat: add verified Databricks DE Associate syllabus and exam guide source"
```

---

## Task 2: Python scaffolding and the syllabus module

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `scripts/bookgen/__init__.py`
- Create: `scripts/bookgen/syllabus.py`
- Test: `tests/conftest.py`, `tests/test_syllabus.py`

**Interfaces:**
- Consumes: `syllabus.yaml` from Task 1.
- Produces:
  - `ChapterEntry(id: str, slug: str, title: str, domain_id: str, topics: list[str], sources: list[str], status: str)`
  - `Domain(id: str, name: str, weight: float, chapters: list[ChapterEntry])`
  - `Syllabus(book_id, title, world, exam: dict, domains: list[Domain], path: Path)` with methods `chapters() -> list[ChapterEntry]`, `next_unwritten() -> ChapterEntry | None`, `find(chapter_id: str) -> ChapterEntry | None`
  - `load_syllabus(path: Path) -> Syllabus`
  - `set_status(path: Path, chapter_id: str, status: str) -> None`
  - `VALID_STATUSES: frozenset[str]`

- [ ] **Step 1: Create `requirements.txt` and `pytest.ini`**

`requirements.txt`:
```
ruamel.yaml>=0.18
pytest>=8.0
mkdocs-material>=9.5
```

`pytest.ini`:
```ini
[pytest]
testpaths = tests
pythonpath = scripts
```

`pythonpath = scripts` is what makes `import bookgen` work without packaging the project.

Install: `pip install -r requirements.txt`

- [ ] **Step 2: Write `tests/conftest.py`**

```python
import textwrap
from pathlib import Path

import pytest

MINIMAL_SYLLABUS = textwrap.dedent("""\
    book_id: test-book
    title: "Test Book"
    world: world/bible.md
    exam:
      name: "Test Exam"
      guide_version: "2025-07-25"
      questions: 45
      duration_minutes: 90
      pass_mark: 0.70
    domains:
      - id: D1
        name: "First Domain"
        weight: 0.6      # provisional
        chapters:
          - id: "001"
            slug: first-chapter
            title: "First Chapter"
            topics: ["topic one"]
            sources: ["sources/guide.md"]
            status: drafted
          - id: "002"
            slug: second-chapter
            title: "Second Chapter"
            topics: ["topic two"]
            sources: ["sources/guide.md"]
            status: unwritten
      - id: D2
        name: "Second Domain"
        weight: 0.4
        chapters:
          - id: "003"
            slug: third-chapter
            title: "Third Chapter"
            topics: ["topic three"]
            sources: ["sources/guide.md"]
            status: unwritten
    """)


def build_chapter(
    *,
    chapter_id="002",
    title="Second Chapter",
    domain="D1",
    topics=("topic two",),
    sources=("sources/guide.md",),
    status="drafted",
    words=2400,
    mcqs=4,
    mermaid="flowchart TD\n  A --> B",
) -> str:
    """Build chapter file text. Defaults produce a chapter that passes every check."""
    front = textwrap.dedent(f"""\
        ---
        chapter: "{chapter_id}"
        title: "{title}"
        domain: {domain}
        topics: {list(topics)}
        sources: {list(sources)}
        status: {status}
        generated: 2026-09-08
        ---
        """)
    prose = " ".join(["word"] * words)
    diagram = f"\n```mermaid\n{mermaid}\n```\n" if mermaid else ""
    questions = "".join(
        f"\n**Q{i + 1}.** Question text?\n\n"
        "- A. one\n- B. two\n- C. three\n- D. four\n\n"
        "<details><summary>Answer</summary>\n\nB. two\n\n</details>\n"
        for i in range(mcqs)
    )
    return f"{front}\n{prose}\n{diagram}{questions}"


LEXICON = textwrap.dedent("""\
    # Lexicon

    | Concept | Story element | First appears |
    |---|---|---|
    | Unity Catalog | The Guild Registry | 001 |
    | Auto Loader | The Gate Warden | 002 |
    """)


@pytest.fixture
def book_dir(tmp_path: Path) -> Path:
    """A minimal valid book: syllabus, one source, world files, one drafted chapter."""
    book = tmp_path / "books" / "test-book"
    (book / "sources").mkdir(parents=True)
    (book / "world").mkdir()
    (book / "chapters").mkdir()
    (book / "syllabus.yaml").write_text(MINIMAL_SYLLABUS, encoding="utf-8")
    (book / "sources" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (book / "world" / "bible.md").write_text("# Bible\n", encoding="utf-8")
    (book / "world" / "lexicon.md").write_text(LEXICON, encoding="utf-8")
    (book / "world" / "continuity.md").write_text("# Continuity\n", encoding="utf-8")
    (book / "chapters" / "001-first-chapter.md").write_text(
        build_chapter(chapter_id="001", title="First Chapter"), encoding="utf-8"
    )
    return book
```

- [ ] **Step 3: Write the failing tests**

`tests/test_syllabus.py`:
```python
import pytest

from bookgen.syllabus import load_syllabus, set_status


def test_loads_book_metadata(book_dir):
    syl = load_syllabus(book_dir / "syllabus.yaml")
    assert syl.book_id == "test-book"
    assert syl.exam["questions"] == 45
    assert len(syl.domains) == 2


def test_chapters_are_flattened_in_document_order(book_dir):
    syl = load_syllabus(book_dir / "syllabus.yaml")
    assert [c.id for c in syl.chapters()] == ["001", "002", "003"]


def test_chapter_carries_its_domain_id(book_dir):
    syl = load_syllabus(book_dir / "syllabus.yaml")
    assert syl.find("003").domain_id == "D2"


def test_next_unwritten_returns_first_in_document_order(book_dir):
    syl = load_syllabus(book_dir / "syllabus.yaml")
    assert syl.next_unwritten().id == "002"


def test_next_unwritten_is_none_when_all_written(book_dir):
    path = book_dir / "syllabus.yaml"
    set_status(path, "002", "drafted")
    set_status(path, "003", "approved")
    assert load_syllabus(path).next_unwritten() is None


def test_set_status_persists(book_dir):
    path = book_dir / "syllabus.yaml"
    set_status(path, "002", "drafted")
    assert load_syllabus(path).find("002").status == "drafted"


def test_set_status_preserves_comments(book_dir):
    path = book_dir / "syllabus.yaml"
    set_status(path, "002", "drafted")
    assert "# provisional" in path.read_text(encoding="utf-8")


def test_set_status_rejects_unknown_status(book_dir):
    with pytest.raises(ValueError, match="unknown status"):
        set_status(book_dir / "syllabus.yaml", "002", "done")


def test_set_status_rejects_unknown_chapter(book_dir):
    with pytest.raises(KeyError, match="999"):
        set_status(book_dir / "syllabus.yaml", "999", "drafted")
```

The comment-preservation test is the reason for ruamel.yaml: `syllabus.yaml` is hand-edited and carries `# provisional` markers on the weightings. PyYAML would silently delete them on every write.

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/test_syllabus.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bookgen'`

- [ ] **Step 5: Implement `scripts/bookgen/syllabus.py`**

Create an empty `scripts/bookgen/__init__.py`, then:

```python
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
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_syllabus.py -v`
Expected: PASS (9 tests)

- [ ] **Step 7: Commit**

```bash
git add requirements.txt pytest.ini scripts/bookgen/ tests/conftest.py tests/test_syllabus.py
git commit -m "feat: add syllabus loader with comment-preserving status updates"
```

---

## Task 3: Chapter parsing

**Files:**
- Create: `scripts/bookgen/chapter.py`
- Test: `tests/test_chapter.py`

**Interfaces:**
- Consumes: `build_chapter` from `tests/conftest.py`.
- Produces:
  - `Chapter(path: Path, meta: dict, body: str)` with properties `word_count: int`, `mcq_count: int`, `mermaid_blocks: list[str]`, `unverified_count: int`
  - `parse_chapter(path: Path) -> Chapter`
  - `chapter_filename(chapter_id: str, slug: str) -> str`
  - `MIN_WORDS = 2000`, `MAX_WORDS = 3000`, `MIN_MCQS = 3`, `MAX_MCQS = 5`
  - `UNVERIFIED_MARKER = '!!! warning "Unverified"'`

- [ ] **Step 1: Write the failing tests**

`tests/test_chapter.py`:
```python
import pytest

from bookgen.chapter import (
    UNVERIFIED_MARKER,
    chapter_filename,
    parse_chapter,
)
from conftest import build_chapter


def write(book_dir, text, name="002-second-chapter.md"):
    path = book_dir / "chapters" / name
    path.write_text(text, encoding="utf-8")
    return path


def test_parses_front_matter(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter()))
    assert ch.meta["chapter"] == "002"
    assert ch.meta["domain"] == "D1"
    assert ch.meta["sources"] == ["sources/guide.md"]


def test_body_excludes_front_matter(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter()))
    assert "chapter:" not in ch.body


def test_word_count_ignores_fenced_code(book_dir):
    without = parse_chapter(write(book_dir, build_chapter(words=2400, mermaid=""))).word_count
    with_code = parse_chapter(write(book_dir, build_chapter(words=2400))).word_count
    assert without == with_code


def test_counts_mcqs(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter(mcqs=5)))
    assert ch.mcq_count == 5


def test_collects_mermaid_blocks(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter()))
    assert len(ch.mermaid_blocks) == 1
    assert ch.mermaid_blocks[0].startswith("flowchart TD")


def test_no_mermaid_is_allowed(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter(mermaid="")))
    assert ch.mermaid_blocks == []


def test_counts_unverified_markers(book_dir):
    text = build_chapter() + f'\n{UNVERIFIED_MARKER}\n    No source found.\n'
    ch = parse_chapter(write(book_dir, text))
    assert ch.unverified_count == 1


def test_missing_front_matter_raises(book_dir):
    with pytest.raises(ValueError, match="front matter"):
        parse_chapter(write(book_dir, "no front matter here\n"))


def test_chapter_filename():
    assert chapter_filename("001", "the-guild-registry") == "001-the-guild-registry.md"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chapter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bookgen.chapter'`

- [ ] **Step 3: Implement `scripts/bookgen/chapter.py`**

```python
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
```

`cached_property` requires the dataclass to not be `slots=True`; it is not. It works on frozen dataclasses because it writes through `__dict__`, which frozen dataclasses still have.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chapter.py -v`
Expected: PASS (9 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/bookgen/chapter.py tests/test_chapter.py
git commit -m "feat: add chapter front matter and body parsing"
```

---

## Task 4: Lexicon parsing and metaphor drift detection

This is the module that keeps a forty-chapter generated novel coherent. If Auto Loader is "the Gate Warden" in chapter 3 and "the Herald of Arrivals" in chapter 9, the metaphor stops aiding recall and the book fails at its only job.

**Files:**
- Create: `scripts/bookgen/lexicon.py`
- Test: `tests/test_lexicon.py`

**Interfaces:**
- Consumes: `world/lexicon.md`.
- Produces:
  - `LexiconEntry(concept: str, story_element: str, first_appears: str)`
  - `parse_lexicon(path: Path) -> list[LexiconEntry]`
  - `find_drift(entries: list[LexiconEntry]) -> list[str]` returning human-readable drift descriptions

- [ ] **Step 1: Write the failing tests**

`tests/test_lexicon.py`:
```python
import textwrap

from bookgen.lexicon import LexiconEntry, find_drift, parse_lexicon


def write_lexicon(book_dir, rows):
    body = textwrap.dedent("""\
        # Lexicon

        | Concept | Story element | First appears |
        |---|---|---|
        """) + "".join(f"| {c} | {s} | {a} |\n" for c, s, a in rows)
    path = book_dir / "world" / "lexicon.md"
    path.write_text(body, encoding="utf-8")
    return path


def test_parses_rows(book_dir):
    path = write_lexicon(book_dir, [("Unity Catalog", "The Guild Registry", "001")])
    assert parse_lexicon(path) == [LexiconEntry("Unity Catalog", "The Guild Registry", "001")]


def test_skips_header_and_separator(book_dir):
    path = write_lexicon(book_dir, [("A", "B", "001"), ("C", "D", "002")])
    assert len(parse_lexicon(path)) == 2


def test_missing_file_is_empty(book_dir):
    assert parse_lexicon(book_dir / "world" / "nope.md") == []


def test_no_drift_when_mapping_is_one_to_one():
    entries = [
        LexiconEntry("Unity Catalog", "The Guild Registry", "001"),
        LexiconEntry("Auto Loader", "The Gate Warden", "002"),
    ]
    assert find_drift(entries) == []


def test_detects_one_concept_with_two_elements():
    entries = [
        LexiconEntry("Auto Loader", "The Gate Warden", "002"),
        LexiconEntry("Auto Loader", "The Herald of Arrivals", "009"),
    ]
    drift = find_drift(entries)
    assert len(drift) == 1
    assert "Auto Loader" in drift[0]
    assert "The Herald of Arrivals" in drift[0]


def test_detects_one_element_reused_for_two_concepts():
    entries = [
        LexiconEntry("Auto Loader", "The Gate Warden", "002"),
        LexiconEntry("COPY INTO", "The Gate Warden", "004"),
    ]
    drift = find_drift(entries)
    assert len(drift) == 1
    assert "The Gate Warden" in drift[0]


def test_exact_duplicate_row_is_not_drift():
    entries = [
        LexiconEntry("Auto Loader", "The Gate Warden", "002"),
        LexiconEntry("Auto Loader", "The Gate Warden", "002"),
    ]
    assert find_drift(entries) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_lexicon.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bookgen.lexicon'`

- [ ] **Step 3: Implement `scripts/bookgen/lexicon.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_lexicon.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/bookgen/lexicon.py tests/test_lexicon.py
git commit -m "feat: add lexicon parsing with metaphor drift detection"
```

---

## Task 5: Validation rules and the `check_book` CLI

**Files:**
- Create: `scripts/bookgen/checks.py`
- Create: `scripts/check_book.py`
- Test: `tests/test_checks.py`

**Interfaces:**
- Consumes: `syllabus.py`, `chapter.py`, `lexicon.py`.
- Produces:
  - `Finding(where: str, message: str)`
  - `check_book(book_dir: Path) -> list[Finding]`
  - `MERMAID_TYPES: frozenset[str]`

**Scope note on Mermaid:** the spec says Mermaid blocks must "parse". Real parsing needs the Node-based `mermaid-cli`, which would drag a Node toolchain into a Python project for one check. This validates instead that each block declares a recognised diagram type on its first line — which catches the realistic failure (a model emitting prose or a non-diagram inside a ```mermaid fence) without the dependency. If genuinely broken diagram syntax shows up in practice, add `mermaid-cli` then.

- [ ] **Step 1: Write the failing tests**

`tests/test_checks.py`:
```python
from bookgen.checks import check_book
from conftest import build_chapter


def messages(findings):
    return " | ".join(f.message for f in findings)


def write_ch2(book_dir, **kwargs):
    kwargs.setdefault("chapter_id", "002")
    kwargs.setdefault("title", "Second Chapter")
    (book_dir / "chapters" / "002-second-chapter.md").write_text(
        build_chapter(**kwargs), encoding="utf-8"
    )


def test_clean_book_has_no_findings(book_dir):
    assert check_book(book_dir) == []


def test_unwritten_chapters_are_not_checked(book_dir):
    # 002 and 003 are unwritten and have no files; that is not an error
    assert check_book(book_dir) == []


def test_drafted_chapter_without_a_file_is_an_error(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    assert "missing chapter file" in messages(check_book(book_dir))


def test_short_chapter_is_an_error(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    write_ch2(book_dir, words=500)
    assert "word count" in messages(check_book(book_dir))


def test_long_chapter_is_an_error(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    write_ch2(book_dir, words=5000)
    assert "word count" in messages(check_book(book_dir))


def test_too_few_mcqs_is_an_error(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    write_ch2(book_dir, mcqs=1)
    assert "MCQ count" in messages(check_book(book_dir))


def test_front_matter_domain_must_match_syllabus(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    write_ch2(book_dir, domain="D9")
    assert "domain" in messages(check_book(book_dir))


def test_unknown_mermaid_type_is_an_error(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    write_ch2(book_dir, mermaid="Here is a diagram of the guild.")
    assert "mermaid" in messages(check_book(book_dir))


def test_missing_source_file_is_an_error(book_dir):
    (book_dir / "sources" / "guide.md").unlink()
    assert "missing source" in messages(check_book(book_dir))


def test_duplicate_chapter_ids_are_an_error(book_dir):
    path = book_dir / "syllabus.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace('id: "003"', 'id: "002"'), encoding="utf-8"
    )
    assert "duplicate chapter id" in messages(check_book(book_dir))


def test_lexicon_drift_is_an_error(book_dir):
    lex = book_dir / "world" / "lexicon.md"
    lex.write_text(
        lex.read_text(encoding="utf-8") + "| Auto Loader | The Herald | 009 |\n",
        encoding="utf-8",
    )
    assert "Auto Loader" in messages(check_book(book_dir))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_checks.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bookgen.checks'`

- [ ] **Step 3: Implement `scripts/bookgen/checks.py`**

```python
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
    if not MIN_WORDS <= chapter.word_count <= MAX_WORDS:
        findings.append(
            Finding(where, f"word count {chapter.word_count} outside {MIN_WORDS}-{MAX_WORDS}")
        )
    if not MIN_MCQS <= chapter.mcq_count <= MAX_MCQS:
        findings.append(
            Finding(where, f"MCQ count {chapter.mcq_count} outside {MIN_MCQS}-{MAX_MCQS}")
        )
    for block in chapter.mermaid_blocks:
        first_token = block.split()[0] if block.split() else ""
        if first_token not in MERMAID_TYPES:
            findings.append(
                Finding(where, f"mermaid block declares unknown diagram type {first_token!r}")
            )
    return findings


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_checks.py -v`
Expected: PASS (11 tests)

- [ ] **Step 5: Write `scripts/check_book.py`**

```python
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
```

- [ ] **Step 6: Run it against the real book**

Run: `python scripts/check_book.py`
Expected: `OK    databricks-de-associate` — every chapter is still `unwritten`, so only source existence and id uniqueness are checked. If it reports a missing source, Task 1's `syllabus.yaml` references a file that was never downloaded; fix the syllabus, not the checker.

- [ ] **Step 7: Commit**

```bash
git add scripts/bookgen/checks.py scripts/check_book.py tests/test_checks.py
git commit -m "feat: add structural book validation and check_book CLI"
```

---

## Task 6: The `next_chapter` context resolver

The generation skill must not decide for itself what to write or which files to read — that is exactly where a model drifts. This script makes the decision deterministically and hands back a manifest.

**Files:**
- Create: `scripts/next_chapter.py`
- Test: `tests/test_next_chapter.py`

**Interfaces:**
- Consumes: `syllabus.py`, `chapter.py`.
- Produces: `build_manifest(book_dir: Path) -> dict` and a CLI printing that dict as JSON.

Manifest shape:
```json
{
  "book_id": "test-book",
  "book_dir": "books/test-book",
  "chapter": {"id": "002", "slug": "second-chapter", "title": "Second Chapter",
              "domain_id": "D1", "domain_name": "First Domain",
              "topics": ["topic two"], "status": "unwritten"},
  "output_path": "books/test-book/chapters/002-second-chapter.md",
  "context_files": ["books/test-book/world/bible.md",
                    "books/test-book/world/lexicon.md",
                    "books/test-book/world/continuity.md",
                    "books/test-book/sources/guide.md",
                    "books/test-book/chapters/001-first-chapter.md"],
  "previous_chapter": "books/test-book/chapters/001-first-chapter.md"
}
```

- [ ] **Step 1: Write the failing tests**

`tests/test_next_chapter.py`:
```python
import pytest

from next_chapter import build_manifest


def test_selects_first_unwritten_chapter(book_dir):
    manifest = build_manifest(book_dir)
    assert manifest["chapter"]["id"] == "002"
    assert manifest["chapter"]["domain_name"] == "First Domain"


def test_output_path_matches_id_and_slug(book_dir):
    manifest = build_manifest(book_dir)
    assert manifest["output_path"].endswith("chapters/002-second-chapter.md")


def test_context_includes_world_sources_and_previous_chapter(book_dir):
    files = build_manifest(book_dir)["context_files"]
    assert any(f.endswith("world/bible.md") for f in files)
    assert any(f.endswith("world/lexicon.md") for f in files)
    assert any(f.endswith("world/continuity.md") for f in files)
    assert any(f.endswith("sources/guide.md") for f in files)
    assert any(f.endswith("001-first-chapter.md") for f in files)


def test_previous_chapter_is_none_for_first_chapter(book_dir):
    from bookgen.syllabus import set_status

    # make 001 unwritten again and delete its file
    set_status(book_dir / "syllabus.yaml", "001", "unwritten")
    (book_dir / "chapters" / "001-first-chapter.md").unlink()
    manifest = build_manifest(book_dir)
    assert manifest["chapter"]["id"] == "001"
    assert manifest["previous_chapter"] is None


def test_missing_source_aborts(book_dir):
    (book_dir / "sources" / "guide.md").unlink()
    with pytest.raises(FileNotFoundError, match="guide.md"):
        build_manifest(book_dir)


def test_no_unwritten_chapters_raises_lookup_error(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    set_status(book_dir / "syllabus.yaml", "003", "drafted")
    with pytest.raises(LookupError, match="no unwritten"):
        build_manifest(book_dir)
```

`test_missing_source_aborts` encodes a spec requirement: writing an ungrounded chapter is worse than writing none, so a missing source aborts *before* generation rather than producing prose from model memory.

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_next_chapter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'next_chapter'`

- [ ] **Step 3: Implement `scripts/next_chapter.py`**

```python
"""Resolve the next unwritten chapter and the exact context needed to write it.

Usage:
    python scripts/next_chapter.py databricks-de-associate
Prints a JSON manifest. Exits 2 when the book is finished, 3 on a missing source.
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


def build_manifest(book_dir: Path) -> dict:
    book_dir = Path(book_dir)
    syllabus = load_syllabus(book_dir / "syllabus.yaml")

    entry = syllabus.next_unwritten()
    if entry is None:
        raise LookupError(f"no unwritten chapters left in {syllabus.book_id}")

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
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_next_chapter.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Run the whole suite**

Run: `pytest -v`
Expected: PASS (42 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/next_chapter.py tests/test_next_chapter.py
git commit -m "feat: add next-chapter context manifest resolver"
```

---

## Task 7: The world bible, lexicon, and continuity ledger

**This task is a conversation with the user, not a generation run.** The spec is explicit: the world bible "decides whether the book is enjoyable, so it is not generated." Draft it, show it, revise it. Do not proceed to Task 8 until the user says they like the premise.

**Files:**
- Create: `books/databricks-de-associate/world/bible.md`
- Create: `books/databricks-de-associate/world/lexicon.md`
- Create: `books/databricks-de-associate/world/continuity.md`
- Modify: `books/databricks-de-associate/syllabus.yaml` (top-level `title`, and every chapter `slug`/`title`)

**Interfaces:**
- Consumes: `syllabus.yaml` domain and topic list from Task 1.
- Produces: `world/lexicon.md` as a three-column Markdown table with header `| Concept | Story element | First appears |`, which `bookgen.lexicon.parse_lexicon` requires. Any other table shape parses to nothing.

- [ ] **Step 1: Draft `world/bible.md`**

Cover, in this order:
- **Premise** — one paragraph. A LitRPG dungeon-guild setting, since that is the direction the user picked.
- **Protagonist** — name, why they are at the guild, what they want. The reader follows this person for forty chapters.
- **Supporting cast** — three to five recurring characters, each mapped to a role that recurs in the material (the archivist who runs the registry, the warden at the gate, and so on).
- **Rules of the world** — what magic/technology can and cannot do. These rules must be isomorphic to the real constraints of the platform, because that isomorphism is the teaching mechanism. When the story says a ward cannot be placed on a single row without naming the row's guild, that must correspond to something true about row-level security.
- **Arc** — how the seven domains map onto a rising narrative. Foundations early, orchestration in the middle, governance and troubleshooting late.
- **Voice** — target register, chapter rhythm, how the status windows read.

- [ ] **Step 2: Seed `world/lexicon.md`**

Header exactly as below — the parser requires three columns:

```markdown
# Lexicon

One concept, one story element, permanently. Appending a second element for an
existing concept is drift and `check_book.py` will fail the build.

| Concept | Story element | First appears |
|---|---|---|
| Unity Catalog | The Guild Registry | 001 |
```

Seed only the concepts that appear in the bible. The generator appends the rest as it writes.

- [ ] **Step 3: Create `world/continuity.md`**

```markdown
# Continuity Ledger

Append two or three lines per chapter: characters introduced, world rules
established, threads left open. Newest last.
```

- [ ] **Step 4: Rename the syllabus chapters to story titles**

Replace the technical slugs from Task 1 with story titles drawn from the bible, and set the top-level `title`. `unity-catalog-namespace` becomes `the-guild-registry`; `title: "TBD - named in Task 8"` becomes the book's real name.

- [ ] **Step 5: Show the user and wait**

Present the premise, the protagonist, and three sample chapter titles. Ask directly whether this is a book they want to read on a train. Revise until yes. Do not continue on silence.

- [ ] **Step 6: Validate and commit**

```bash
python scripts/check_book.py databricks-de-associate
git add books/databricks-de-associate/
git commit -m "feat: add world bible, lexicon, and continuity ledger"
```

Expected: `OK    databricks-de-associate`

---

## Task 8: The `generate-next-chapter` skill

**Files:**
- Create: `.claude/skills/generate-next-chapter/SKILL.md`

**Interfaces:**
- Consumes: `scripts/next_chapter.py`, `scripts/check_book.py`, the world files from Task 7.
- Produces: a chapter file, appended lexicon and continuity entries, and `status: drafted` in the syllabus.

- [ ] **Step 1: Write the skill**

````markdown
---
name: generate-next-chapter
description: Use when writing the next chapter of a certification study novel in this repo, or when the user says "generate the next chapter" or "write chapter N"
---

# Generate Next Chapter

Write one chapter of a certification study novel, grounded in the book's sources.

## Steps

1. **Resolve the target.**

   ```bash
   python scripts/next_chapter.py <book-id>
   ```

   - Exit 2 means every chapter is written. Say so and stop. This is not an error.
   - Exit 3 means a source file is missing. Stop and report it. Never write a
     chapter whose sources are absent — an ungrounded chapter is worse than no
     chapter.

2. **Read every file in `context_files`.** All of them, before writing anything.
   `bible.md` sets voice and cast, `lexicon.md` fixes the metaphors you must reuse,
   `continuity.md` says what has already happened, the sources are your ground
   truth, and the previous chapter sets the rhythm you are continuing.

3. **Write the chapter** to `output_path`, in this shape:

   ```markdown
   ---
   chapter: "<id from manifest>"
   title: "<title from manifest>"
   domain: <domain_id from manifest>
   topics: <topics from manifest>
   sources: <the chapter's sources>
   status: drafted
   generated: <today's date, YYYY-MM-DD>
   ---
   ```

   Then five sections:

   - **Cold open** — a problem the characters face. Story, not exposition.
   - **The mechanism** — the story resolves, and the technical concept is the
     resolution. Exact syntax, real option names, and actual error text appear as
     story artifacts: a scroll, a ward inscription, a warden's complaint. These
     details are what the exam tests, so they must be exact, not paraphrased.
   - **Diagram** — a Mermaid block, but only if the concept is genuinely
     structural. A decorative diagram is noise. Skipping it is fine and valid.
   - **Status Window** — a boxed cheat sheet in LitRPG style. This is the revision
     surface, re-read the morning of the exam. Dense and scannable.
   - **Field Test** — 3 to 5 exam-style MCQs. Each is a question, options A-D, then:

     ```markdown
     <details><summary>Answer</summary>

     B. Because ...

     </details>
     ```

   Target 2000-3000 words, excluding code blocks.

4. **Ground every technical claim in the sources.** Where you cannot, mark it:

   ```markdown
   !!! warning "Unverified"
       No source in this book confirms the default value of `maxFilesPerTrigger`.
   ```

   Use the marker honestly. It is cheap, and it is the only accuracy mechanism
   this pipeline has. A chapter with three honest markers is more useful than one
   with none and a fabrication.

5. **Reuse metaphors; never invent a second one.** If `lexicon.md` maps a concept
   to a story element, use that element. When you introduce a genuinely new
   concept, append one row to `lexicon.md`. Never add a second row for a concept
   that already has one — `check_book.py` fails on drift.

6. **Append to `continuity.md`**: two or three lines — characters introduced,
   world rules established, threads left open.

7. **Validate.**

   ```bash
   python scripts/check_book.py <book-id>
   ```

   If it fails, fix the chapter and re-run. Do not edit the checker to pass, and
   do not commit a failing chapter.

8. **Mark it drafted**, only after validation passes:

   ```bash
   python -c "import sys; sys.path.insert(0,'scripts'); from bookgen.syllabus import set_status; set_status('books/<book-id>/syllabus.yaml','<id>','drafted')"
   ```

   The file is written before the syllabus is updated, so an interrupted run
   leaves the chapter `unwritten` and simply retries next time.

9. **Commit and push.**

   ```bash
   git add books/<book-id>/
   git commit -m "content: chapter <id> - <title>"
   git push
   ```

## Do not

- Write from memory when a source exists. Read the source.
- Invent Databricks behaviour to make a scene work. Mark it unverified instead.
- Generate more than one chapter per run.
- Skip validation.
````

- [ ] **Step 2: Generate chapter 001**

Invoke the skill. Read the output yourself before showing the user — if the prose is obviously bad, the prompt needs work, not the user's time.

- [ ] **Step 3: Verify the mechanics worked**

Run: `python scripts/check_book.py databricks-de-associate`
Expected: `OK    databricks-de-associate`

Then confirm by inspection:
- `syllabus.yaml` shows `status: drafted` for chapter 001 and comments are intact.
- `continuity.md` gained entries.
- `lexicon.md` gained rows, with no concept listed twice.

- [ ] **Step 4: Have the user read it**

This is the real gate. Ask specifically: is the voice right, is the density right, would you read chapter 2? Feed the answer back into the skill's prompt. **Expect to revise the skill here** — this is the step the whole plan exists to reach.

- [ ] **Step 5: Generate chapters 002 and 003, revising the prompt between each**

Three chapters is enough to see whether the voice holds and whether continuity is actually being carried forward. Do not automate before this.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/generate-next-chapter/SKILL.md books/databricks-de-associate/
git commit -m "feat: add chapter generation skill and first three chapters"
```

---

## Task 9: MkDocs site and Cloudflare Pages deploy

**Files:**
- Create: `mkdocs.yml`
- Create: `books/databricks-de-associate/index.md`
- (`.gitignore` already excludes `_site/` from Task 1; no change needed.)

**Interfaces:**
- Consumes: `books/*/chapters/*.md`.
- Produces: a static site in `_site/`.

**Deviation from the spec:** the spec put site config in `site/`. MkDocs' default `site_dir` is also `site/`, so the config directory and the build output would collide. `mkdocs.yml` therefore lives at the repo root — which is also the only place `docs_dir: books` resolves cleanly — and the build output goes to `_site/`, gitignored.

- [ ] **Step 1: Write `mkdocs.yml`**

```yaml
site_name: Certification Novels
site_dir: _site
docs_dir: books
use_directory_urls: true

exclude_docs: |
  */sources/*
  */world/*

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.top
    - content.code.copy
    - search.suggest

markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format

plugins:
  - search
```

`admonition` renders the `!!! warning "Unverified"` markers. `pymdownx.details` renders the collapsed `<details>` answer blocks. The `superfences` custom fence is what turns ```mermaid blocks into diagrams.

- [ ] **Step 2: Write the book landing page**

`books/databricks-de-associate/index.md`:
```markdown
# <book title from syllabus.yaml>

A story-driven guide to the Databricks Certified Data Engineer Associate exam.

Chapters are listed in the navigation, in reading order.
```

- [ ] **Step 3: Build and check locally**

Run: `mkdocs serve`
Then open the local URL and verify:
- Chapters appear in the nav; `sources/` and `world/` do **not**.
- The Mermaid diagram in chapter 001 renders as a diagram, not as code.
- A Field Test answer block expands when clicked.
- Any `!!! warning "Unverified"` renders as a warning box.
- The page is readable at phone width (narrow the browser).

If Mermaid does not render, the `superfences` custom fence is misconfigured — that is the first thing to check.

- [ ] **Step 4: Configure Cloudflare Pages**

In the Cloudflare dashboard, connect the GitHub repo with:
- Build command: `pip install -r requirements.txt && mkdocs build`
- Build output directory: `_site`
- Python version: set the `PYTHON_VERSION` environment variable to `3.13`

- [ ] **Step 5: Verify the deploy on a phone**

Push, wait for the build, open the site on the phone. This is the acceptance test for the entire plan: a chapter, readable on a train.

- [ ] **Step 6: Commit**

```bash
git add mkdocs.yml books/databricks-de-associate/index.md
git commit -m "feat: add MkDocs Material site with Mermaid and admonition support"
git push
```

---

## Out of scope for this plan

Phases 4 and 5 of the spec, deliberately:

- **Scheduled automation.** Set up only once the prompt reliably produces chapters worth keeping — which is a judgement the user makes after reading a few. The `generate-next-chapter` skill is already the single entry point any scheduler would call, so this is later a configuration step, not a rewrite.
- **A second book.** `books/aws-sa-pro/` stays empty until book one is done. AWS SA Pro tests scenario and cost tradeoffs rather than syntax nuance, so its chapter template will differ — and writing book one is what reveals how.
