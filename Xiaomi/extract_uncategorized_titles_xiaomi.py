"""
extract_uncategorized_titles_xiaomi.py
======================================
Scans 'Xiaomi/uncategorized/' for all markdown files, extracts their titles/filenames,
and writes a clean numbered list to 'Xiaomi/uncategorized_titles_xiaomi.txt'.
"""

from pathlib import Path

def extract_uncategorized_titles():
    # Detect if run from root or inside Xiaomi folder
    current_dir = Path(__file__).parent
    if (current_dir / "uncategorized").exists():
        uncat_dir = current_dir / "uncategorized"
        out_file = current_dir / "uncategorized_titles_xiaomi.txt"
    elif (current_dir / "Xiaomi" / "uncategorized").exists():
        uncat_dir = current_dir / "Xiaomi" / "uncategorized"
        out_file = current_dir / "Xiaomi" / "uncategorized_titles_xiaomi.txt"
    else:
        print("Error: Could not locate 'uncategorized' folder.")
        return

    md_files = sorted(list(uncat_dir.glob("*.md")), key=lambda p: p.stem.lower())
    
    if not md_files:
        print(f"No markdown files found in {uncat_dir}")
        return

    with open(out_file, "w", encoding="utf-8") as f:
        for idx, file_path in enumerate(md_files, start=1):
            f.write(f"{idx}. {file_path.stem}\n")

    print(f"Successfully extracted {len(md_files)} titles into:")
    print(f"-> {out_file.resolve()}")

if __name__ == "__main__":
    extract_uncategorized_titles()