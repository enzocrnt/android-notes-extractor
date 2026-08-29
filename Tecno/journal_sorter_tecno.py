import os
import re
import shutil
from pathlib import Path

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}

def sanitize_filename(name: str, max_len: int = 65) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|\r\n]', "", name)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned.rstrip(". ")

def parse_date(month_str: str, day_str: str, year_str: str) -> str:
    clean_month = month_str.replace(".", "").strip().lower()
    month_num = MONTH_MAP.get(clean_month, "01")
    if "-" in day_str:
        parts = day_str.split("-")
        day_num = "-".join(str(int(p)).zfill(2) for p in parts if p.isdigit())
    else:
        day_num = str(int(day_str)).zfill(2)
    return f"{month_num}-{day_num}-{year_str}"

def get_unique_filepath(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    while target_path.exists():
        target_path = parent / f"{stem}_{counter}{suffix}"
        counter += 1
    return target_path

def process_and_sort_tecno(file_path: Path, journal_dir: Path, uncategorized_dir: Path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {file_path.name}: {e}")
        return

    # 1. Matches already numerical names (e.g., 01-07-2026 - Title.md or 01-26-2026 to 02-01-2026...)
    already_numeric_match = re.match(r"^(\d{2}-\d{2}-\d{4}(?:(?:\s+to\s+\d{2}-\d{2}-\d{4})?\s*-\s*[^\n]+)?)$", file_path.stem)

    # 2. Matches textual dates in filename (e.g., Nov. 4, 2023 - Subtitle.md)
    text_date_match = re.match(r"^([A-Za-z]+)\.?\s*(\d{1,2}(?:-\d{1,2})?),\s*(\d{4})(?:\s*-\s*(.*))?$", file_path.stem)

    # 3. Check internal Tecno markdown header (# Title \n **Date:** Date)
    body_tecno_match = re.search(r"^#\s*([^\n]+)\n+(?:\*\*Date:\*\*[^\n]*\n+)?", content)

    is_journal = False
    new_header = ""
    clean_stem = ""
    body = ""

    if already_numeric_match:
        is_journal = True
        new_header = file_path.stem.strip()
        clean_stem = sanitize_filename(new_header, max_len=75)

        # Clean body text
        if body_tecno_match:
            body = content[body_tecno_match.end():].lstrip("\n")
        else:
            lines = content.splitlines()
            if lines and (lines[0].startswith("#") or lines[0].strip() == new_header):
                body = "\n".join(lines[1:]).lstrip("\n")
            else:
                body = content.lstrip("\n")

    elif text_date_match:
        m, d, y, sub = text_date_match.groups()
        date_formatted = parse_date(m, d, y)
        subtitle = (sub or "").strip()
        is_journal = True

        if body_tecno_match:
            body = content[body_tecno_match.end():].lstrip("\n")
        else:
            lines = content.splitlines()
            body = "\n".join(lines[1:]).lstrip("\n") if len(lines) > 1 else ""

        if subtitle:
            new_header = f"{date_formatted} - {subtitle}"
            safe_sub = sanitize_filename(subtitle, max_len=55)
            clean_stem = f"{date_formatted} - {safe_sub}"
        else:
            new_header = date_formatted
            clean_stem = date_formatted

    if is_journal:
        # Guarantee 3 blank lines: Line 1 (Title) -> \n\n\n\n -> Line 5 (Content)
        updated_content = f"{new_header}\n\n\n\n{body}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        target_path = journal_dir / f"{clean_stem}.md"
        final_path = get_unique_filepath(target_path)
        shutil.move(str(file_path), str(final_path))
        print(f"[Journal] Moved: {final_path.name}")
    else:
        # Keep non-journal file in uncategorized
        if file_path.parent != uncategorized_dir:
            target_path = uncategorized_dir / file_path.name
            final_path = get_unique_filepath(target_path)
            shutil.move(str(file_path), str(final_path))
            print(f"[Uncategorized] Moved: {final_path.name}")

def main():
    source_dirs = [Path("./uncategorized_tecno"), Path("./my_exported_journals")]
    journal_dir = Path("./journal_entries_tecno")
    uncategorized_dir = Path("./uncategorized_tecno")

    journal_dir.mkdir(parents=True, exist_ok=True)
    uncategorized_dir.mkdir(parents=True, exist_ok=True)

    print("Re-scanning and moving entries...")
    for s_dir in source_dirs:
        if s_dir.exists():
            for file in list(s_dir.glob("*.md")):
                process_and_sort_tecno(file, journal_dir, uncategorized_dir)

    print("\nComplete! All misplaced notes have been moved to journal_entries_tecno.")

if __name__ == "__main__":
    main()