from src.journal_parser import create_entries

def test_parser_creates_entries():
    sample_text = """
Monday, January 01, 2024 at 10:00 AM
First journal entry.

Tuesday, January 02, 2024 at 11:00 AM
Second journal entry.
"""
    entries = create_entries(sample_text)
    assert len(entries) == 2
    assert entries[0]["timestamp"] == "Monday, January 01, 2024 at 10:00 AM"
    assert entries[0]["entry"] == "First journal entry."
    assert entries[1]["timestamp"] == "Tuesday, January 02, 2024 at 11:00 AM"
    assert entries[1]["entry"] == "Second journal entry."

def test_empty_input():
    entries = create_entries("")
    assert len(entries) == 0
    assert entries == []

def test_none_input():
    try:
        create_entries(None)
    except ValueError as ve:
        assert str(ve) == "Input data cannot be None"

def test_one_entry_no_newline():
    sample_text = "Monday, January 01, 2024 at 10:00 AM\nOnly one entry without a newline at the end."
    entries = create_entries(sample_text)
    assert len(entries) == 1
    assert entries[0]["timestamp"] == "Monday, January 01, 2024 at 10:00 AM"
    assert entries[0]["entry"] == "Only one entry without a newline at the end."

def test_whitespace_handling():
    sample_text = """

Monday, January 01, 2024 at 10:00 AM

   Entry with spaces   

"""

    entries = create_entries(sample_text)

    assert len(entries) == 1
    assert entries[0]["entry"] == "Entry with spaces"

def test_multiline_entry():
    sample_text = """
Monday, January 01, 2024 at 10:00 AM
Line one.
Line two.
Line three.
"""

    entries = create_entries(sample_text)

    assert len(entries) == 1
    assert "Line one." in entries[0]["entry"]
    assert "Line two." in entries[0]["entry"]

def test_no_timestamps():
    sample_text = """
This is just text.
No timestamps here.
"""

    entries = create_entries(sample_text)

    assert entries == []