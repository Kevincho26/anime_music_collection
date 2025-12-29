#!/usr/bin/env python3
"""
Apply hero banner images to MkDocs pages (playlist pages), centered title + banner.

- Reads heroes_report.csv: columns (titulo, hero_file)
- Scans docs/series/** for markdown files (excluding index.md and .pages)
- Matches page by first H1 (# Title) to 'titulo'
- Inserts a hero block right after the H1 (or replaces existing hero block if present)

Hero block inserted:
<!-- HERO:START -->
<div class="hero" markdown>
![Title](REL_PATH_TO_HERO){ .hero-img }
</div>
<!-- HERO:END -->

Requires mkdocs.yml:
markdown_extensions:
  - md_in_html
  - attr_list
extra_css with styles for .hero + centered h1.

Usage (run from repo root):
  py apply_heroes_to_mkdocs_v2.py heroes_report.csv
"""
from __future__ import annotations
import csv, re, argparse, os
from pathlib import Path

HERO_START = "<!-- HERO:START -->"
HERO_END = "<!-- HERO:END -->"

def read_first_h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def make_hero_block(title: str, rel_img: str) -> str:
    return "\n".join([
        HERO_START,
        '<div class="hero" markdown>',
        f'![{title}]({rel_img}){{ .hero-img }}',
        "</div>",
        HERO_END,
        ""
    ])

def remove_existing_hero(text: str) -> str:
    if HERO_START in text and HERO_END in text:
        pattern = re.compile(re.escape(HERO_START) + r".*?" + re.escape(HERO_END) + r"\n?", re.S)
        return pattern.sub("", text)
    return text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report", help="heroes_report.csv (titulo, hero_file)")
    ap.add_argument("--docs", default="docs", help="docs dir (default: docs)")
    ap.add_argument("--series", default="docs/series", help="series dir (default: docs/series)")
    ap.add_argument("--assets", default="docs/assets/heroes", help="heroes assets dir (default: docs/assets/heroes)")
    args = ap.parse_args()

    report_path = Path(args.report)
    series_dir = Path(args.series)
    assets_dir = Path(args.assets)

    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")
    if not series_dir.exists():
        raise SystemExit(f"Series dir not found: {series_dir}")
    if not assets_dir.exists():
        raise SystemExit(f"Assets dir not found: {assets_dir}")

    hero_map = {}
    with report_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hero_map[row["titulo"]] = row["hero_file"]

    updated = 0
    skipped = 0
    missing = 0

    for md in series_dir.rglob("*.md"):
        if md.name.lower() == "index.md" or md.name == ".pages":
            continue
        text = md.read_text(encoding="utf-8")
        title = read_first_h1(text)
        if not title:
            skipped += 1
            continue

        hero_file = hero_map.get(title)
        if not hero_file:
            missing += 1
            continue

        rel = Path(os.path.relpath(assets_dir / hero_file, md.parent)).as_posix()

        text2 = remove_existing_hero(text)
        lines = text2.splitlines()
        out_lines = []
        inserted = False
        for line in lines:
            out_lines.append(line)
            if not inserted and line.startswith("# "):
                out_lines.append("")
                out_lines.append(make_hero_block(title, rel).rstrip("\n"))
                inserted = True

        if not inserted:
            skipped += 1
            continue

        md.write_text("\n".join(out_lines).replace("\n\n\n", "\n\n") + "\n", encoding="utf-8")
        updated += 1

    print(f"Updated: {updated}")
    print(f"Skipped(no H1): {skipped}")
    print(f"Missing hero: {missing}")

if __name__ == "__main__":
    main()
