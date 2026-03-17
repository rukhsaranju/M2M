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
import nltk
#nltk.download("stopwords")
from nltk.corpus import stopwords
import os

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

def search_entries(keyword, db_name='journal_entries.db'): 
    if not os.path.exists(db_name):
        print("Error: Database not found. Please use the --parse flag to parse the journal entries first and create the database.")
        return []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE entry LIKE ?", ('%' + keyword + '%',))
    results = cursor.fetchall()
    conn.close()
    results_only_sentences_with_keyword = []

    for id, timestamp, entry in results:
        sentences = re.split(r'(?<=[.!?])\s+', entry)
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                results_only_sentences_with_keyword.append((id, timestamp, sentence))

    if not results_only_sentences_with_keyword:
        print(f"No sentences found containing the keyword '{keyword}'.")
        return []

    return results_only_sentences_with_keyword

def keyword_frequency(keyword, db_name='journal_entries.db'):
    if not os.path.exists(db_name):
        return("Error: Database not found. Please use the --parse flag to parse the journal entries first and create the database.")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT entry FROM entries")
    results = cursor.fetchall()
    conn.close()

    frequency = 0
    for (entry,) in results:
        frequency += entry.lower().count(keyword.lower())

    return f"Frequency of '{keyword}': {frequency}"

def top_keywords(number_of_keywords, db_name='journal_entries.db'):
    if not os.path.exists(db_name):
        print("Error: Database not found. Please use the --parse flag to parse the journal entries first and create the database.")
        return []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT entry FROM entries")
    results = cursor.fetchall()
    conn.close()

    word_freq = {}
    try:
        words_ignore = set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords")
        words_ignore = set(stopwords.words("english"))
    words_ignore.update(["im", "ive", "dont", "cant", "didnt", "doesnt", "wont", "couldnt", "wouldnt", "shouldnt", "isnt", "arent", "wasnt", "werent", "like"]) 
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
        print(f"Invalid number of keywords requested ({number_of_keywords})")
        return []
    elif number_of_keywords > len(sorted_words):
        print(f"Requested number of keywords ({number_of_keywords}) exceeds the total unique keywords ({len(sorted_words)}). Please choose a number less than or equal to {len(sorted_words)}.")
        return []
    else:
        return sorted_words[:number_of_keywords]

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
            elif len(row) == 2:
                f.write(f"Keyword: {row[0]}\n")
                f.write(f"Frequency: {row[1]}\n")
                f.write("-" * 50 + "\n")

