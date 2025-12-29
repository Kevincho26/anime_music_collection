"""
Apply cover images to MkDocs markdown pages.

- Expects:
  - docs/ directory (MkDocs default)
  - covers_report.csv produced by my processor (contains titulo + cover_file)
  - cover images located at: docs/assets/covers/<cover_file>

It will:
  - scan all *.md under docs/
  - if the first H1 heading (# Title) matches a playlist title in covers_report.csv,
    it inserts a cover image line right after the H1 (if not already present).

Run from repo root:
  py apply_covers_to_mkdocs.py covers_report.csv
"""
from __future__ import annotations
import csv
import os
import sys
from pathlib import Path

def read_report(report_csv: Path) -> dict[str, str]:
    m: dict[str, str] = {}
    with report_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("titulo") or "").strip()
            cover_file = (row.get("cover_file") or "").strip()
            if title and cover_file:
                m[title] = cover_file
    return m

def main():
    if len(sys.argv) < 2:
        print("Usage: py apply_covers_to_mkdocs.py covers_report.csv")
        sys.exit(1)

    report_csv = Path(sys.argv[1]).resolve()
    repo_root = Path.cwd()
    docs_dir = repo_root / "docs"
    covers_dir = docs_dir / "assets" / "covers"

    if not docs_dir.exists():
        print("ERROR: docs/ not found. Run this from your MkDocs repo root.")
        sys.exit(2)
    if not covers_dir.exists():
        print(f"ERROR: covers dir not found: {covers_dir}")
        sys.exit(3)

    title_to_cover = read_report(report_csv)
    if not title_to_cover:
        print("ERROR: no titles found in report CSV.")
        sys.exit(4)

    changed = 0
    scanned = 0

    for md in docs_dir.rglob("*.md"):
        scanned += 1
        text = md.read_text(encoding="utf-8")

        lines = text.splitlines()
        if not lines:
            continue

        # find first H1
        h1_idx = None
        h1_title = None
        for i, line in enumerate(lines[:30]):  # only look near top
            if line.startswith("# "):
                h1_idx = i
                h1_title = line[2:].strip()
                break

        if not h1_title or h1_title not in title_to_cover:
            continue

        cover_file = title_to_cover[h1_title]
        cover_abs = covers_dir / cover_file
        if not cover_abs.exists():
            continue

        # compute relative path from md file to cover
        rel = os.path.relpath(cover_abs, md.parent).replace("\\", "/")

        cover_line = f'![Cover]({rel}){{ width=320 }}'

        # already present?
        if any("assets/covers/" in ln and cover_file in ln for ln in lines[:40]):
            continue
        if any(cover_line in ln for ln in lines[:40]):
            continue

        insert_at = h1_idx + 1
        # ensure a blank line after insertion
        new_lines = lines[:insert_at] + ["", cover_line, ""] + lines[insert_at:]
        md.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        changed += 1

    print(f"Scanned: {scanned} markdown files")
    print(f"Updated: {changed} files (cover inserted)")

if __name__ == "__main__":
    main()
