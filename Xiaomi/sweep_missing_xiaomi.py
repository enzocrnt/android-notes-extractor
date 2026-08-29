"""
sweep_missing_xiaomi.py
========================
Sweeps Xiaomi Notes to find and export ONLY the ~20 missing notes.
Uses deep body-content normalization (ignoring date formatting differences,
headers, and markdown tags) to prevent re-extracting previously renamed notes.

Before:
  - Missed ~20 notes due to scroll skips or boundary cutoffs.
  - Previous sweep falsely re-downloaded notes whose headers changed to MM-DD-YYYY.

After:
  - Accurately identifies and saves only truly missing notes to 'Xiaomi/raw_exports/'.
  - Completely skips notes that exist in journal_entries, uncategorized, or dream_journal.
"""

import uiautomator2 as u2
import os
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path

d = u2.connect()

BASE_DIR = Path(__file__).parent
output_dir = BASE_DIR / "raw_exports"
output_dir.mkdir(parents=True, exist_ok=True)

# Helper to strip dates, headers, and punctuation for pure body comparison
def get_clean_fingerprint(text: str) -> str:
    # 1. Remove Markdown headers & 'Date:' tags
    cleaned = re.sub(r"^#.*$", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*Date:\*\*.*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"Date:\s*", "", cleaned, flags=re.IGNORECASE)

    # 2. Remove date patterns (both MM-DD-YYYY and Text Months)
    date_pattern = r"(?:\d{2}-\d{2}-\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{2,4})"
    cleaned = re.sub(date_pattern, "", cleaned, flags=re.IGNORECASE)

    # 3. Keep only alphanumeric characters (ignores punctuation/spacing shifts)
    alphanumeric = re.sub(r"[^a-zA-Z0-9\u00C0-\u017F]", "", cleaned.lower())
    
    # Return first 100 meaningful characters of note body
    return alphanumeric[:100]

# 1. Index pure body fingerprints from ALL existing folders
all_folders = [
    output_dir,
    BASE_DIR / "journal_entries",
    BASE_DIR / "uncategorized",
    BASE_DIR / "dream_journal"
]

known_body_fingerprints = set()
for folder in all_folders:
    if folder.exists():
        for fpath in folder.glob("*.md"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    fp = get_clean_fingerprint(f.read())
                    if len(fp) >= 10:  # Ignore empty stubs
                        known_body_fingerprints.add(fp)
            except Exception:
                pass

print(f"Indexed {len(known_body_fingerprints)} unique note bodies across all folders.")
print("Starting precision sweep for missing notes...\n")

APP_PKG = "com.miui.notes"
APP_ACT = "com.miui.notes.ui.NotesListActivity"

def sanitize_filename(title, max_length=60):
    sanitized = re.sub(r'[\\/*?:"<>|\r\n]', "", title).strip()
    sanitized = re.sub(r'\s+', ' ', sanitized)
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    return sanitized.rstrip(". ") if sanitized else "Untitled"

def get_smart_title(raw_text, fallback="Untitled"):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip() and not l.startswith("**Date:")]
    if not lines:
        return fallback

    date_pattern = r'^(?:(?:Sept?|Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|August|September)\.?\s+\d{1,2},?\s+\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{2,4}|\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4})$'
    if len(lines) > 1 and re.match(date_pattern, lines[0].strip(), re.IGNORECASE):
        return f"{lines[0]} - {lines[1]}"
    return lines[0]

def return_to_notes_list():
    for _ in range(4):
        if d(resourceId="com.miui.notes:id/note_group").exists:
            return True
        d.press("back")
        time.sleep(0.25)
    
    d.app_start(APP_PKG, APP_ACT)
    time.sleep(1.0)
    return d(resourceId="com.miui.notes:id/note_group").exists

def trigger_copy_to_clipboard():
    time.sleep(0.35)
    share_btn = None
    for selector in [
        d(description="Share this note"),
        d(resourceId="com.miui.notes:id/share"),
        d(resourceId="com.miui.notes:id/action_menu_item_child_icon")
    ]:
        if selector.wait(timeout=1.0):
            share_btn = selector
            break

    if not share_btn:
        return ""

    share_btn.click()
    text_option = d(text="Share note as text")
    if text_option.wait(timeout=2.0):
        text_option.click()

    time.sleep(0.3)
    copy_option = d(text="Copy to clipboard")
    if not copy_option.exists:
        d.swipe(850, 1900, 150, 1900, duration=0.2)
        time.sleep(0.2)
        copy_option = d(text="Copy to clipboard")

    if copy_option.wait(timeout=2.0):
        d.set_clipboard("")
        copy_option.click()
        for _ in range(10):
            time.sleep(0.1)
            clip = d.clipboard.strip()
            if clip:
                return clip
    return ""

