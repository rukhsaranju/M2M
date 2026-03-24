import subprocess
import sys


def test_search_ngrams_requires_length():
    result = subprocess.run(
        [sys.executable, "main.py", "--search_ngrams", "5"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Error: Please provide an n-gram length." in result.stdout


def test_search_ngrams_requires_positive_length():
    result = subprocess.run(
        [sys.executable, "main.py", "--search_ngrams", "5", "--n-grams-length", "0"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Error: Invalid n-gram length requested (0)" in result.stdout


def test_top_keywords_requires_positive_count():
    result = subprocess.run(
        [sys.executable, "main.py", "--top_keywords", "0"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Error: Invalid number of keywords requested (0)" in result.stdout


def test_top_keywords_requires_existing_database():
    result = subprocess.run(
        [sys.executable, "main.py", "--top_keywords", "5", "--db_name", "missing.db"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Error: Database not found." in result.stdout


def test_keyword_trend_requires_existing_database():
    result = subprocess.run(
        [sys.executable, "main.py", "--keyword_trend", "focus", "--db_name", "missing.db"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Error: Database not found." in result.stdout


def test_top_keywords_by_month_requires_existing_database():
    result = subprocess.run(
        [sys.executable, "main.py", "--top_keywords_by_month", "5", "--db_name", "missing.db"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Error: Database not found." in result.stdout
