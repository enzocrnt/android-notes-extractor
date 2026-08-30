"""
auto_categorizer_xiaomi.py
===========================
Automatically sorts high-confidence note titles from 'Xiaomi/uncategorized'
into their dedicated subfolders:
  - dream_journal/
  - food/
  - commute/
  - acads/
  - fitness_health/
  - media_entertainment/
  - important_accounts/
  - finance_shopping/
  - stubs_trash/
"""

import os
import re
import shutil
from pathlib import Path

# Explicit keyword and prefix definitions
CATEGORIES = {
    "dream_journal": {
        "prefixes": ["dream ", "dream_", "dream", "dteamq "],
        "exact": ["dream", "dream_1"]
    },
    "food": {
        "prefixes": ["starbucks", "wendy's", "zagu", "big brew", "mylk tea"],
        "exact": [
            "amici", "andy's", "angel's burger", "aristocrat visitors (22)", 
            "aristocrat visitors (22)_1", "army navy", "art bar", "big brew", 
            "big brew_1", "cabalen visitors", "cake", "coffee", "coffee bean & tea leaf", 
            "conti's", "dq blizzard", "dunkin' donuts", "eggzellent", "ferrero", 
            "good taste restaurant", "grilled balut", "kwek-kwek", "liam's lomi house", 
            "magnum", "maki", "mccafe", "mcdo", "mojito (alak)", "mr. kimbob", 
            "mylk tea", "mylk tea_1", "omakase maki", "one takoyaki", "pizza volante", 
            "s&r", "sandwich ni tita trish", "slurpee", "snack time", "starbucks", 
            "starbucks sandwich", "starbucks_1", "starbucks_2", 
            "strawberry taho from baguio", "tea box", "terrasse", "tokyo tokyo", 
            "wendy's", "wendy's_1", "wendy's_2", "zagu", "zagu_1", "zark's"
        ]
    },
    "commute": {
        "prefixes": ["commute", "byahe ", "daan papuntang", "nlex to", "concepcion to"],
        "exact": [
            "alternate route papuntang school", "angelicum to sm north", 
            "bus papuntang sto. domingo", "byahe ng malabon gamit si ertiga", 
            "byahe papuntang fairview kasama sila daddy, ako, mommy, at ethan", 
            "byahe pauwi", "commonwealth liko sa kaliwa doon sa may pataas", 
            "commuting to sm north", "concepcion to sagana", "daan papuntang tarlac", 
            "e-jeep", "fairview teracces to sacred heart commute", "jeep monumento", 
            "lrt kasama sila daddy papuntang star city", "malabon to qc", 
            "nlex to concepcion, tarlac", "paglabas sa culiat, may labasan sa central bago yung iglesia ni cristo", 
            "things i learned from commuting"
        ]
    },
    "acads": {
        "prefixes": ["how to review", "school to do", "precal"],
        "exact": [
            "205 total school days", "back to school after acad break", 
            "college entrance exam reviewer", "examination week", "finals exam", 
            "grade 12 might be my time to show the real me", "math-sci-ya webinar", 
            "moving up ceremony notes", "oral comms and kompan vlog )", 
            "precal", "precal quiz average time", "preparation for finals exam", 
            "preparation for moving up", "review for midterm exam", "school done list", 
            "school to do list", "school to do list_1", "teachers of ust angelicum college", 
            "thursday class", "to do for school", "upcat preparation"
        ]
    },
    "fitness_health": {
        "prefixes": ["workout"],
        "exact": [
            "bike stats", "fitness army", "how to monkey bar", "how to workout", 
            "incline machine press 55 lbs each", "naubos na yung cherifer ko", 
            "pediasure plus stats", "stretching stats", "toothbrush routine", 
            "workout", "workout stats", "workout tips"
        ]
    },
    "media_entertainment": {
        "prefixes": ["song ", "dragon ball", "ben 10", "bleach", "anime "],
        "exact": [
            "3lixir", "anime figures", "anime figures_1", "anime figures_2", 
            "anime, manga, manhwa, series", "aot", "ben 10 (2005)", "ben 10 alien force", 
            "bleach", "bleach_1", "ch. 1053.1", "ch. 1053.2", "code geass", "dragon ball gt", 
            "dragon ball super", "dragon ball z", "dragonball", "fairy tail", 
            "froakie shiny hunt", "games i played pc edition", "goh", "k-drama", 
            "laro ng sekiro sa tv", "manhwa list", "mga nalarong games kasama si tito eldon", 
            "minecraft smp build ideas", "minecraft smp projects", "mining ancient debris", 
            "naruto", "naruto shippuden ultimate ninja storm 3", "omen big brain plays 😈", 
            "one piece", "one piece messenger names", "playstation store", "pokemon series", 
            "skidrow reloaded", "steam sale computations", "taptap valo", "top 10 anime list", 
            "twitch choogsh", "watch true detective - king in yellow"
        ]
    },
    "important_accounts": {
        "prefixes": ["09502823012"],
        "exact": [
            "072531", "09502823012 - kuya janjan", "contact no.", "postal code", 
            "valorant accounts", "website yung portal"
        ]
    },
    "finance_shopping": {
        "prefixes": ["how to pair realme", "keyboard "],
        "exact": [
            "256gb sd card", "5th charger", "cable", "circle c controllers", 
            "circle c finds", "coolectzone", "datablitz", "earphones", "earphones_1", 
            "gamextreme", "gastos", "gulikit kingkong 2 pro", "ipon galing baon", 
            "japanese keycaps", "jbl", "keyboard frame", "keyboard keychain", 
            "keyboard modding", "keyboard 🔥", "kupal gastusin", "laptop stand", 
            "micro valley", "powerbank hunting", "road to one million 😎💸", 
            "summer sale!!", "wallet", "watch"
        ]
    },
    "stubs_trash": {
        "exact": [
            "(. _. )", "13", "14x10", "29", "358", "di pa tapos", "try if magsave sa cloud", 
            "wala magawa", "wala magawa_1", "you don't"
        ]
    }
}

