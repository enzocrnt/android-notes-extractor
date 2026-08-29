Here is the updated `README.md` structured cleanly to match your previous repository format without icons or emojis:

```markdown
# android-notes-extractor

An automated Python tool to extract, parse, and export notes from OEM Android applications into organized Markdown files via ADB and UI Automator.

## Overview

Stock Android notes applications (such as Tecno HiOS Notebook) often restrict direct cloud export and isolate data inside private application databases (`/data/data/`) with backup flags disabled. 

`android-notes-extractor` automates screen traversal over an Android Debug Bridge (ADB) connection. The tool opens each entry programmatically, extracts the full text and metadata from internal UI widgets, sanitizes file paths to prevent operating system path errors, and outputs clean Markdown (`.md`) files ready for local archiving or import into applications like Obsidian, Notion, and Google Drive.

## Output Directory Structure

```text
android-notes-extractor/
├── export_all_notes.py
├── requirements.txt
└── my_exported_journals/
    ├── 08-17-2026 - First Day of Classes.md
    ├── 08-13-2026 - Welcome Walk Event.md
    ├── Cisco Lab Test Review.md
    └── ...

```

## Features

* Automated UI traversal: programmatically iterates through lists, opens individual entries, and handles scrolling automatically.
* Full-text parsing: retrieves complete title, timestamp, and multiline text bodies from internal editor nodes.
* Filename sanitization: truncates long titles and strips invalid filesystem characters to prevent path length exceptions (`Errno 22`).
* Navigation state recovery: automatically detects accidental app minimization and brings the target package back to the foreground.
* Duplicate detection: scans existing files in the target directory on launch to prevent re-extracting previously saved notes.
* Local execution: operates entirely over USB via ADB without transmitting personal notes to external servers.

## Prerequisites

* Python 3.10 or higher
* Android Platform Tools (`adb`) installed and configured in system `PATH`
* Target Android device connected via USB with **USB Debugging** enabled

## Setup

1. Clone the repository:
```bash
git clone [https://github.com/your-username/android-notes-extractor.git](https://github.com/your-username/android-notes-extractor.git)
cd android-notes-extractor

```


2. Install the required dependencies:
```bash
pip install -r requirements.txt

```


3. Verify ADB connection:
```bash
adb devices

```



## Usage

### Run Full Extraction Pipeline

Open your notes application on the phone to the desired folder or note list, then execute:

```bash
python export_all_notes.py

```

### Resume Interrupted Extraction

If the process is stopped, re-running the command resumes extraction and skips already exported files:

```bash
python export_all_notes.py

```

## License

MIT

```

```