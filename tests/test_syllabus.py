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