def auto_sort_xiaomi():
    base_dir = Path(__file__).parent
    uncat_dir = base_dir / "uncategorized"
    
    if not uncat_dir.exists():
        print(f"Error: Directory not found: {uncat_dir}")
        return

    files = list(uncat_dir.glob("*.md"))
    moved_summary = {cat: 0 for cat in CATEGORIES}

    for file_path in files:
        stem_lower = file_path.stem.lower().strip()
        matched_cat = None

        for cat, rules in CATEGORIES.items():
            # Check exact match
            if stem_lower in [e.lower() for e in rules.get("exact", [])]:
                matched_cat = cat
                break
            
            # Check prefix match
            prefixes = [p.lower() for p in rules.get("prefixes", [])]
            if any(stem_lower.startswith(p) for p in prefixes):
                matched_cat = cat
                break

        if matched_cat:
            target_folder = base_dir / matched_cat
            target_folder.mkdir(parents=True, exist_ok=True)
            
            target_path = target_folder / file_path.name
            counter = 1
            while target_path.exists():
                target_path = target_folder / f"{file_path.stem}_{counter}.md"
                counter += 1
            
            shutil.move(str(file_path), str(target_path))
            moved_summary[matched_cat] += 1

    print("=" * 60)
    print(" AUTO-CATEGORIZATION SUMMARY")
    print("=" * 60)
    total_moved = sum(moved_summary.values())
    for cat, count in moved_summary.items():
        print(f"  {cat:<25}: {count} files")
    print("-" * 60)
    print(f"  Total files categorized  : {total_moved}")
    print(f"  Remaining in uncategorized: {len(list(uncat_dir.glob('*.md')))}")
    print("=" * 60)

if __name__ == "__main__":
    auto_sort_xiaomi()