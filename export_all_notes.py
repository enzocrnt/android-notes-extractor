import uiautomator2 as u2
import time
import os
import re

d = u2.connect()
output_dir = "my_exported_journals"
os.makedirs(output_dir, exist_ok=True)

# Load existing files to prevent re-extracting
processed_titles = set()
for existing_file in os.listdir(output_dir):
    if existing_file.endswith(".md"):
        base = os.path.splitext(existing_file)[0]
        base = re.sub(r'_\d+$', '', base)
        processed_titles.add(base)

consecutive_no_new = 0
print(f"Starting automatic export ({len(processed_titles)} already backed up)...")

def ensure_in_notes_app():
    """Ensure the notes app is actively open and in the foreground."""
    current = d.app_current().get("package", "")
    if current != "com.transsion.notebook":
        print("Notes app exited. Relaunching...")
        d.app_start("com.transsion.notebook")
        time.sleep(2.0)

ensure_in_notes_app()

while consecutive_no_new < 12:
    ensure_in_notes_app()

    title_elements = d(resourceId="com.transsion.notebook:id/title")
    found_new_in_batch = False

    titles_to_click = []
    for el in title_elements:
        try:
            t = el.get_text()
            if not t:
                continue
            short_id = re.sub(r'[\\/*?:"<>|\n\r]', "_", t)[:50].strip()
            if short_id not in processed_titles and t not in ["All", "Notes", "Recently Deleted", "Folders", "Journal", "Info", "Dream"]:
                titles_to_click.append(t)
        except Exception:
            continue

    for title in titles_to_click:
        ensure_in_notes_app()
        short_id = re.sub(r'[\\/*?:"<>|\n\r]', "_", title)[:50].strip()
        if short_id in processed_titles:
            continue

        try:
            target = d(resourceId="com.transsion.notebook:id/title", text=title)
            if not target.exists:
                continue

            print(f"--> Extracting: {title[:60]}...")
            target.click()
            time.sleep(0.8)

            # Extract full text inside note
            content_pieces = []
            for node in d(className="android.widget.EditText"):
                txt = node.get_text()
                if txt and txt not in content_pieces:
                    content_pieces.append(txt)

            if not content_pieces:
                for node in d(className="android.widget.TextView"):
                    info = node.info or {}
                    res_name = info.get("resourceName") or ""
                    if any(k in res_name for k in ["content", "editor", "text_body", "note"]):
                        txt = node.get_text()
                        if txt and txt not in content_pieces:
                            content_pieces.append(txt)

            body_text = "\n\n".join(content_pieces) if content_pieces else "(Empty Note)"

            # Safe filename capped at 50 chars
            safe_filename = short_id if short_id else f"note_{int(time.time())}"
            filepath = os.path.join(output_dir, f"{safe_filename}.md")

            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(output_dir, f"{safe_filename}_{counter}.md")
                counter += 1

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n{body_text}\n")

            processed_titles.add(short_id)
            found_new_in_batch = True

            # Safely return to note list
            d.press("back")
            time.sleep(0.5)

            # If the back button exited the app, bring it right back
            ensure_in_notes_app()

        except Exception as err:
            print(f"Error on note: {err}")
            processed_titles.add(short_id)
            # Recover navigation if stuck
            ensure_in_notes_app()

    if found_new_in_batch:
        consecutive_no_new = 0
    else:
        consecutive_no_new += 1

    # Scroll down smoothly
    ensure_in_notes_app()
    d.swipe(0.5, 0.75, 0.5, 0.25, 0.25)
    time.sleep(1.0)

print(f"\nFinished! Total extracted notes: {len(processed_titles)}")