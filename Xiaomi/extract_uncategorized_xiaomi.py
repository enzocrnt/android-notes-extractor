import os
from pathlib import Path

def extract_titles():
    BASE_DIR = Path(__file__).parent
    uncategorized_dir = BASE_DIR / "uncategorized"
    output_file = BASE_DIR / "uncategorized_titles.txt"

    if not uncategorized_dir.exists():
        print(f"Directory not found: {uncategorized_dir.resolve()}")
        return

    md_files = sorted(list(uncategorized_dir.glob("*.md")), key=lambda p: p.name.lower())
    if not md_files:
        print("No .md files found in Xiaomi uncategorized folder.")
        return

    titles = [f.stem for f in md_files]
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(titles))

    print(f"Exported {len(titles)} titles to '{output_file.resolve()}'")

if __name__ == "__main__":
    extract_titles()