import os
import shutil
from pathlib import Path

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

def sort_dreams():
    BASE_DIR = Path(__file__).parent
    uncategorized_dir = BASE_DIR / "uncategorized"
    dream_journal_dir = BASE_DIR / "dream_journal"

    if not uncategorized_dir.exists():
        print(f"Directory not found: {uncategorized_dir.resolve()}")
        return

    dream_journal_dir.mkdir(parents=True, exist_ok=True)
    moved_count = 0

    print("Scanning Xiaomi uncategorized for dreams...")
    for file_path in list(uncategorized_dir.glob("*.md")):
        if file_path.name.lower().startswith("dream"):
            target_file = dream_journal_dir / file_path.name
            final_path = get_unique_filepath(target_file)
            shutil.move(str(file_path), str(final_path))
            print(f"Moved: {final_path.name}")
            moved_count += 1

    print(f"\nDone! Moved {moved_count} notes to {dream_journal_dir.resolve()}")

if __name__ == "__main__":
    sort_dreams()