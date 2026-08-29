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
│   ├── export_tecno_notes.py              # Automates HiOS Notebook UI extraction
│   ├── journal_sorter_tecno.py            # Sorts notes into journal entries vs uncategorized
│   ├── continuation_renamer_tecno.py      # Groups multi-part entries as [P1], [P2], [P3]
│   ├── process_numeric_continuations_tecno.py
│   └── extract_uncategorized_tecno.py     # Dumps uncategorized note titles for review
│
├── Xiaomi/
│   ├── export_xiaomi_notes.py             # Automates MIUI/HyperOS Notes UI extraction
│   ├── sweep_missing_xiaomi.py            # Deep body-fingerprint sweep to recover skipped notes
│   ├── journal_sorter_xiaomi_.py          # Formats dated Xiaomi entries into MM-DD-YYYY
│   ├── dream_sorter_xiaomi.py             # Extracts dream logs into dedicated dream journal
│   ├── extract_uncategorized_xiaomi.py    # Dumps uncategorized note titles for review
│   └── verify_xiaomi_count.py             # Deep verification and content hash counter
│
├── backups/                               # Raw backup archives
├── requirements.txt
├── .gitignore
└── README.md

```

## Features

* **Dual-OEM Support:** Dedicated extraction pipelines tailored for both Transsion/Tecno HiOS Notebook (`com.transsion.notebook`) and Xiaomi MIUI/HyperOS Notes (`com.miui.notes`).
* **Automated UI Traversal:** Programmatically iterates through lists, opens individual entries, triggers clipboard share targets or widget scraping, and handles vertical scroll batches.
* **Intelligent Date Parsing:** Converts word-based and varied date stamps (`Nov. 4, 2023`, `Sept. 20, 2023`) into standard `MM-DD-YYYY` formats for chronological sorting.
* **Multi-Part / Continuation Grouping:** Detects long split entries (`Continuation ng...`), links them to the day's main entry, and formats them into sequential tags (`[P1]`, `[P2]`, `[P3]`).
* **Content Fingerprinting & Deduplication:** Generates normalized text hashes to prevent duplicate extraction on repeated runs.
* **Deep Recovery Sweeps:** Sweeper module with relaxed screen boundaries and slow scroll stepping to catch missed notes.
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

# 3. Format and link multi-part continuations ([P1], [P2], [P3])
python .\Tecno\continuation_renamer_tecno.py
python .\Tecno\process_numeric_continuations_tecno.py

# 4. Extract remaining uncategorized note titles for manual review
python .\Tecno\extract_uncategorized_tecno.py

```

### 2. Xiaomi Extraction & Processing

```bash
# 1. Run extraction from Xiaomi Notes
python .\Xiaomi\export_xiaomi_notes.py

# 2. Run precision sweep to recover any missed notes
python .\Xiaomi\sweep_missing_xiaomi.py

# 3. Verify total unique note counts against your Xiaomi Notes app counter
python .\Xiaomi\verify_xiaomi_count.py

# 4. Sort dated notes into journal_entries
python .\Xiaomi\journal_sorter_xiaomi_.py

# 5. Extract dream journal entries
python .\Xiaomi\dream_sorter_xiaomi.py

# 6. Extract remaining uncategorized note titles for review
python .\Xiaomi\extract_uncategorized_xiaomi.py

```

---

## Output Format Example

```markdown
04-28-2024 - [P1] Sample Note Title



Sample body text extracted from the mobile application...

```

## License

MIT