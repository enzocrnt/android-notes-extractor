# android-notes-extractor

An automated Python toolchain to extract, parse, standardize, and sort notes from OEM Android applications (Tecno HiOS Notebook & Xiaomi MIUI/HyperOS Notes) into clean, chronologically organized Markdown files via ADB and UI Automator.

## Overview

Stock Android notes applications often restrict direct cloud export, lack bulk export features, and isolate personal data inside private application databases (`/data/data/`) with backup flags disabled.

`android-notes-extractor` automates screen traversal over an Android Debug Bridge (ADB) connection. The tool opens each entry programmatically, extracts full text and timestamps from internal UI widgets, sanitizes filenames to prevent OS path errors, and standardizes multi-part entries. The exported notes are formatted into clean Markdown (`.md`) files ready for local archiving or import into Obsidian, Notion, Logseq, and Google Drive.

## Repository Directory Structure

```text
android-notes-extractor/
│
├── Tecno/
│   ├── export_tecno_notes.py                  # Automates HiOS Notebook UI extraction
│   ├── journal_sorter_tecno.py                # Sorts dated notes into journal_entries vs uncategorized
│   ├── recover_missed_journals_tecno.py       # Scans uncategorized note bodies for missed date stamps
│   ├── continuation_renamer_tecno.py          # Standardizes multi-part entries ([P1], [P2], [P3])
│   ├── extract_uncategorized_tecno.py         # Dumps uncategorized note titles to text file
│   └── interactive_sorter_tecno.py            # Interactive CLI sorter with live commenting feature
│
├── Xiaomi/
│   ├── export_xiaomi_notes.py                 # Automates MIUI/HyperOS Notes UI extraction
│   ├── sweep_missing_xiaomi.py                # Deep UI sweep to recover skipped entries
│   ├── journal_sorter_xiaomi.py               # Formats dated Xiaomi entries into MM-DD-YYYY
│   ├── auto_categorizer_xiaomi.py             # Rule-based auto-sorter for common note categories
│   ├── extract_uncategorized_titles_xiaomi.py # Extracts uncategorized titles for batch analysis
│   └── interactive_sorter_xiaomi.py           # Interactive CLI sorter for Xiaomi uncategorized notes
│
├── backups/                                   # Raw backup archives
├── requirements.txt
├── .gitignore
└── README.md

```

## Features

* **Dual-OEM Support:** Dedicated extraction pipelines tailored for both Transsion/Tecno HiOS Notebook (`com.transsion.notebook`) and Xiaomi MIUI/HyperOS Notes (`com.miui.notes`).
* **Automated UI Traversal:** Programmatically iterates through lists, opens individual entries, triggers clipboard share targets or widget scraping, and handles vertical scroll batches.
* **Intelligent Date Parsing:** Converts word-based and varied date stamps (`Nov. 4, 2023`, `Sept. 20, 2023`) into standard `MM-DD-YYYY` formats for chronological sorting.
* **Multi-Day & Multi-Part Formatting:** Handles multi-day span titles (e.g., `11-20-2024 - [Nov. 20-21] ...`) and continuation tags (`[P1]`, `[P2]`, `[P3]`).
* **Interactive CLI Sorter & Reflection Tool:** Single-keypress terminal interface to sort notes into dedicated category subfolders (`misc/`) with live note preview, undo history (`[B]`), and interactive "future self" commenting (`[C]`).
* **Content Spacing Standardization:** Automatically ensures standardized 3-line separation (`\n\n\n`) between title headers and note bodies across all exports.
* **Local & Secure:** Operates entirely over USB via ADB without transmitting personal notes to external servers.

## Prerequisites

* Python 3.10 or higher
* Android Platform Tools (`adb`) installed and configured in system `PATH`
* Target Android device with **Developer Options** and **USB Debugging** enabled

### Enabling Developer Mode and USB Debugging

#### Step 1: Enable Developer Options

1. Open **Settings** on your Android device.
2. Scroll down and select **About Phone** (or **My Phone**).
3. Locate **Build Number**.
4. Tap **Build Number** 7 times continuously until a pop-up appears stating *"You are now a developer!"* (Enter your PIN/password if prompted).

#### Step 2: Enable USB Debugging

1. Go to **Settings** > **System** > **Developer Options** (or **Additional Settings** > **Developer Options**).
2. Toggle **USB Debugging** to **ON** and confirm.
3. Connect your phone to your PC via USB cable.
4. When the *"Allow USB debugging?"* prompt appears, check **Always allow from this computer** and tap **Allow**.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/android-notes-extractor.git
cd android-notes-extractor

```

2. Install dependencies:

```bash
pip install -r requirements.txt

```

3. Verify ADB connection:

```bash
adb devices

```

---

## Usage Workflow

### 1. Tecno Extraction & Processing

```bash
# 1. Run extraction from Tecno HiOS Notebook
python .\Tecno\export_tecno_notes.py

# 2. Sort dated entries to journal_entries and the rest to uncategorized
python .\Tecno\journal_sorter_tecno.py

# 3. Recover any journals where dates were inside note bodies
python .\Tecno\recover_missed_journals_tecno.py

# 4. Standardize multi-part continuations ([P1], [P2])
python .\Tecno\continuation_renamer_tecno.py

# 5. Extract remaining uncategorized titles for review
python .\Tecno\extract_uncategorized_tecno.py

# 6. Interactively sort remaining uncategorized notes into misc folders
python .\Tecno\interactive_sorter_tecno.py

```

### 2. Xiaomi Extraction & Processing

```bash
# 1. Run extraction from Xiaomi Notes
python .\Xiaomi\export_xiaomi_notes.py

# 2. Run sweep to catch any notes skipped during rapid scrolling
python .\Xiaomi\sweep_missing_xiaomi.py

# 3. Sort dated notes into journal_entries
python .\Xiaomi\journal_sorter_xiaomi.py

# 4. Run automated category sorter (Dreams, Food, Commute, Acads, etc.)
python .\Xiaomi\auto_categorizer_xiaomi.py

# 5. Extract remaining uncategorized note titles to text file
python .\Xiaomi\extract_uncategorized_titles_xiaomi.py

# 6. Interactively sort remaining notes with live reflection commenting
python .\Xiaomi\interactive_sorter_xiaomi.py

```

---

## Output Format Example

```markdown
# Sample Note Title

**Date:** Jun. 22, 2024



Sample body text extracted from the mobile application...

---
### 💬 Comment galing sa future self mo:
**Date & Time:** Aug. 30, 2026 | 10:35 PM

Reflections added during sorting...

```

## License

MIT