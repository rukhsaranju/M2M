# Me 2 Me Engine

Me 2 Me Engine is a local-first journal analysis CLI for people who want to explore their writing privately, structurally, and on their own terms.

This project parses journal exports, stores entries in a local SQLite database, and provides offline text analysis without cloud services or AI-generated interpretation.

## Why This Exists

Most tools for analyzing personal writing push users toward cloud storage, automated summaries, or systems that try to explain the writer back to themselves.

This project takes the opposite approach.

Personal writing is sensitive. Reflection should remain private and self-directed. Me 2 Me Engine is built for people who want useful structure and analysis without giving up control over their data or their interpretation.

The goal is not to tell you who you are. The goal is to help you examine your own patterns while keeping meaning in your hands.

## Version 1 Scope

Version 1 focuses on a narrow, practical workflow:

- Parse raw journal text into structured entries
- Store entries in a local SQLite database
- Prevent duplicate entry insertion
- Search entries by keyword
- Measure keyword frequency
- Extract top keywords with stopword filtering
- Extract top keywords for each month
- Track keyword trends over time by month
- Extract common n-grams
- Export analysis results to text files

## Privacy Philosophy

- Local-first
- No cloud dependency
- No AI-generated psychological summaries
- No automated identity conclusions
- User retains interpretive control

## Tech Stack

- Python
- SQLite
- NLTK
- Pytest

## Project Structure

```text
.
├── main.py
├── src/
│   ├── database.py
│   └── journal_parser.py
├── tests/
│   ├── test_database.py
│   ├── test_main.py
│   └── test_parser.py
└── readme.md
```

## Setup

Install dependencies:

```bash
python -m pip install nltk pytest
```

Download the NLTK stopwords corpus:

```bash
python -c "import nltk; nltk.download('stopwords')"
```

If you use a project virtual environment:

```bash
source .venv/bin/activate
```

## Usage

Parse a journal file into the database:

```bash
python main.py --parse --file your_journal.txt
```

Search entries by keyword:

```bash
python main.py --search "keyword"
```

Measure keyword frequency:

```bash
python main.py --frequency "keyword"
```

Export top keywords:

```bash
python main.py --top_keywords 10
```

Export top keywords for each month:

```bash
python main.py --top_keywords_by_month 5
```

Track a keyword trend over time by month:

```bash
python main.py --keyword_trend "focus"
```

Export top n-grams:

```bash
python main.py --search_ngrams 10 --n-grams-length 2
```

Use a custom database path:

```bash
python main.py --top_keywords 10 --db_name /path/to/custom.db
```

## Expected Input Format

Version 1 assumes each journal entry begins with a timestamp in this format:

```text
Monday, January 01, 2024 at 10:00 AM
Today I felt really productive.

Tuesday, January 02, 2024 at 11:00 AM
Worked on my project and learned a lot.
```

The parser is intentionally strict in this version because it was built around a real journal export format. Entries that do not follow this structure may not parse correctly.

## Testing

Run the test suite with:

```bash
python -m pytest
```

## Current Limitations

- The parser expects one specific timestamp format
- Inconsistent export formats are not yet handled gracefully
- Analysis is descriptive and text-based, not interpretive
- Time-based analysis is currently grouped by month only

## Future Direction

Planned improvements include:

- Support for multiple timestamp formats
- More resilient parsing for inconsistent exports
- Better CLI ergonomics
- Richer offline analysis features
- Voice-to-text ingestion for audio notes

## Project Intent

This tool is designed for people who want to keep their diary data fully local, explore it without surveillance or automation, and share their own findings on their own terms if they choose.
