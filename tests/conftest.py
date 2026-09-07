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
