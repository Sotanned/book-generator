import pytest

from next_chapter import BookFinished, build_manifest, main


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


def test_no_unwritten_chapters_raises_book_finished(book_dir):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    set_status(book_dir / "syllabus.yaml", "003", "drafted")
    with pytest.raises(BookFinished, match="no unwritten"):
        build_manifest(book_dir)


def test_main_exits_0_and_prints_manifest_on_success(book_dir, capsys):
    assert main([str(book_dir)]) == 0
    out = capsys.readouterr().out
    assert '"book_id"' in out


def test_main_exits_2_when_book_finished(book_dir, capsys):
    from bookgen.syllabus import set_status

    set_status(book_dir / "syllabus.yaml", "002", "drafted")
    set_status(book_dir / "syllabus.yaml", "003", "drafted")
    assert main([str(book_dir)]) == 2
    assert "no unwritten" in capsys.readouterr().err


def test_main_exits_3_on_missing_source(book_dir, capsys):
    (book_dir / "sources" / "guide.md").unlink()
    assert main([str(book_dir)]) == 3
    assert "guide.md" in capsys.readouterr().err


def test_main_exits_64_on_wrong_arg_count(capsys):
    assert main([]) == 64
    assert main(["a", "b"]) == 64
    assert "usage" in capsys.readouterr().err


def test_main_exits_1_and_not_2_on_malformed_syllabus(book_dir, capsys):
    path = book_dir / "syllabus.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace('book_id: test-book', ''),
        encoding="utf-8",
    )
    code = main([str(book_dir)])
    assert code == 1
    assert code != 2
    assert code != 3
    assert capsys.readouterr().err
