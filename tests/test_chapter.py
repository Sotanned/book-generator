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


def test_word_count_ignores_tilde_fenced_code(book_dir):
    base = build_chapter(words=2400, mermaid="")
    without = parse_chapter(write(book_dir, base, name="a.md")).word_count
    tilde_block = "\n~~~python\n" + " ".join(["word"] * 500) + "\n~~~\n"
    with_code = parse_chapter(write(book_dir, base + tilde_block, name="b.md")).word_count
    assert without == with_code


def test_counts_mcqs(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter(mcqs=5)))
    assert ch.mcq_count == 5


def test_counts_questions(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter(mcqs=4)))
    assert ch.question_count == 4


def test_question_and_answer_counts_can_disagree(book_dir):
    ch = parse_chapter(write(book_dir, build_chapter(mcqs=4, answers=3)))
    assert ch.question_count == 4
    assert ch.mcq_count == 3


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
