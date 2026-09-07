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
