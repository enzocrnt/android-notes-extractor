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
└── exported_notes/
    ├── notes sample 1.md
    ├── notes sample 2.md
    ├── notes sample 3.md
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
* Target Android device with **Developer Options** and **USB Debugging** enabled

### Enabling Developer Mode and USB Debugging

#### Step 1: Enable Developer Options

1. Open **Settings** on your Android device.
2. Scroll down and select **About Phone** (or **My Phone**).
3. Locate **Build Number**.
4. Tap **Build Number** 7 times continuously until a pop-up appears stating *"You are now a developer!"* (Enter your device lock PIN/password if prompted).

#### Step 2: Enable USB Debugging

1. Go back to the main **Settings** menu.
2. Navigate to **System** > **Developer Options** (on some devices, this is located under **Additional Settings**).
3. Scroll down to the **Debugging** section.
4. Toggle the switch next to **USB Debugging** to **ON** and confirm the prompt.
5. Connect your phone to your computer via USB cable. When the *"Allow USB debugging?"* prompt appears on your phone screen, check **Always allow from this computer** and tap **Allow**.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/enzocrnt/android-notes-extractor.git
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

## Disclaimer

This tool is specifically tailored for devices running Transsion/Tecno HiOS Notebook (`com.transsion.notebook`). Due to differences in UI node hierarchies, view resource IDs, and package naming conventions across Android manufacturers (e.g., Samsung Notes, Xiaomi Notes, ColorOS), this script may not work out-of-the-box on every Android device without modifying the target resource IDs in `export_all_notes.py`.

## License

MIT