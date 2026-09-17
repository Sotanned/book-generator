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
