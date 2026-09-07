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
