"""
Scans 'journal_entries' for notes already named with '(Part X)' suffixes, 
matches them with the primary daily note on the same date, prepends [P1] to 
the main entry's title, and applies the full title to all subsequent parts [P2], [P3], etc.

Before:
  journal_entries/
    - 08-05-2024 - Welcome Walk.md
    - 08-05-2024 - (Part 2).md
    - 08-25-2024 - First meetup kay Ayes...md
    - 08-25-2024 - (Part 2).md
    - 08-25-2024 - (Part 3).md
    - 08-25-2024 - (Part 4).md

After:
  journal_entries/
    - 08-05-2024 - [P1] Welcome Walk.md
    - 08-05-2024 - [P2] Welcome Walk.md
    - 08-25-2024 - [P1] First meetup kay Ayes...md
    - 08-25-2024 - [P2] First meetup kay Ayes...md
    - 08-25-2024 - [P3] First meetup kay Ayes...md
    - 08-25-2024 - [P4] First meetup kay Ayes...md

Notes without any '(Part X)' companions remain untouched.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def sanitize_filename(name: str, max_len: int = 65) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|\r\n]', "", name)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned.rstrip(". ")

def get_body_content(file_path: Path) -> str:
    """Reads file and returns pure body content without header line."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return ""

    body_match = re.search(r"^#\s*[^\n]+\n+(?:\*\*Date:\*\*[^\n]*\n+)?", content)
    if body_match:
        return content[body_match.end():].lstrip("\n")

    lines = content.splitlines()
    if lines and (lines[0].startswith("#") or re.match(r"^\d{2}-\d{2}-\d{4}", lines[0])):
        return "\n".join(lines[1:]).lstrip("\n")
    return content.lstrip("\n")

def process_journal_entries():
    BASE_DIR = Path(__file__).parent
    journal_dir = BASE_DIR / "journal_entries"

    if not journal_dir.exists():
        print(f"Directory not found: {journal_dir.resolve()}")
        return

    # 1. Group part files by date: date_key -> list of (part_number, file_path)
    part_files_map = defaultdict(list)
    part_regex = re.compile(r"^(\d{2}-\d{2}-\d{4})\s*-\s*\(Part\s*(\d+)\)$", re.IGNORECASE)

    all_files = list(journal_dir.glob("*.md"))

    for f in all_files:
        match = part_regex.match(f.stem.strip())
        if match:
            date_key, part_num = match.groups()
            part_files_map[date_key].append((int(part_num), f))

    if not part_files_map:
        print("No '(Part X)' files found in journal_entries.")
        return

    # 2. Match with main notes on the same date
    for date_key, parts_list in part_files_map.items():
        main_entry = None
        main_title = ""

        # Find the base entry for this date (excluding other parts)
        for f in all_files:
            if f.stem.startswith(date_key):
                if not part_regex.match(f.stem.strip()) and not re.search(r"\[P\d+\]", f.stem):
                    main_entry = f
                    if " - " in f.stem:
                        main_title = f.stem.split(" - ", 1)[1].strip()
                    break

        title_suffix = f" {main_title}" if main_title else ""
        safe_suffix = f" {sanitize_filename(main_title, max_len=50)}" if main_title else ""

        # Update and rename main note to [P1]
        if main_entry and main_entry.exists():
            main_body = get_body_content(main_entry)
            p1_header = f"{date_key} - [P1]{title_suffix}"
            p1_filename = f"{date_key} - [P1]{safe_suffix}.md"

            with open(main_entry, "w", encoding="utf-8") as f:
                f.write(f"{p1_header}\n\n\n\n{main_body}")

            new_main_path = journal_dir / p1_filename
            if main_entry.resolve() != new_main_path.resolve():
                main_entry.rename(new_main_path)
                print(f"[P1 Main Entry] Renamed: {new_main_path.name}")

        # Update and rename all follow-up parts [P2], [P3], etc.
        parts_list.sort(key=lambda x: x[0])
        for part_num, part_file in parts_list:
            if not part_file.exists():
                continue
            part_body = get_body_content(part_file)
            part_header = f"{date_key} - [P{part_num}]{title_suffix}"
            part_filename = f"{date_key} - [P{part_num}]{safe_suffix}.md"

            with open(part_file, "w", encoding="utf-8") as f:
                f.write(f"{part_header}\n\n\n\n{part_body}")

            new_part_path = journal_dir / part_filename
            if part_file.resolve() != new_part_path.resolve():
                part_file.rename(new_part_path)
                print(f"[P{part_num} Part] Renamed: {new_part_path.name}")

    print("\nAll matching journal entries updated to [P1], [P2], [P3] format successfully!")

if __name__ == "__main__":
    process_journal_entries()