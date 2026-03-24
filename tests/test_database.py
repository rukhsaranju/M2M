import os
import sqlite3
import pytest
from src import database
from src.database import (
    create_database,
    export_results,
    insert_entries,
    keyword_trend_over_time,
    keyword_frequency,
    search_entries,
    top_keywords,
    top_keywords_by_month,
    top_ngrams,
)

TEST_DB = "test_journal_entries.db"
def setup_function():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def teardown_function():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)



def test_create_database():
    create_database(TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries'")
    result = cursor.fetchone()
    conn.close()

    assert result is not None

def test_insert_entries():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Hello world"},
        {"timestamp": "Tuesday, January 02, 2024 at 11:00 AM", "entry": "Another entry"},
    ]

    insert_entries(entries, TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM entries")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 2

def test_no_duplicate_entries():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Hello world"},
    ]

    insert_entries(entries, TEST_DB)
    insert_entries(entries, TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM entries")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1

def test_search_entries():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Hello world. This is a test entry."},
        {"timestamp": "Tuesday, January 02, 2024 at 11:00 AM", "entry": "Another entry without the keyword."},
    ]

    insert_entries(entries, TEST_DB)

    results = search_entries("test", TEST_DB)
    assert len(results) == 1
    assert "This is a test entry." in results[0][2]

def test_search_entries_no_matches():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "I love python."},
    ]

    insert_entries(entries, TEST_DB)
    results = search_entries("java", TEST_DB)

    assert results == []


def test_search_entries_raises_when_database_missing():
    with pytest.raises(FileNotFoundError, match="Database not found"):
        search_entries("test", TEST_DB)

def test_keyword_frequency():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "apple apple banana"},
        {"timestamp": "Tuesday, January 02, 2024 at 11:00 AM", "entry": "banana orange"},
    ]

    insert_entries(entries, TEST_DB)
    result = keyword_frequency("banana", TEST_DB)

    assert result == "Frequency of 'banana': 2"

def test_keyword_frequency_case_insensitive():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Python python PYTHON"},
    ]

    insert_entries(entries, TEST_DB)
    result = keyword_frequency("python", TEST_DB)

    assert result == "Frequency of 'python': 3"


def test_keyword_frequency_raises_when_database_missing():
    with pytest.raises(FileNotFoundError, match="Database not found"):
        keyword_frequency("python", TEST_DB)


def test_keyword_trend_over_time_groups_counts_by_month():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Focus focus"},
        {"timestamp": "Wednesday, January 10, 2024 at 09:00 AM", "entry": "Focus energy focus"},
        {"timestamp": "Thursday, February 01, 2024 at 08:00 AM", "entry": "Focus"},
    ]

    insert_entries(entries, TEST_DB)
    results = keyword_trend_over_time("focus", TEST_DB)

    assert results == [("2024-01", 4), ("2024-02", 1)]


def test_keyword_trend_over_time_returns_chronological_months():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Friday, March 01, 2024 at 08:00 AM", "entry": "Calm"},
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Calm calm"},
        {"timestamp": "Thursday, February 01, 2024 at 08:00 AM", "entry": "Calm"},
    ]

    insert_entries(entries, TEST_DB)
    results = keyword_trend_over_time("calm", TEST_DB)

    assert results == [("2024-01", 2), ("2024-02", 1), ("2024-03", 1)]


def test_keyword_trend_over_time_raises_when_database_missing():
    with pytest.raises(FileNotFoundError, match="Database not found"):
        keyword_trend_over_time("focus", TEST_DB)


def test_top_keywords_returns_most_common_keywords():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Focus focus energy"},
        {"timestamp": "Tuesday, January 02, 2024 at 11:00 AM", "entry": "Energy focus clarity"},
    ]

    insert_entries(entries, TEST_DB)
    results = top_keywords(2, TEST_DB)

    assert results == [("focus", 3), ("energy", 2)]


def test_top_keywords_raises_when_count_not_positive():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Focus energy"},
    ]

    insert_entries(entries, TEST_DB)

    with pytest.raises(ValueError, match=r"Invalid number of keywords requested \(0\)"):
        top_keywords(0, TEST_DB)


