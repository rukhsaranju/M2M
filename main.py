from src.journal_parser import create_entries, print_entries_to_file 
from src.database import create_database, insert_entries, keyword_frequency, search_entries, top_keywords, export_results
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process journal entries.")
    parser.add_argument("--parse", action="store_true", help="Parse the journal entries from the text file.")
    parser.add_argument("--file", type=str, help="Path to the journal text file.")
    parser.add_argument("--search", type=str, help="Search for a keyword in the journal entries.")
    parser.add_argument("--frequency", type=str, help="Get the frequency of a keyword in the journal entries.")
    parser.add_argument("--top_keywords", type=int, help="Get the top keywords from the journal entries.")

    args = parser.parse_args()

    if args.parse:
        if not args.file:
            print("Error: Please provide the path to the journal text file using the --file argument.")
            return
        try:
            with open(args.file, "r") as my_file:
                data = my_file.read()
        except FileNotFoundError:
            print(f"Error: File {args.file} not found.")
            return
    
        try:
            entries = create_entries(data)
            create_database() 
            insert_entries(entries)
        except ValueError as ve:
            print(f"Error: {ve}")
            return
        
        

    if args.search is not None:
        search_test = search_entries(args.search)
        if search_test != []:
            export_results(search_test, f"search_results_{args.search}.txt")

    if args.frequency is not None:
        frequency_result = keyword_frequency(args.frequency)
        print(frequency_result)

    if args.top_keywords is not None:
        top_keywords_result = top_keywords(args.top_keywords)
        if top_keywords_result != []:
            export_results(top_keywords_result, f"top_keywords_{args.top_keywords}.txt")

if __name__ == "__main__":    main()
