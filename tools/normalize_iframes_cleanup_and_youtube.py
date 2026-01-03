from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

IFRAME_OPEN_RE = re.compile(r"<iframe\b.*?>", re.IGNORECASE | re.DOTALL)

# src="..." o src='...'
SRC_RE = re.compile(r'\bsrc\s*=\s*(["\'])(.*?)\1', re.IGNORECASE | re.DOTALL)

# Atributos a eliminar del tag de apertura
STYLE_RE = re.compile(r"\sstyle\s*=\s*(\"[^\"]*\"|'[^']*')", re.IGNORECASE | re.DOTALL)
WIDTH_RE = re.compile(r"\swidth\s*=\s*(\"[^\"]*\"|'[^']*')", re.IGNORECASE | re.DOTALL)
HEIGHT_RE = re.compile(r"\sheight\s*=\s*(\"[^\"]*\"|'[^']*')", re.IGNORECASE | re.DOTALL)

def collapse_ws_outside_quotes(s: str) -> str:
    """Colapsa whitespace fuera de comillas para dejar el <iframe ...> en una sola línea."""
    out = []
    in_quote = None
    prev_space = False

    for ch in s:
        if in_quote:
            out.append(ch)
            if ch == in_quote:
                in_quote = None
            continue

        if ch in ('"', "'"):
            out.append(ch)
            in_quote = ch
            prev_space = False
            continue

        if ch.isspace():
            if not prev_space:
                out.append(" ")
                prev_space = True
            continue

        out.append(ch)
        prev_space = False

    return "".join(out).strip()

def normalize_youtube_playlist_src(src: str) -> str:
    """
    Normaliza playlists de YouTube a:
    https://www.youtube.com/embed/videoseries?list=PLAYLIST_ID&rel=0

    Solo toca casos de playlist:
    - /embed?listType=playlist&list=...
    - /embed/videoseries?list=...
    """
    try:
        u = urlparse(src)
    except Exception:
        return src

    host = (u.netloc or "").lower()
    path = u.path or ""

    if "youtube.com" not in host:
        return src

    qs = parse_qs(u.query, keep_blank_values=True)

    # Caso Home típico: /embed?listType=playlist&list=...
    is_embed_root = path.rstrip("/") == "/embed"
    is_videoseries = path.rstrip("/") == "/embed/videoseries"

    if is_embed_root and qs.get("listType", [""])[0].lower() == "playlist" and "list" in qs:
        playlist_id = qs["list"][0]
        new_qs = {"list": playlist_id, "rel": "0"}
        return urlunparse(("https", "www.youtube.com", "/embed/videoseries", "", urlencode(new_qs), ""))

    # Caso ya videoseries: asegurar rel=0
    if is_videoseries and "list" in qs:
        playlist_id = qs["list"][0]
        new_qs = {"list": playlist_id, "rel": "0"}
        return urlunparse(("https", "www.youtube.com", "/embed/videoseries", "", urlencode(new_qs), ""))

    return src

def process_iframe_open_tag(tag: str) -> str:
    original = tag

    # 1) quitar style/width/height (para que mande CSS)
    tag = STYLE_RE.sub("", tag)
    tag = WIDTH_RE.sub("", tag)
    tag = HEIGHT_RE.sub("", tag)

    # 2) normalizar src si es playlist de YouTube
    m = SRC_RE.search(tag)
    if m:
        quote = m.group(1)
        src = m.group(2).strip()
        new_src = normalize_youtube_playlist_src(src)
        if new_src != src:
            # reemplaza solo el valor del src
            start, end = m.span(2)
            tag = tag[:start] + new_src + tag[end:]

    # 3) colapsar whitespace para que el tag quede en 1 sola línea
    tag = collapse_ws_outside_quotes(tag)

    # 4) asegura que cierre con ">"
    if not tag.endswith(">"):
        tag = tag + ">"

    return tag if tag != original else original

def process_file(path: Path) -> tuple[bool, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    changed = False
    processed = 0

    def repl(m: re.Match) -> str:
        nonlocal changed, processed
        processed += 1
        old = m.group(0)
        new = process_iframe_open_tag(old)
        if new != old:
            changed = True
        return new

    new_text = IFRAME_OPEN_RE.sub(repl, text)
    if changed:
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return changed, processed

def main() -> None:
    if not DOCS_DIR.exists():
        print(f"❌ No existe carpeta docs: {DOCS_DIR}")
        return

    md_files = sorted(DOCS_DIR.rglob("*.md"))
    files_changed = 0
    iframes_seen = 0

    for f in md_files:
        changed, processed = process_file(f)
        iframes_seen += processed
        if changed:
            files_changed += 1

    print(f"✅ Iframes procesados: {iframes_seen}")
    print(f"✅ Archivos modificados: {files_changed}")

if __name__ == "__main__":
    main()
