import uiautomator2 as u2
import os
import time
import re

d = u2.connect()

output_dir = "exported_notes"
os.makedirs(output_dir, exist_ok=True)

processed_files = set(os.listdir(output_dir))
total_exported = len(processed_files)

APP_PKG = "com.transsion.notebook"
APP_ACT = "com.transsion.notebook.activity.MainActivity"

def sanitize_filename(title, max_length=50):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    sanitized = re.sub(r'\s+', ' ', sanitized)
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    return sanitized if sanitized else "Untitled"

def ensure_app_foreground():
    current = d.app_current()
    if current.get('package') != APP_PKG:
        print("Notes app exited. Relaunching...")
        d.app_start(APP_PKG, APP_ACT)
        time.sleep(1.5)

print(f"Starting extraction. Found {total_exported} previously exported notes.")

stuck_count = 0
prev_first_title = ""

while True:
    ensure_app_foreground()
    
    note_cards = d(resourceId="com.transsion.notebook:id/note_card")
    count = note_cards.count
    
    if count == 0:
        print("No note cards visible.")
        break

    current_first_title = ""
    try:
        title_widget = note_cards[0].child(resourceId="com.transsion.notebook:id/note_title")
        if title_widget.exists:
            current_first_title = title_widget.get_text()
    except Exception:
        pass

    found_new = False

    for i in range(count):
        try:
            card = note_cards[i]
            if not card.exists:
                continue

            card.click()
            time.sleep(0.4)

            title_elem = d(resourceId="com.transsion.notebook:id/title_content")
            date_elem = d(resourceId="com.transsion.notebook:id/date_content")
            body_elem = d(resourceId="com.transsion.notebook:id/note_content_view")

            title = title_elem.get_text() if title_elem.exists else "Untitled"
            date_str = date_elem.get_text() if date_elem.exists else ""
            body = body_elem.get_text() if body_elem.exists else ""

            safe_title = sanitize_filename(title)
            filename = f"{safe_title}.md"
            filepath = os.path.join(output_dir, filename)

            if filename not in processed_files:
                counter = 1
                while os.path.exists(filepath):
                    filename = f"{safe_title}_{counter}.md"
                    filepath = os.path.join(output_dir, filename)
                    counter += 1

                content = f"# {title}\n"
                if date_str:
                    content += f"**Date:** {date_str}\n\n"
                else:
                    content += "\n"
                content += body

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

                processed_files.add(filename)
                total_exported += 1
                preview = title[:50] + "..." if len(title) > 50 else title
                print(f"--> Extracting: {preview}")
                found_new = True

            d.press("back")
            time.sleep(0.2)

        except Exception as e:
            print(f"Error during note extraction: {e}")
            d.press("back")
            time.sleep(0.3)

    if current_first_title == prev_first_title and not found_new:
        stuck_count += 1
        if stuck_count >= 3:
            print("Reached the bottom of notes list.")
            break
    else:
        stuck_count = 0

    prev_first_title = current_first_title

    d.swipe(500, 1800, 500, 600, duration=0.25)
    time.sleep(0.5)

print(f"\nFinished! Total extracted notes: {total_exported}")