def test_top_keywords_raises_when_request_exceeds_available_keywords():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Focus energy"},
    ]

    insert_entries(entries, TEST_DB)

    with pytest.raises(ValueError, match="Requested number of keywords \\(5\\) exceeds"):
        top_keywords(5, TEST_DB)


def test_top_keywords_raises_when_database_missing():
    with pytest.raises(FileNotFoundError, match="Database not found"):
        top_keywords(3, TEST_DB)


def test_top_keywords_by_month_returns_top_keywords_for_each_month():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Focus focus energy"},
        {"timestamp": "Wednesday, January 10, 2024 at 09:00 AM", "entry": "Energy calm focus"},
        {"timestamp": "Thursday, February 01, 2024 at 08:00 AM", "entry": "Calm calm energy"},
    ]

    insert_entries(entries, TEST_DB)
    results = top_keywords_by_month(2, TEST_DB)

    assert results == [
        ("2024-01", [("focus", 3), ("energy", 2)]),
        ("2024-02", [("calm", 2), ("energy", 1)]),
    ]


def test_top_keywords_by_month_raises_when_count_not_positive():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "Focus energy"},
    ]

    insert_entries(entries, TEST_DB)

    with pytest.raises(ValueError, match=r"Invalid number of keywords requested \(0\)"):
        top_keywords_by_month(0, TEST_DB)


def test_top_keywords_by_month_raises_when_database_missing():
    with pytest.raises(FileNotFoundError, match="Database not found"):
        top_keywords_by_month(2, TEST_DB)


def test_export_results_writes_top_keywords_by_month_format(tmp_path):
    output_file = tmp_path / "top_keywords_by_month.txt"
    results = [
        ("2024-01", [("focus", 3), ("energy", 2)]),
        ("2024-02", [("calm", 2)]),
    ]

    export_results(results, output_file)

    output_text = output_file.read_text()

    assert "Month: 2024-01" in output_text
    assert "Keyword: focus" in output_text
    assert "Frequency: 3" in output_text
    assert "Month: 2024-02" in output_text


def test_get_stopwords_raises_clear_error_when_corpus_missing(monkeypatch):
    database.get_stopwords.cache_clear()

    def raise_lookup_error(_language):
        raise LookupError("missing stopwords corpus")

    monkeypatch.setattr(database.stopwords, "words", raise_lookup_error)

    with pytest.raises(RuntimeError, match="NLTK stopwords corpus is not installed"):
        database.get_stopwords()

    database.get_stopwords.cache_clear()


def test_top_ngrams_raises_when_length_missing():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "good day good work"},
    ]

    insert_entries(entries, TEST_DB)
    with pytest.raises(ValueError, match="Please provide an n-gram length"):
        top_ngrams(5, None, TEST_DB)


def test_top_ngrams_raises_when_length_not_positive():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "good day good work"},
    ]

    insert_entries(entries, TEST_DB)
    with pytest.raises(ValueError, match=r"Invalid n-gram length requested \(0\)"):
        top_ngrams(5, 0, TEST_DB)


def test_top_ngrams_returns_most_common_phrases():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "good day good day"},
        {"timestamp": "Tuesday, January 02, 2024 at 11:00 AM", "entry": "good day bright light"},
    ]

    insert_entries(entries, TEST_DB)
    results = top_ngrams(2, 2, TEST_DB)

    assert results[0] == ("good day", 3)
    assert len(results) == 2


def test_top_ngrams_raises_when_count_not_positive():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "good day good work"},
    ]

    insert_entries(entries, TEST_DB)

    with pytest.raises(ValueError, match=r"Invalid number of phrases requested \(0\)"):
        top_ngrams(0, 2, TEST_DB)


def test_top_ngrams_raises_when_request_exceeds_available_phrases():
    create_database(TEST_DB)

    entries = [
        {"timestamp": "Monday, January 01, 2024 at 10:00 AM", "entry": "good day bright light"},
    ]

    insert_entries(entries, TEST_DB)

    with pytest.raises(ValueError, match="Requested number of phrases \\(10\\) exceeds"):
        top_ngrams(10, 2, TEST_DB)


def test_top_ngrams_raises_when_database_missing():
    with pytest.raises(FileNotFoundError, match="Database not found"):
        top_ngrams(3, 2, TEST_DB)
