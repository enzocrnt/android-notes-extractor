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

# Scan all Xiaomi subfolders to avoid re-exporting notes
all_xiaomi_folders = [
    output_dir,
    BASE_DIR / "journal_entries",
    BASE_DIR / "uncategorized",
    BASE_DIR / "dream_journal"
]

processed_signatures = set()
for folder in all_xiaomi_folders:
    if folder.exists():
        for fpath in folder.glob("*.md"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    txt = f.read()
                    norm_snippet = re.sub(r'\s+', ' ', txt).strip()[:120]
                    if norm_snippet:
                        processed_signatures.add(norm_snippet)
            except Exception:
                pass

print(f"Starting Xiaomi Notes fast extractor. Found {len(processed_signatures)} indexed notes across folders.")

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
        time.sleep(0.3)
    
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
        if selector.wait(timeout=1.2):
            share_btn = selector
            break

    if not share_btn:
        return ""

    share_btn.click()
    text_option = d(text="Share note as text")
    if text_option.wait(timeout=2.5):
        text_option.click()

    time.sleep(0.35)
    copy_option = d(text="Copy to clipboard")
    if not copy_option.exists:
        d.swipe(850, 1900, 150, 1900, duration=0.2)
        time.sleep(0.25)
        copy_option = d(text="Copy to clipboard")

    if copy_option.wait(timeout=2.5):
        d.set_clipboard("")
        copy_option.click()
        
        for _ in range(12):
            time.sleep(0.12)
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
                
                if top < 120 or bottom > 2200:
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

stuck_count = 0
prev_first_sig = ""
total_exported = 0

while True:
    return_to_notes_list()

    cards = get_visible_cards()
    if not cards:
        print("No note cards found on screen.")
        break

    current_first_sig = f"{cards[0]['top']}_{cards[0]['preview'][:25]}"
    found_new_on_screen = False

    for card in cards:
        card_preview_norm = re.sub(r'\s+', ' ', card['preview']).strip()
        
        is_already_exported = False
        if card_preview_norm:
            for sig in processed_signatures:
                if card_preview_norm[:60] in sig or sig[:60] in card_preview_norm:
                    is_already_exported = True
                    break

        if is_already_exported:
            continue

        try:
            if not d(resourceId="com.miui.notes:id/note_group").exists:
                return_to_notes_list()

            d.click(card['cx'], card['cy'])
            time.sleep(0.45)

            if d(resourceId="com.miui.notes:id/note_group").exists:
                d.click(card['cx'], card['cy'])
                time.sleep(0.45)

            raw_text = trigger_copy_to_clipboard()

            if not raw_text:
                edit_texts = d(className="android.widget.EditText")
                if edit_texts.count > 0:
                    raw_text = "\n\n".join(e.get_text() for e in edit_texts if e.get_text() and e.get_text() != "Title")

            if not raw_text.strip():
                return_to_notes_list()
                continue

            content_norm = re.sub(r'\s+', ' ', raw_text).strip()
            content_sig = content_norm[:120]
            if content_sig in processed_signatures:
                return_to_notes_list()
                continue

            smart_title = get_smart_title(raw_text, fallback=card['preview'] if card['preview'] else "Untitled")
            safe_filename_base = sanitize_filename(smart_title)
            
            filepath = output_dir / f"{safe_filename_base}.md"
            counter = 1
            while filepath.exists():
                filepath = output_dir / f"{safe_filename_base}_{counter}.md"
                counter += 1

            date_header = f"Date:\n\n" if card['date'] else ""
            content = f"# {smart_title}\n\n{date_header}{raw_text.strip()}\n"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            processed_signatures.add(content_sig)
            total_exported += 1
            print(f"--> Extracted: {smart_title[:45]}")
            found_new_on_screen = True

            return_to_notes_list()

        except Exception as e:
            print(f"Error during extraction: {e}")
            return_to_notes_list()

    if current_first_sig == prev_first_sig and not found_new_on_screen:
        stuck_count += 1
        if stuck_count >= 3:
            print("Reached the bottom of the notes list.")
            break
    else:
        stuck_count = 0

    prev_first_sig = current_first_sig
    d.swipe(500, 1400, 500, 750, duration=0.3)
    time.sleep(0.7)

print(f"\nExtraction complete! Saved to {output_dir.resolve()}")