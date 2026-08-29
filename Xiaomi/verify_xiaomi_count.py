"""
Scans all Xiaomi subfolders, creates content hashes for every note,
and prints the true unique note count along with how many fresh notes 
in 'raw_exports' are ready to be sorted.

Output:
  - True unique note count (across all folders)
  - Duplicate breakdown
  - Number of unsorted notes waiting in raw_exports
"""

import re
import hashlib
from pathlib import Path
from collections import defaultdict

def normalize_text(text: str) -> str:
    # Strip markdown headers, tags, and collapse whitespaces
    cleaned = re.sub(r"^#\s*[^\n]+", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"Date:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\*\*Date:\*\*[^\n]*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:150]  # First 150 chars fingerprint

def get_file_hash(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        norm = normalize_text(content)
        if not norm:
            return f"empty_{file_path.stem}"
        return hashlib.md5(norm.encode("utf-8")).hexdigest()
    except Exception:
        return f"err_{file_path.name}"

def run_deep_check():
    base_dir = Path(__file__).parent
    folders = ["journal_entries", "uncategorized", "dream_journal", "raw_exports"]

    signatures = defaultdict(list)
    folder_counts = {}

    for folder_name in folders:
        folder_path = base_dir / folder_name
        if folder_path.exists():
            files = list(folder_path.glob("*.md"))
            folder_counts[folder_name] = len(files)
            for f in files:
                sig = get_file_hash(f)
                signatures[sig].append((folder_name, f.name))
        else:
            folder_counts[folder_name] = 0

    # Categorized vs Raw analysis
    already_sorted_sigs = set()
    for sig, locs in signatures.items():
        if any(loc[0] in ["journal_entries", "uncategorized", "dream_journal"] for loc in locs):
            already_sorted_sigs.add(sig)

    pending_in_raw = 0
    for sig, locs in signatures.items():
        if sig not in already_sorted_sigs and any(loc[0] == "raw_exports" for loc in locs):
            pending_in_raw += 1

    total_unique_notes = len(signatures)

    print("=== Xiaomi Deep Notes Verification ===\n")
    for f_name, count in folder_counts.items():
        print(f"- {f_name:18}: {count} files")

    print("\n----------------------------------------")
    print(f"Total Unique Notes Extracted        : {total_unique_notes}")
    print(f"Already Sorted (Journal/Uncat/Dream): {len(already_sorted_sigs)}")
    print(f"New Unsorted Notes in raw_exports   : {pending_in_raw}")
    print("----------------------------------------\n")
    print("Compare the 'Total Unique Notes Extracted' with the count in your Xiaomi Notes app.")

if __name__ == "__main__":
    run_deep_check()