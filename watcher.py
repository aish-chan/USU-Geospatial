"""
watcher.py  –  Watches posts/ for new/modified/deleted .txt files
               and rebuilds the site automatically.

Usage:
    python watcher.py
    python watcher.py --title "My Blog" --tagline "Stories & Ideas"
"""

import sys
import time
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generator import build_site, POSTS_DIR

class PostHandler(FileSystemEventHandler):
    def __init__(self, title, tagline):
        self.title   = title
        self.tagline = tagline

    def _relevant(self, path: str) -> bool:
        return Path(path).suffix.lower() == ".txt"

    def on_created(self, event):
        if not event.is_directory and self._relevant(event.src_path):
            print(f"[watcher] New file detected: {event.src_path}")
            build_site(self.title, self.tagline)

    def on_modified(self, event):
        if not event.is_directory and self._relevant(event.src_path):
            print(f"[watcher] File modified: {event.src_path}")
            build_site(self.title, self.tagline)

    def on_deleted(self, event):
        if not event.is_directory and self._relevant(event.src_path):
            print(f"[watcher] File removed: {event.src_path}")
            build_site(self.title, self.tagline)

    def on_moved(self, event):
        if self._relevant(event.dest_path) or self._relevant(event.src_path):
            print(f"[watcher] File moved/renamed: {event.src_path} → {event.dest_path}")
            build_site(self.title, self.tagline)


def main():
    parser = argparse.ArgumentParser(description="Auto-rebuilding blog watcher")
    parser.add_argument("--title",   default="Utah Geospatial Opportunities",        help="Site title")
    parser.add_argument("--tagline", default="GIS, Remote Sensing and GeoAI", help="Site tagline")
    args = parser.parse_args()

    POSTS_DIR.mkdir(exist_ok=True)

    # Initial build
    build_site(args.title, args.tagline)

    observer = Observer()
    handler  = PostHandler(args.title, args.tagline)
    observer.schedule(handler, str(POSTS_DIR), recursive=False)
    observer.start()

    print(f"\n[watcher] Watching '{POSTS_DIR}/' for .txt changes  (Ctrl+C to stop)\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watcher] Stopped.")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
