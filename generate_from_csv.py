"""
Generate MkDocs docs/ structure for the anime playlist catalogue.

Usage (from your MkDocs repo root):
    py generate_from_csv.py playlists_index.csv

It will (re)create ./docs/series/* and update ./docs/index.md.
"""

import csv
import os
import re
import shutil
import string
import unicodedata
from pathlib import Path

def slugify_filename(s: str) -> str:
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if not s:
        s = "playlist"
    reserved = {"con","prn","aux","nul","com1","com2","com3","com4","com5","com6","com7","com8","com9",
                "lpt1","lpt2","lpt3","lpt4","lpt5","lpt6","lpt7","lpt8","lpt9"}
    if s in reserved:
        s += "-1"
    return s[:80]

def spotify_id(url: str) -> str:
    m = re.search(r"open\.spotify\.com/playlist/([A-Za-z0-9]+)", url or "")
    return m.group(1) if m else ""

def group_key(title: str) -> str:
    t = (title or "").strip()
    if not t:
        return "#"
    ch = t[0].upper()
    if ch.isdigit():
        return "0-9"
    if ch in string.ascii_uppercase:
        return ch
    return "#"

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_text(p: Path, text: str):
    p.write_text(text, encoding="utf-8")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: py generate_from_csv.py playlists_index.csv")
        raise SystemExit(2)

    csv_path = Path(sys.argv[1]).resolve()
    repo_root = Path.cwd()
    docs = repo_root / "docs"
    series_dir = docs / "series"

    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    rows = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "titulo": (r.get("titulo") or "").strip(),
                "spotify_url": (r.get("spotify_url") or "").strip(),
                "youtube_url": (r.get("youtube_url") or "").strip(),
            })

    rows = [r for r in rows if r["titulo"] and r["spotify_url"]]

    # Recreate series folder
    ensure_dir(docs)
    if series_dir.exists():
        shutil.rmtree(series_dir)
    ensure_dir(series_dir)

    # Determine letters present
    present = {group_key(r["titulo"]) for r in rows}
    order = (["0-9"] if "0-9" in present else []) + sorted([c for c in present if c not in ["0-9","#"]]) + (["#"] if "#" in present else [])

    # Series root pages
    write_text(series_dir / "index.md", "# Series\n\nSelecciona una letra en el menú.\n")
    pages = "title: Series\nnav:\n  - index.md\n" + "".join([f"  - {l}/\n" for l in order])
    write_text(series_dir / ".pages", pages)

    # Central playlist
    central = next((r for r in rows if r["titulo"].lower() == "anime gems"), rows[0])
    central_id = spotify_id(central["spotify_url"])

    # Site index
    index_md = f"""# Anime Music Collection

Esta es una colección de playlists (una por serie).  
Usa el buscador (lupa) para encontrar rápido una serie.

## Empezar aquí: {central["titulo"]}

=== "Spotify"
    <iframe style="border-radius:12px"
      src="https://open.spotify.com/embed/playlist/{central_id}"
      width="100%" height="352" frameborder="0"
      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
      loading="lazy"></iframe>

    [▶ Abrir en Spotify]({central["spotify_url"]})

=== "YouTube"
    *(pendiente: añade el link de YouTube a esta playlist)*

## Series (A–Z)

""" + "\n".join([f"- [{l}](series/{l}/)" for l in order]) + "\n"
    write_text(docs / "index.md", index_md)

    # Per-letter folders and pages
    used = set()
    for l in order:
        lp = series_dir / l
        ensure_dir(lp)
        write_text(lp / ".pages", f'title: "{l}"\nnav:\n  - index.md\nsort_type: natural\n')

    # Create playlist pages
    for r in rows:
        title = r["titulo"]
        l = group_key(title)
        sp_url = r["spotify_url"]
        spid = spotify_id(sp_url)

        fn = slugify_filename(title) + ".md"
        key = (l, fn)
        if key in used:
            base = fn[:-3]
            i = 2
            while (l, f"{base}-{i}.md") in used:
                i += 1
            fn = f"{base}-{i}.md"
            key = (l, fn)
        used.add(key)

        yt = r["youtube_url"]
        if yt:
            m = re.search(r"list=([^&]+)", yt)
            yid = m.group(1) if m else ""
            yt_section = f"""    <iframe width="100%" height="360"
      src="https://www.youtube.com/embed/videoseries?list={yid}"
      title="YouTube playlist player"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      allowfullscreen
      loading="lazy"></iframe>

    [▶ Abrir en YouTube]({yt})
"""
        else:
            yt_section = "    *(pendiente: añade el link de YouTube a esta playlist)*\n"

        content = f"""# {title}

=== "Spotify"
    <iframe style="border-radius:12px"
      src="https://open.spotify.com/embed/playlist/{spid}"
      width="100%" height="352" frameborder="0"
      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
      loading="lazy"></iframe>

    [▶ Abrir en Spotify]({sp_url})

=== "YouTube"
{yt_section}
"""
        write_text(series_dir / l / fn, content)

    # Build letter index lists
    for l in order:
        lp = series_dir / l
        md_files = [p for p in lp.glob("*.md") if p.name != "index.md"]
        entries = []
        for p in md_files:
            first = p.read_text(encoding="utf-8").splitlines()[0].strip()
            t = first.lstrip("# ").strip()
            entries.append((t, p.name))
        entries.sort(key=lambda x: x[0].lower())
        lines = "\n".join([f"- [{t}]({fn})" for t, fn in entries])
        write_text(lp / "index.md", f"# {l}\n\n{lines}\n")

    print(f"✅ Generated {len(rows)} playlist pages under: {series_dir}")

if __name__ == "__main__":
    main()
