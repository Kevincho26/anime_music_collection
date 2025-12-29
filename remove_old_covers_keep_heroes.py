#!/usr/bin/env python3
"""
Remove previous cover images from playlist pages, keeping only HERO blocks.

What it removes (from docs/series/** excluding index.md/.pages):
- Any Markdown image lines that reference assets/covers/ or assets/thumbs/
  (these were previously used as "portadas" / thumbnails on pages).
- It DOES NOT touch section index grids (docs/series/<LETTER>/index.md),
  because those are index.md files and are skipped.
- It DOES NOT touch HERO blocks (between <!-- HERO:START --> and <!-- HERO:END -->).

Usage (run from repo root):
  py remove_old_covers_keep_heroes.py

Optional:
  py remove_old_covers_keep_heroes.py --docs docs --series docs/series
"""
from __future__ import annotations
import argparse, re
from pathlib import Path

HERO_START = "<!-- HERO:START -->"
HERO_END = "<!-- HERO:END -->"

IMG_RE = re.compile(r"!\[.*?\]\((.*?)\)")  # markdown image

def is_portada_image_line(line: str) -> bool:
    m = IMG_RE.search(line)
    if not m:
        return False
    url = m.group(1)
    return ("assets/covers/" in url) or ("assets/thumbs/" in url)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--series", default="docs/series")
    args = ap.parse_args()

    series_dir = Path(args.series)
    if not series_dir.exists():
        raise SystemExit(f"Series dir not found: {series_dir}")

    updated = 0
    scanned = 0
    removed_lines_total = 0

    for md in series_dir.rglob("*.md"):
        if md.name.lower() == "index.md" or md.name == ".pages":
            continue

        scanned += 1
        text = md.read_text(encoding="utf-8")
        lines = text.splitlines()

        out = []
        in_hero = False
        removed_here = 0

        for line in lines:
            if HERO_START in line:
                in_hero = True
                out.append(line)
                continue
            if HERO_END in line:
                in_hero = False
                out.append(line)
                continue

            if (not in_hero) and is_portada_image_line(line):
                removed_here += 1
                continue

            out.append(line)

        # cleanup: collapse 3+ blank lines to max 2
        cleaned = "\n".join(out)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip() + "\n"

        if cleaned != text:
            md.write_text(cleaned, encoding="utf-8")
            updated += 1
            removed_lines_total += removed_here

    print(f"Scanned: {scanned}")
    print(f"Updated files: {updated}")
    print(f"Removed portada image lines: {removed_lines_total}")

if __name__ == "__main__":
    main()
