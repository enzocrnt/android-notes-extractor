"""
Scans 'Tecno/uncategorized' for journal notes with dates or date ranges in various
formats (e.g., date ranges, text months, spaced hyphens, typos like 'Comtinuation'),
standardizes them into 'MM-DD-YYYY - Title.md' with the 3 blank lines header format,
and moves them to 'Tecno/journal_entries/'.

Before:
  Tecno/uncategorized/
    - 01-26-2026 to 02-01-2026 thoughts this week.md
    - 02-16- 2026 - LT1 sa data com lab, Com arch comple.md
    - Jul. 19 - Jul. 21, 2024 - Sacred Heart kasama si T.md
    - Jul. 20 - Jul. 29, 2024 - Bakasyon sa Sacred Heart.md
    - Jun. 20 - Jun. 22, 2024 - Sleepover kay Jared back.md
    - Comtinuation ng Apr. 4, 2024.md
    - Continuation ng Nov. 20-21, 2024.md

After:
  Tecno/journal_entries/
    - 01-26-2026 - 01-26-2026 to 02-01-2026 thoughts this week.md
    - 02-16-2026 - LT1 sa data com lab, Com arch comple.md
    - 07-19-2024 - Sacred Heart kasama si T.md
    - 07-20-2024 - Bakasyon sa Sacred Heart.md
    - 06-20-2024 - Sleepover kay Jared back.md
    - 04-04-2024 - (Part 2).md
    - 11-20-2024 - (Part 2).md

Non-dated files (e.g., '_input type=__.md', '2ITB.md') remain untouched in uncategorized.
"""

import os
import re
import shutil
from pathlib import Path

MONTH_MAP = {
    "jan": "01", "january": "01", "feb": "02", "february": "02",
    "mar": "03", "march": "03", "apr": "04", "april": "04",
    "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
    "aug": "08", "august": "08", "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10", "nov": "11", "november": "11", "dec": "12", "december": "12"
}

def sanitize_filename(name: str, max_len: int = 65) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|\r\n]', "", name)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned.rstrip(". ")

def parse_month_to_num(m_str: str) -> str:
    clean = m_str.replace(".", "").strip().lower()
    return MONTH_MAP.get(clean, "01")

def get_body_content(file_path: Path) -> str:
    """Reads file and returns pure body content without header metadata."""
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

def extract_journal_date_and_title(filename_stem: str):
    stem = filename_stem.strip()

    # 1. Match 'Comtinuation' or 'Continuation' variations
    # e.g., 'Comtinuation ng Apr. 4, 2024' or 'Continuation ng Nov. 20-21, 2024'
    cont_match = re.match(r"^(?:Co[mn]tinuation)\s*(\d+)?\s*(?:ng|for)?\s*(.+)$", stem, re.IGNORECASE)
    if cont_match:
        part_idx_str, date_part = cont_match.groups()
        part_num = int(part_idx_str) + 1 if part_idx_str else 2
        
        # Check text month inside continuation
        tm = re.search(r"([A-Za-z]+)\.?\s*(\d{1,2})(?:-\d{1,2})?,?\s*(\d{4})", date_part)
        if tm:
            m, d, y = tm.groups()
            std_date = f"{parse_month_to_num(m)}-{int(d):02d}-{y}"
            return std_date, f"(Part {part_num})", False

    # 2. Spaced MM-DD- YYYY pattern (e.g. '02-16- 2026 - LT1 sa data com lab, Com arch comple')
    spaced_date_match = re.match(r"^(\d{2})-(\d{2})-\s*(\d{4})\s*-\s*(.+)$", stem)
    if spaced_date_match:
        m, d, y, title = spaced_date_match.groups()
        return f"{m}-{d}-{y}", title.strip(), False

    # 3. Numeric Date Range (e.g. '01-26-2026 to 02-01-2026 thoughts this week')
    num_range_match = re.match(r"^(\d{2}-\d{2}-\d{4})\s+to\s+(\d{2}-\d{2}-\d{4})\s+(.+)$", stem, re.IGNORECASE)
    if num_range_match:
        start_date, end_date, title = num_range_match.groups()
        full_title = f"{start_date} to {end_date} {title.strip()}"
        return start_date, full_title, False

    # 4. Text Month Date Range (e.g. 'Jul. 19 - Jul. 21, 2024 - Sacred Heart kasama si T')
    range_text_match = re.match(
        r"^([A-Za-z]+)\.?\s*(\d{1,2})\s*-\s*(?:[A-Za-z]+\.?\s*)?(\d{1,2}),?\s*(\d{4})\s*-\s*(.+)$", 
        stem, 
        re.IGNORECASE
    )
    if range_text_match:
        m1, d1, d2, y, title = range_text_match.groups()
        std_date = f"{parse_month_to_num(m1)}-{int(d1):02d}-{y}"
        return std_date, title.strip(), False

    # 5. Text Month Single Date (e.g. 'Jul. 16, 2024 - Title' or 'Gameplan Jul. 16, 2024')
    single_text_match = re.search(r"([A-Za-z]+)\.?\s*(\d{1,2}),?\s*(\d{4})", stem)
    if single_text_match:
        m, d, y = single_text_match.groups()
        std_date = f"{parse_month_to_num(m)}-{int(d):02d}-{y}"
        # Keep clean title by removing date substring
        clean_title = re.sub(r"([A-Za-z]+)\.?\s*(\d{1,2}),?\s*(\d{4})", "", stem).strip(" -_")
        return std_date, clean_title if clean_title else "Journal Entry", False

    return None, None, False

def recover_missed_journals():
    BASE_DIR = Path(__file__).parent
    uncategorized_dir = BASE_DIR / "uncategorized"
    journal_dir = BASE_DIR / "journal_entries"

    if not uncategorized_dir.exists():
        print(f"Directory not found: {uncategorized_dir.resolve()}")
        return

    journal_dir.mkdir(parents=True, exist_ok=True)
    recovered_count = 0

    for fpath in list(uncategorized_dir.glob("*.md")):
        std_date, title, _ = extract_journal_date_and_title(fpath.stem)
        
        if std_date:
            safe_title = sanitize_filename(title, max_len=50) if title else ""
            filename_suffix = f" - {safe_title}" if safe_title else ""
            new_filename = f"{std_date}{filename_suffix}.md"
            
            body = get_body_content(fpath)
            header = f"{std_date}{filename_suffix}"
            full_content = f"{header}\n\n\n\n{body}"

            target_path = journal_dir / new_filename
            counter = 1
            while target_path.exists():
                target_path = journal_dir / f"{std_date}{filename_suffix}_{counter}.md"
                counter += 1

            with open(fpath, "w", encoding="utf-8") as f:
                f.write(full_content)

            shutil.move(str(fpath), str(target_path))
            recovered_count += 1
            print(f"[RECOVERED JOURNAL] {target_path.name}")

    print(f"\nFinished! Recovered and formatted {recovered_count} notes into Tecno/journal_entries/.")

if __name__ == "__main__":
    recover_missed_journals()