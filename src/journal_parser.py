"""Parse journal text into timestamped entries."""

from datetime import datetime


def is_timestamp_line(line):
    try:
        datetime.strptime(line.strip(), "%A, %B %d, %Y at %I:%M %p")
        return True
    except ValueError:
        return False


def create_entries(data):
    entries = []
    current_entry = None
    current_lines = []

    if data is None:
        raise ValueError("Input data cannot be None")

    for line in data.splitlines():
        if is_timestamp_line(line):
            if current_entry is not None:
                current_entry["entry"] = "\n".join(current_lines).strip()
                entries.append(current_entry)
            current_entry = {"timestamp": line.strip()}
            current_lines = []
        else:
            current_lines.append(line)

    if current_entry is not None:
        current_entry["entry"] = "\n".join(current_lines).strip()
        entries.append(current_entry)

    return entries


def print_entries_to_file(entries):
    with open("output.txt", "w", encoding="utf-8") as f:
        for page in entries:
            f.write(page["timestamp"] + "\n")
            f.write(page["entry"])
            f.write("\n\n")
