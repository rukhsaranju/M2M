"""
Journal Parser

Journal_parser.py
    ├── Read journal text file
    ├── Detect timestamps 
    ├── Build entries
    └── (Optional) debug output file 

Responsible for:

Text File → Entries structured in a list of dictionaries

Contains:

    is_timestamp_line()
    create_entries()
    print_entries_to_file()

Purpose
-------
Parse a text journal file where each entry begins with a timestamp line.

Example timestamp format:
    Monday, January 01, 2024 at 10:30 AM

Logic
-----
1. Read the entire journal text file.
2. Iterate through the file line by line.
3. Detect lines that match the timestamp format.
4. When a timestamp is found:
      - Save the previous entry (if one exists).
      - Start a new dictionary with that timestamp.
5. Continue collecting lines until the next timestamp appears.
6. Store each entry as a dictionary:
      {"timestamp": <timestamp>, "entry": <text>}
7. Append each dictionary to a list of entries.
8. After the loop finishes, save the final entry (since no later timestamp will trigger it).
9. Write parsed entries to an output file.

Assumption
----------
Each entry begins with a line that exactly matches the timestamp format.

Output
------
A list of dictionaries representing structured journal entries.

"""
from datetime import datetime

def is_timestamp_line(line):
    try:
        datetime.strptime(line.strip(), "%A, %B %d, %Y at %I:%M %p")
        return True
    except ValueError:
        return False

def create_entries(data): 
    entries = []
    entry = ""
    current_entry = None
    if data is None:
        raise ValueError("Input data cannot be None")
    for line in data.splitlines():
        if is_timestamp_line(line):
            if current_entry is not None: 
                #print("in current entry is not none if")
                current_entry["entry"] = entry.strip()
                entries.append(current_entry)
                #print(entries)
                entry = ""
            
            current_entry = {"timestamp":line.strip()}
            #print(entries)
            
        else:
            #print("in else")
            entry += line + "\n" 
    if current_entry is not None:
        current_entry["entry"] = entry.strip()
        entries.append(current_entry)
    
    print(f"Total entries parsed from file: {len(entries)}")
    return entries

def print_entries_to_file(entries):
    with open("output.txt", "w", encoding="utf-8") as f:
        for page in entries:
            f.write(page["timestamp"] + "\n")
            f.write(page["entry"])
            f.write("\n\n")


