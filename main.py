import argparse

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
from src.journal_parser import create_entries


def parse_args():
    parser = argparse.ArgumentParser(description="Process journal entries.")
    parser.add_argument("--db_name", type=str, help="Name of the database to create.")
    parser.add_argument("--parse", action="store_true", help="Parse the journal entries from the text file.")
    parser.add_argument("--file", type=str, help="Path to the journal text file.")
    parser.add_argument("--search", type=str, help="Search for a keyword in the journal entries.")
    parser.add_argument("--frequency", type=str, help="Get the frequency of a keyword in the journal entries.")
    parser.add_argument("--keyword_trend", type=str, help="Get keyword frequency grouped by month over time.")
    parser.add_argument("--top_keywords", type=int, help="Get the top keywords from the journal entries.")
    parser.add_argument("--top_keywords_by_month", type=int, help="Get the top keywords for each month.")
    parser.add_argument("--search_ngrams", type=int, help="Search for the most common n-grams in the journal entries.")
    parser.add_argument("--n-grams-length", type=int, help="Specify the length of n-grams to search for (used with --search_ngrams).")
    return parser.parse_args()


def get_database_name(args):
    return args.db_name if args.db_name else "journal_entries.db"


def handle_parse(args, database_name):
    if not args.file:
        raise ValueError("Please provide the path to the journal text file using the --file argument.")

    with open(args.file, "r") as my_file:
        data = my_file.read()

    entries = create_entries(data)
    print(f"Total entries parsed from file: {len(entries)}")
    create_database(database_name)
    insert_entries(entries, database_name)


def handle_search(args, database_name):
    if args.search is None:
        return

    results = search_entries(args.search, database_name)
    if results:
        export_results(results, f"search_results_{args.search}.txt")


def handle_frequency(args, database_name):
    if args.frequency is None:
        return

    frequency_result = keyword_frequency(args.frequency, database_name)
    print(frequency_result)


def handle_top_keywords(args, database_name):
    if args.top_keywords is None:
        return

    results = top_keywords(args.top_keywords, database_name)
    if results:
        export_results(results, f"top_keywords_{args.top_keywords}.txt")


def handle_keyword_trend(args, database_name):
    if args.keyword_trend is None:
        return

    results = keyword_trend_over_time(args.keyword_trend, database_name)
    if results:
        export_results(results, f"keyword_trend_{args.keyword_trend}.txt")


def handle_top_keywords_by_month(args, database_name):
    if args.top_keywords_by_month is None:
        return

    results = top_keywords_by_month(args.top_keywords_by_month, database_name)
    if results:
        export_results(results, f"top_keywords_by_month_{args.top_keywords_by_month}.txt")


def handle_top_ngrams(args, database_name):
    if args.search_ngrams is None:
        return

    results = top_ngrams(args.search_ngrams, args.n_grams_length, database_name)
    if results:
        export_results(results, f"search_ngrams_{args.search_ngrams}.txt")


def main():
    args = parse_args()
    database_name = get_database_name(args)

    if args.parse:
        try:
            handle_parse(args, database_name)
        except FileNotFoundError:
            print(f"Error: File {args.file} not found.")
            return
        except ValueError as exc:
            print(f"Error: {exc}")
            return

    try:
        handle_search(args, database_name)
        handle_frequency(args, database_name)
        handle_keyword_trend(args, database_name)
        handle_top_keywords(args, database_name)
        handle_top_keywords_by_month(args, database_name)
        handle_top_ngrams(args, database_name)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return


if __name__ == "__main__":
    main()