def get_visible_cards():
    xml_data = d.dump_hierarchy()
    root = ET.fromstring(xml_data)
    cards = []

    for node in root.iter('node'):
        if node.attrib.get('resource-id') == 'com.miui.notes:id/note_group':
            bounds = node.attrib.get('bounds', '')
            m = re.findall(r'\[(\d+),(\d+)\]', bounds)
            if len(m) == 2:
                left, top = int(m[0][0]), int(m[0][1])
                right, bottom = int(m[1][0]), int(m[1][1])
                
                # Relaxed bounds to capture top/bottom cards
                if top < 80 or bottom > 2320:
                    continue
                
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2

                preview_text = ""
                date_text = ""
                for child in node.iter('node'):
                    c_res = child.attrib.get('resource-id', '')
                    c_txt = child.attrib.get('text', '').strip()
                    if 'preview' in c_res and c_txt:
                        preview_text = c_txt
                    elif 'time' in c_res and c_txt:
                        date_text = c_txt

                cards.append({
                    'top': top,
                    'left': left,
                    'cx': center_x,
                    'cy': center_y,
                    'preview': preview_text,
                    'date': date_text
                })

    cards.sort(key=lambda c: (c['top'] // 160, c['left']))
    return cards

# Scroll to the top of Xiaomi notes
d.app_start(APP_PKG, APP_ACT)
time.sleep(1.0)
for _ in range(4):
    d.swipe(500, 500, 500, 1800, duration=0.2)
    time.sleep(0.25)

recovered_count = 0
stuck_count = 0
prev_first_sig = ""

while True:
    return_to_notes_list()
    cards = get_visible_cards()
    if not cards:
        break

    current_first_sig = f"{cards[0]['top']}_{cards[0]['preview'][:25]}"
    found_new = False

    for card in cards:
        card_fp = get_clean_fingerprint(card['preview'])

        # Pre-check: skip clicking if card preview text already matches an indexed body
        if len(card_fp) >= 15 and card_fp in known_body_fingerprints:
            continue

        try:
            d.click(card['cx'], card['cy'])
            time.sleep(0.35)

            if d(resourceId="com.miui.notes:id/note_group").exists:
                d.click(card['cx'], card['cy'])
                time.sleep(0.35)

            raw_text = trigger_copy_to_clipboard()
            if not raw_text:
                edit_texts = d(className="android.widget.EditText")
                if edit_texts.count > 0:
                    raw_text = "\n\n".join(e.get_text() for e in edit_texts if e.get_text() and e.get_text() != "Title")

            if not raw_text.strip():
                return_to_notes_list()
                continue

            full_body_fp = get_clean_fingerprint(raw_text)

            # Deep verification: if this note body exists anywhere, skip it immediately!
            if full_body_fp and full_body_fp in known_body_fingerprints:
                return_to_notes_list()
                continue

            # Found a truly missing note!
            smart_title = get_smart_title(raw_text, fallback=card['preview'] if card['preview'] else "Untitled")
            safe_filename = sanitize_filename(smart_title)
            
            filepath = output_dir / f"{safe_filename}.md"
            counter = 1
            while filepath.exists():
                filepath = output_dir / f"{safe_filename}_{counter}.md"
                counter += 1

            date_header = f"Date:\n\n" if card['date'] else ""
            content = f"# {smart_title}\n\n{date_header}{raw_text.strip()}\n"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            if full_body_fp:
                known_body_fingerprints.add(full_body_fp)

            recovered_count += 1
            found_new = True
            print(f"[RECOVERED #{recovered_count}] {smart_title[:45]}")

            return_to_notes_list()

        except Exception as e:
            return_to_notes_list()

    if current_first_sig == prev_first_sig and not found_new:
        stuck_count += 1
        if stuck_count >= 3:
            print("Completed sweep at the bottom of the list.")
            break
    else:
        stuck_count = 0

    prev_first_sig = current_first_sig

    # Slow, controlled scroll step
    d.swipe(500, 1300, 500, 850, duration=0.4)
    time.sleep(0.7)

print(f"\nDone! Recovered {recovered_count} truly missing notes into Xiaomi/raw_exports/")