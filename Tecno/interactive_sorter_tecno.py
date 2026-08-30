"""
interactive_sorter_tecno.py
============================
An interactive CLI tool that iterates through every note in 'Tecno/uncategorized',
displays its entire text content, and prompts for single-key sorting or live commenting.

Features:
  - Full text preview without truncation
  - [C] Add Comment: Appends a formatted reflection block with custom Date & Time
  - Instant routing into dedicated category folders
  - [B] Undo support to return previous note back to uncategorized

Category Mappings:
  Row 1: [1] Stub / Trash      [2] Important / Accounts  [3] Rant             [4] Journal
  Row 2: [Q] Commute           [W] Finance / Shopping    [E] Acads            [R] Fitness & Health
  Row 3: [A] Food              [D] Dream                 [C] Add Comment      [Space] Skip Note
  Row 4: [B] Undo Last Move    [X] Exit Sorter
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Setup Windows/Unix single-character non-blocking key reader
if os.name == "nt":
    import msvcrt

    def get_key():
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):  # Function / Arrow keys
            msvcrt.getch()
            return ""
        try:
            return ch.decode("utf-8")
        except UnicodeDecodeError:
            return ""
else:
    import termios
    import tty

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def interactive_sorter():
    BASE_DIR = Path(__file__).parent
    uncat_dir = BASE_DIR / "uncategorized"

    if not uncat_dir.exists():
        print(f"Error: Directory not found: {uncat_dir.resolve()}")
        return

    # Folder mappings according to your exact keys
    category_map = {
        "1": ("Stub / Trash", BASE_DIR / "stubs_trash"),
        "2": ("Important / Accounts", BASE_DIR / "important_accounts"),
        "3": ("Rant", BASE_DIR / "rants"),
        "4": ("Journal", BASE_DIR / "manual_journals"),
        "q": ("Commute", BASE_DIR / "commute"),
        "w": ("Finance / Shopping", BASE_DIR / "finance_shopping"),
        "e": ("Acads", BASE_DIR / "acads"),
        "r": ("Fitness & Health", BASE_DIR / "fitness_health"),
        "a": ("Food", BASE_DIR / "food"),
        "d": ("Dream", BASE_DIR / "dream_journal"),
    }

    # Ensure target folders exist
    for _, folder_path in category_map.values():
        folder_path.mkdir(parents=True, exist_ok=True)

    files = sorted(list(uncat_dir.glob("*.md")), key=lambda p: p.name.lower())
    total_files = len(files)

    if total_files == 0:
        print("No markdown files found in 'Tecno/uncategorized' to sort.")
        return

    history = []  # Stack of (src_path, dst_path) for Undo feature
    index = 0

    while index < len(files):
        current_file = files[index]

        # If file was already moved in a previous step, skip it
        if not current_file.exists():
            index += 1
            continue

        try:
            with open(current_file, "r", encoding="utf-8") as f:
                raw_content = f.read()
        except Exception as e:
            raw_content = f"[Error reading file content: {e}]"

        clear_screen()
        print("=" * 96)
        print(f" NOTE [{index + 1}/{total_files}]: {current_file.name}")
        print("=" * 96)
        
        # Display the entire note content
        print(raw_content)
        
        print("\n" + "-" * 96)
        print(f" {'[1] Stub / Trash':<23} {'[2] Important / Accounts':<26} {'[3] Rant':<20} {'[4] Journal':<20}")
        print(f" {'[Q] Commute':<23} {'[W] Finance / Shopping':<26} {'[E] Acads':<20} {'[R] Fitness & Health':<20}")
        print(f" {'[A] Food':<23} {'[D] Dream':<26} {'[C] Add Comment':<20} {'[Space] Skip Note':<20}")
        print(f" {'[B] Undo Last Move':<23} {'[X] Exit Sorter':<26}")
        print("-" * 96)
        print("Press a key to sort: ", end="", flush=True)

        key = get_key().lower()

        if key == "x":
            clear_screen()
            print("Exited sorter. Progress saved!")
            break

        elif key == "b":
            if history:
                prev_src, prev_dst = history.pop()
                if prev_dst.exists():
                    shutil.move(str(prev_dst), str(prev_src))
                    print(f"\nUndid move: Returned {prev_src.name} to uncategorized.")
                index = max(0, index - 1)
            else:
                print("\nNo previous moves to undo!")
            continue

        elif key == "c":
            print("\n" + "-" * 80)
            print("Write your comment below (or press Enter without typing to cancel):\n")
            try:
                user_comment = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                user_comment = ""

            if user_comment:
                # Format: Aug. 30, 2026 | 10:35 PM
                now = datetime.now()
                month_abbr = now.strftime("%b")
                date_str = f"{month_abbr}. {now.strftime('%d, %Y | %I:%M %p')}"
                
                comment_block = (
                    f"\n\n---\n"
                    f"### 💬 Comment galing sa future self mo:\n"
                    f"**Date & Time:** {date_str}\n\n"
                    f"{user_comment}\n"
                )
                
                try:
                    with open(current_file, "a", encoding="utf-8") as f:
                        f.write(comment_block)
                except Exception as e:
                    print(f"\n[Error saving comment: {e}]")
            else:
                print("\n[Canceled. No changes made.]")

            # Stay on current note to inspect refreshed preview
            continue

        elif key == " ":
            # Skip / leave in uncategorized
            index += 1
            continue

        elif key in category_map:
            cat_name, target_folder = category_map[key]
            target_path = target_folder / current_file.name
            
            # Avoid overwriting duplicates in target folder
            counter = 1
            while target_path.exists():
                target_path = target_folder / f"{current_file.stem}_{counter}.md"
                counter += 1

            shutil.move(str(current_file), str(target_path))
            history.append((current_file, target_path))
            index += 1

        else:
            # Invalid key pressed, loop and ask again
            continue

    clear_screen()
    remaining = len(list(uncat_dir.glob("*.md")))
    print("=" * 96)
    print(" CATEGORIZATION SESSION COMPLETE")
    print("=" * 96)
    print(f"Total processed in this session : {index}")
    print(f"Remaining in uncategorized      : {remaining}")
    print("=" * 96 + "\n")

if __name__ == "__main__":
    interactive_sorter()