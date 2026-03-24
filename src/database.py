"""
Database.py

Responsible for:

entries → SQLite database

Functions like:

create_database()
insert_entries()
query_entries() """
import re
import sqlite3
import string
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
import os
from nltk.corpus import stopwords

CUSTOM_STOPWORDS = {
    "im", "ive", "dont", "cant", "didnt", "doesnt", "wont",
    "couldnt", "wouldnt", "shouldnt", "isnt", "arent",
    "wasnt", "werent", "like",
}

@lru_cache(maxsize=1)
def get_stopwords():
    try:
        words_ignore = set(stopwords.words("english"))
    except LookupError as exc:
        raise RuntimeError(
            "NLTK stopwords corpus is not installed. Run "
            "`python -c \"import nltk; nltk.download('stopwords')\"` first."
        ) from exc

    words_ignore.update(CUSTOM_STOPWORDS)
    return words_ignore

def ensure_database_exists(db_name):
    if not os.path.exists(db_name):
        raise FileNotFoundError(
            "Database not found. Please use the --parse flag to parse the journal "
            "entries first and create the database."
        )

def create_database(db_name='journal_entries.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            entry TEXT,
            UNIQUE(timestamp, entry)
        )
    ''')
    conn.commit()
    conn.close()

    print("Database ready.")

def insert_entries(entries, db_name='journal_entries.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    inserted_count = 0
    for e in entries:
        cursor.execute(
            "INSERT OR IGNORE INTO entries (timestamp, entry) VALUES (?, ?)",
            (e["timestamp"], e["entry"])
        )
        if cursor.rowcount == 1:
            inserted_count += 1
    conn.commit()
    conn.close() 

    print(f"Inserted {inserted_count} new entries into the database.")

def fetch_all(query, params=(), db_name='journal_entries.db'):
    ensure_database_exists(db_name)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


def search_entries(keyword, db_name='journal_entries.db'): 
    results = fetch_all("SELECT * FROM entries WHERE entry LIKE ?", ('%' + keyword + '%',), db_name)
    results_only_sentences_with_keyword = []
    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

    for id, timestamp, entry in results:
        sentences = re.split(r'(?<=[.!?])\s+', entry)
        for sentence in sentences:
            if pattern.search(sentence):
                results_only_sentences_with_keyword.append((id, timestamp, sentence))

    if not results_only_sentences_with_keyword:
        print(f"No sentences found containing the keyword '{keyword}'.")
        return []

    return results_only_sentences_with_keyword

def keyword_frequency(keyword, db_name='journal_entries.db'):
    results = fetch_all("SELECT entry FROM entries", db_name=db_name)

    frequency = 0
    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    for (entry,) in results:
        frequency += len(pattern.findall(entry))

    return f"Frequency of '{keyword}': {frequency}"

def top_keywords(number_of_keywords, db_name='journal_entries.db'):
    results = fetch_all("SELECT entry FROM entries", db_name=db_name)

    word_freq = {}
    words_ignore = get_stopwords()
    translator = str.maketrans('', '', string.punctuation)

    for (entry,) in results:
        words = entry.split()
        words = [word.lower().replace("’", "").translate(translator) for word in words]
        for word in words:
            if word == "" or len(word) < 3 or word in words_ignore:
                continue
            else:
                word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    if number_of_keywords <= 0:
        raise ValueError(f"Invalid number of keywords requested ({number_of_keywords})")
    if number_of_keywords > len(sorted_words):
        raise ValueError(
            f"Requested number of keywords ({number_of_keywords}) exceeds the total "
            f"unique keywords ({len(sorted_words)}). Please choose a number less than "
            f"or equal to {len(sorted_words)}."
        )
    return sorted_words[:number_of_keywords]

def top_ngrams(number_of_phrases, phrase_length, db_name='journal_entries.db'):
    if phrase_length is None:
        raise ValueError("Please provide an n-gram length.")
    if phrase_length <= 0:
        raise ValueError(f"Invalid n-gram length requested ({phrase_length})")
    results = fetch_all("SELECT entry FROM entries", db_name=db_name)

    ngram_freq = {}
    words_ignore = get_stopwords()
    translator = str.maketrans('', '', string.punctuation)

    for (entry,) in results:
        words = entry.split()
        words = [word.lower().replace("’", "").translate(translator) for word in words]
        for i in range(len(words) - phrase_length + 1):
            phrase = ' '.join(words[i:i + phrase_length])
            if all(word in words_ignore for word in phrase.split()):
                continue
            ngram_freq[phrase] = ngram_freq.get(phrase, 0) + 1

    sorted_phrases = sorted(ngram_freq.items(), key=lambda x: x[1], reverse=True)

    if number_of_phrases <= 0:
        raise ValueError(f"Invalid number of phrases requested ({number_of_phrases})")
    if number_of_phrases > len(sorted_phrases):
        raise ValueError(
            f"Requested number of phrases ({number_of_phrases}) exceeds the total "
            f"unique phrases ({len(sorted_phrases)}). Please choose a number less "
            f"than or equal to {len(sorted_phrases)}."
        )
    return sorted_phrases[:number_of_phrases]


def keyword_trend_over_time(keyword, db_name='journal_entries.db'):
    results = fetch_all("SELECT timestamp, entry FROM entries", db_name=db_name)

    trend_data = defaultdict(int)
    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

    for timestamp_text, entry in results:
        timestamp = datetime.strptime(timestamp_text, "%A, %B %d, %Y at %I:%M %p")
        month_key = timestamp.strftime("%Y-%m")
        trend_data[month_key] += len(pattern.findall(entry))

    return sorted(trend_data.items())

def top_keywords_by_month(number_of_keywords, db_name='journal_entries.db'):
    if number_of_keywords <= 0:
        raise ValueError(f"Invalid number of keywords requested ({number_of_keywords})")

    results = fetch_all("SELECT timestamp, entry FROM entries", db_name=db_name)
    monthly_keywords = defaultdict(lambda: defaultdict(int))
    words_ignore = get_stopwords()
    translator = str.maketrans('', '', string.punctuation)

    for timestamp_text, entry in results:
        timestamp = datetime.strptime(timestamp_text, "%A, %B %d, %Y at %I:%M %p")
        month_key = timestamp.strftime("%Y-%m")
        words = entry.split()
        words = [word.lower().replace("’", "").translate(translator) for word in words]
        for word in words:
            if word == "" or len(word) < 3 or word in words_ignore:
                continue
            monthly_keywords[month_key][word] += 1

    if not monthly_keywords:
        return []

    top_keywords_per_month = []
    for month_key in sorted(monthly_keywords):
        sorted_words = sorted(
            monthly_keywords[month_key].items(),
            key=lambda item: item[1],
            reverse=True,
        )
        top_keywords_per_month.append((month_key, sorted_words[:number_of_keywords]))

    return top_keywords_per_month







def export_results(results, filename):
    with open(filename, "w") as f:
        if not results:
            f.write("No results found.\n")
            return
        for row in results:
            if len(row) == 3:
                f.write(f"ID: {row[0]}\n")
                f.write(f"Timestamp: {row[1]}\n")
                f.write(f"Entry:\n{row[2]}\n")
                f.write("-" * 50 + "\n")
            elif len(row) == 2 and isinstance(row[1], list):
                f.write(f"Month: {row[0]}\n")
                for keyword, frequency in row[1]:
                    f.write(f"Keyword: {keyword}\n")
                    f.write(f"Frequency: {frequency}\n")
                f.write("-" * 50 + "\n")
            elif len(row) == 2:
                f.write(f"Keyword: {row[0]}\n")
                f.write(f"Frequency: {row[1]}\n")
                f.write("-" * 50 + "\n")
