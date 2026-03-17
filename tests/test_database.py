import os
import sqlite3
import pytest
from src.database import create_database, insert_entries, search_entries, keyword_frequency

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
