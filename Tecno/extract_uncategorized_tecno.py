"""
Scans the 'Tecno/uncategorized' folder, extracts all note titles (without the .md extension),
and exports them into a clean, line-separated text file 'uncategorized_titles_tecno.txt'.

Before:
  Tecno/uncategorized/
    - _input type=__.md
    - 2ITB.md
    - 2nd checkup Dr. Cabansag.md
    - 3_40 ready na civil law.md

After:
  Tecno/uncategorized_titles_tecno.txt
    _input type=__
    2ITB
    2nd checkup Dr. Cabansag
    3_40 ready na civil law

Non-markdown files are skipped. Existing output files are overwritten cleanly.
"""

import os
from pathlib import Path

def extract_tecno_titles():
    BASE_DIR = Path(__file__).parent
    uncategorized_dir = BASE_DIR / "uncategorized"
    output_file = BASE_DIR / "uncategorized_titles_tecno.txt"

    if not uncategorized_dir.exists():
        print(f"Directory not found: {uncategorized_dir.resolve()}")
        return

    # Collect and sort all markdown files case-insensitively
    md_files = sorted(list(uncategorized_dir.glob("*.md")), key=lambda p: p.name.lower())

    if not md_files:
        print("No .md files found in the Tecno uncategorized folder.")
        return

    titles = [f.stem for f in md_files]

    # Write titles line-by-line
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(titles))

    print(f"Successfully extracted {len(titles)} titles to '{output_file.resolve()}'!")

if __name__ == "__main__":
    extract_tecno_titles()