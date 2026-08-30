"""
journal_sorter_xiaomi.py
========================
Sorts journal entries from Xiaomi/raw_exports into Xiaomi/journal_entries.
Converts textual dates (e.g. 'Apr. 1, 2023', 'Nov. 20-21, 2024') into 'MM-DD-YYYY'.
Preserves distinct titles on the same day without adding [P1]/[P2] unless explicitly a part.
Enforces 3 empty lines between title header and body text.
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

MONTH_MAP = {
    "jan": ("01", "Jan."), "feb": ("02", "Feb."), "mar": ("03", "Mar."),
    "apr": ("04", "Apr."), "may": ("05", "May."), "jun": ("06", "Jun."),
    "jul": ("07", "Jul."), "aug": ("08", "Aug."), "sep": ("09", "Sept."),
    "oct": ("10", "Oct."), "nov": ("11", "Nov."), "dec": ("12", "Dec.")
}

def parse_date_structure(name: str):
    clean_name = name.strip()
    
    # Multi-day range (e.g., Nov. 20-21, 2024 - Title)
    range_regex = r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})\s*[-~–]\s*(\d{1,2}),?\s+(\d{4})(?:\s*[-–:]\s*(.*))?$"
    m_range = re.match(range_regex, clean_name, re.IGNORECASE)
    if m_range:
        mon_str, day1, day2, year, rest = m_range.groups()
        mm, abbrev = MONTH_MAP[mon_str[:3].lower()]
        dd1 = f"{int(day1):02d}"
        start_date = f"{mm}-{dd1}-{year}"
        range_tag = f"[{abbrev} {int(day1)}-{int(day2)}]"
        return start_date, range_tag, (rest or "").strip()

    # Single date (e.g., Apr. 1, 2023 - Title)
    single_regex = r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})(?:\s*[-–:]\s*(.*))?$"
    m_single = re.match(single_regex, clean_name, re.IGNORECASE)
    if m_single:
        mon_str, day, year, rest = m_single.groups()
        mm, _ = MONTH_MAP[mon_str[:3].lower()]
        dd = f"{int(day):02d}"
        start_date = f"{mm}-{dd}-{year}"
        return start_date, None, (rest or "").strip()

    # Already numerical (e.g., 11-20-2024 - Title)
    num_single_regex = r"^(\d{2})-(\d{2})-(\d{4})(?:\s*[-–:]\s*(.*))?$"
    m_num_single = re.match(num_single_regex, clean_name)
    if m_num_single:
        mm, dd, year, rest = m_num_single.groups()
        return f"{mm}-{dd}-{year}", None, (rest or "").strip()

    return None

def format_body_spacing(content: str) -> str:
    lines = content.splitlines()
    if not lines:
        return content

    header_indices = []
    idx = 0
    while idx < len(lines):
        line_s = lines[idx].strip()
        if not line_s:
            idx += 1
            continue
        if line_s.startswith("#") or line_s.lower() == "title" or line_s.startswith("**Date") or parse_date_structure(line_s):
            header_indices.append(idx)
            idx += 1
        else:
            break

    if header_indices:
        last_header_pos = header_indices[-1]
        headers = [lines[i] for i in header_indices]
        body = lines[last_header_pos + 1:]
        while body and not body[0].strip():
            body.pop(0)
        return "\n".join(headers) + "\n\n\n" + "\n".join(body).rstrip() + "\n"
    
    return content.rstrip() + "\n"

def run_journal_sorter():
    BASE_DIR = Path(__file__).parent
    raw_dir = BASE_DIR / "raw_exports"
    journal_dir = BASE_DIR / "journal_entries"
    journal_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        print(f"Error: Directory not found: {raw_dir}")
        return

    files = list(raw_dir.glob("*.md"))
    moved_count = 0

    for f in files:
        parsed = parse_date_structure(f.stem)
        if parsed:
            start_date, range_tag, rest_title = parsed
            
            # Check for explicit continuation in original name (e.g., '(Part 2)', '[P2]')
            part_match = re.search(r"\(Part\s*(\d+)\)|\[P(\d+)\]", rest_title, re.IGNORECASE)
            part_tag = None
            if part_match:
                num = part_match.group(1) or part_match.group(2)
                part_tag = f"[P{num}]"
                rest_title = re.sub(r"\(Part\s*\d+\)|\[P\d+\]", "", rest_title, flags=re.IGNORECASE).strip()

            parts = [start_date]
            if part_tag:
                parts.append(part_tag)
            if range_tag:
                parts.append(range_tag)
            if rest_title:
                parts.append(rest_title)

            dest = journal_dir / (f"{' - '.join(parts)}.md")
            try:
                with open(f, "r", encoding="utf-8") as rf:
                    content = format_body_spacing(rf.read())
                with open(dest, "w", encoding="utf-8") as wf:
                    wf.write(content)
                f.unlink()
            except Exception:
                shutil.move(str(f), str(dest))
            moved_count += 1

    print(f"Sorted {moved_count} journals into {journal_dir}")

if __name__ == "__main__":
    run_journal_sorter()