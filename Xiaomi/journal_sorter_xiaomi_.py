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

def sanitize_filename(name: str, max_len: int = 60) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|\r\n]', "", name)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned.rstrip(". ")

def parse_date(month_str: str, day_str: str, year_str: str) -> str:
    clean_month = month_str.replace(".", "").strip().lower()
    month_num = MONTH_MAP.get(clean_month, "01")
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

def sort_xiaomi_files():
    BASE_DIR = Path(__file__).parent
    raw_dir = BASE_DIR / "raw_exports"
    journal_dir = BASE_DIR / "journal_entries"
    uncat_dir = BASE_DIR / "uncategorized"

    journal_dir.mkdir(parents=True, exist_ok=True)
    uncat_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        print(f"Directory not found: {raw_dir.resolve()}")
        return

    date_pattern = re.compile(
        r"^#\s*([A-Za-z]+)\.?\s*(\d{1,2}),\s*(\d{4})[^\n]*\n+"
        r"(?:Date:\s*\n+)?"
        r"(?:[A-Za-z]+\.?\s*\d{1,2},\s*\d{4}[^\n]*\n+)?"
        r"(?:([^\n]+)\n+)?",
        re.MULTILINE
    )

    print("Sorting Xiaomi raw exports...")
    for file_path in list(raw_dir.glob("*.md")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = date_pattern.search(content)
        date_found = None
        subtitle = ""
        body = ""

        if match:
            m, d, y, sub = match.groups()
            date_found = parse_date(m, d, y)
            subtitle = (sub or "").strip()
            body = content[match.end():].lstrip("\n")
        else:
            fn_match = re.search(r"([A-Za-z]+)\.?\s*(\d{1,2}),\s*(\d{4})", file_path.name)
            if fn_match:
                m, d, y = fn_match.groups()
                date_found = parse_date(m, d, y)
                lines = [l.strip() for l in content.split("\n") if l.strip()]
                subtitle = lines[0].replace("#", "").strip() if lines else ""
                body = "\n".join(lines[1:]).lstrip("\n") if len(lines) > 1 else ""

        if date_found:
            new_header = f"{date_found} - {subtitle}" if (subtitle and subtitle != date_found) else date_found
            safe_title = sanitize_filename(subtitle, max_len=50) if (subtitle and subtitle != date_found) else ""
            clean_stem = f"{date_found} - {safe_title}" if safe_title else date_found

            updated_content = f"{new_header}\n\n\n\n{body}"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            dest = get_unique_filepath(journal_dir / f"{clean_stem}.md")
            shutil.move(str(file_path), str(dest))
            print(f"[Journal] Moved: {dest.name}")
        else:
            dest = get_unique_filepath(uncat_dir / file_path.name)
            shutil.move(str(file_path), str(dest))
            print(f"[Uncategorized] Moved: {dest.name}")

    print("\nXiaomi sorting complete!")

if __name__ == "__main__":
    sort_xiaomi_files()