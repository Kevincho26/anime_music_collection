#!/usr/bin/env python3
"""
Build grid catalog pages (A, B, C...) for MkDocs Material using thumbnail images.

Usage (run from repo root, where mkdocs.yml is):
  py build_grid_catalog.py --csv playlists_index.csv --thumbs thumbs_report.csv

Assumptions:
- Your docs live in ./docs
- Your letter folders are ./docs/series/A, ./docs/series/B, ... and 0-9
- It will overwrite ./docs/series/<SECTION>/index.md for sections listed in docs/series/.pages nav.
- It does NOT rename or move your existing playlist pages; it links to whatever it finds under each section folder.

What it does:
- Scans markdown files under docs/series/<SECTION>/ (excluding index.md and .pages) and reads first H1 as title.
- Joins with CSV (spotify_url) and thumbs_report (thumb_file).
- Writes a Material "cards grid" with thumbnail + title + buttons.

Requires: Python 3.10+, no extra packages.
"""
from __future__ import annotations
import argparse, csv, re, urllib.parse
from pathlib import Path

def read_first_h1(md_path: Path) -> str | None:
    try:
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        return None
    return None

def urlenc_path(p: str) -> str:
    # Encode spaces and special chars but keep slashes
    return urllib.parse.quote(p, safe="/-_.~")

def load_csv_map(path: Path, key: str) -> dict[str, dict]:
    out = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out[row[key]] = row
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs", help="Docs directory (default: docs)")
    ap.add_argument("--series-dir", default="docs/series", help="Series directory (default: docs/series)")
    ap.add_argument("--csv", required=True, help="playlists_index.csv (titulo, spotify_url)")
    ap.add_argument("--thumbs", required=True, help="thumbs_report.csv (titulo, thumb_file)")
    ap.add_argument("--thumbs-web-path", default="../../assets/thumbs", help="Path used in markdown image links from section index.md")
    args = ap.parse_args()

    docs_dir = Path(args.docs)
    series_dir = Path(args.series_dir)

    if not series_dir.exists():
        raise SystemExit(f"Series dir not found: {series_dir}")

    playlist_map = load_csv_map(Path(args.csv), "titulo")
    thumbs_map = load_csv_map(Path(args.thumbs), "titulo")

    # Determine sections: based on existing folders in docs/series that look like A-Z or 0-9
    sections = [p.name for p in series_dir.iterdir() if p.is_dir() and (re.fullmatch(r"[A-Z]", p.name) or p.name == "0-9")]
    sections = sorted(sections, key=lambda s: (s != "0-9", s))

    for sec in sections:
        sec_dir = series_dir / sec
        # Find pages inside this section
        pages = []
        for md in sec_dir.rglob("*.md"):
            if md.name.lower() == "index.md":
                continue
            if md.name == ".pages":
                continue
            title = read_first_h1(md)
            if not title:
                continue
            # Link from sec index to this file (prefer folder link if it's .../X/index.md but we skipped index)
            rel = md.relative_to(sec_dir).as_posix()
            pages.append((title, rel))

        # Sort by title
        pages.sort(key=lambda x: x[0].lower())

        # Build grid
        lines = []
        lines.append(f"# {sec}")
        lines.append("")
        lines.append('<div class="grid cards" markdown>')
        lines.append("")

        for title, rel in pages:
            spotify_url = playlist_map.get(title, {}).get("spotify_url", "")
            thumb_file = thumbs_map.get(title, {}).get("thumb_file", "")
            thumb_src = f"{args.thumbs_web_path}/{thumb_file}" if thumb_file else ""

            rel_link = urlenc_path(rel)
            thumb_link = urlenc_path(thumb_src) if thumb_src else ""

            lines.append(f"-   [![{title}]({thumb_link}){{ width=200 }}]({rel_link})" if thumb_link else "-   **(no cover)**")
            lines.append("")
            lines.append(f"    **[{title}]({rel_link})**")
            lines.append("")
            
        lines.append("</div>")
        lines.append("")
        out_path = sec_dir / "index.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {out_path} ({len(pages)} items)")

if __name__ == "__main__":
    main()
