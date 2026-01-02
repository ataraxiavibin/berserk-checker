# chapter-check.py
#
# easy web-scraping project for automated checking if the new Berserk chapter is out
#

import json
from typing import Optional, Dict, Any
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

URL = "https://www.gutsberserk.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
CACHE_FILE = Path("./chapter.json")


def load_cache() -> Dict[str, str]:
    if not CACHE_FILE.exists():
        return {}

    try:
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("The cache file is corrupted. Starting fresh.")
        return {}


def dump_cache(times_ran: int, last_known: str) -> None:
    data = {"times_ran": times_ran, "last_known": last_known}
    with open(CACHE_FILE, "w") as file:
        json.dump(data, file)


def fetch_latest_chapter() -> Optional[str]:
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
            response = client.get(URL)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        chapter_element = soup.select_one(".site-content .row .font50")
        if chapter_element:
            return chapter_element.get_text(strip=True)
        else:
            raise Exception("Couldn't find the chapter element on the page.")

    except httpx.RequestError as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def main():
    first_time = False

    cache = load_cache()
    times_ran = cache.get("times_ran", 0)
    last_known = cache.get("last_known", None)

    last_chapter = fetch_latest_chapter()

    if last_known is None:
        print(f"Either a first run or a cache reset. Current chapter: {last_chapter}")
        dump_cache(times_ran + 1, last_chapter)
    elif last_known != last_chapter:
        print(f"NEW CHAPTER DETECTED: {last_chapter}")
        dump_cache(times_ran + 1, last_chapter)
    else:
        print(f"No changes. Checked {times_ran} times.")
        print(f"Struggle, contend, wriggle! For that alone is the sword of one who confronts death.")
        dump_cache(times_ran + 1, last_chapter)


if __name__ == "__main__":
    main()

