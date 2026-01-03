from __future__ import annotations
import re
from pathlib import Path

ROOT = Path("docs")

YOUTUBE_RE = re.compile(r'(<iframe\b[^>]*\bsrc="[^"]*youtube\.com/embed[^"]*"[^>]*)(>)', re.IGNORECASE)
SPOTIFY_RE = re.compile(r'(<iframe\b[^>]*\bsrc="[^"]*open\.spotify\.com/embed[^"]*"[^>]*)(>)', re.IGNORECASE)

STYLE_RE = re.compile(r'\sstyle="[^"]*"', re.IGNORECASE)
WIDTH_RE = re.compile(r'\swidth="[^"]*"', re.IGNORECASE)
HEIGHT_RE = re.compile(r'\sheight="[^"]*"', re.IGNORECASE)

CLASS_RE = re.compile(r'\sclass="([^"]*)"', re.IGNORECASE)
LOADING_RE = re.compile(r'\sloading="[^"]*"', re.IGNORECASE)

def ensure_class(tag_start: str, class_to_add: str) -> str:
    m = CLASS_RE.search(tag_start)
    if m:
        classes = m.group(1).split()
        if class_to_add not in classes:
            classes.append(class_to_add)
        new_class = ' class="' + " ".join(classes) + '"'
        return CLASS_RE.sub(new_class, tag_start, count=1)
    else:
        return tag_start + f' class="{class_to_add}"'

def ensure_loading_lazy(tag_start: str) -> str:
    if LOADING_RE.search(tag_start):
        return tag_start
    return tag_start + ' loading="lazy"'

def clean_iframe(tag_start: str) -> str:
    # removemos inline style y width/height inline
    tag_start = STYLE_RE.sub("", tag_start)
    tag_start = WIDTH_RE.sub("", tag_start)
    tag_start = HEIGHT_RE.sub("", tag_start)
    return tag_start

def transform(text: str) -> tuple[str, int]:
    changes = 0

    def repl(match: re.Match) -> str:
        nonlocal changes
        tag_start, end = match.group(1), match.group(2)
        original = tag_start

        tag_start = clean_iframe(tag_start)
        tag_start = ensure_class(tag_start, "anison-embed")
        tag_start = ensure_loading_lazy(tag_start)

        if tag_start != original:
            changes += 1
        return tag_start + end

    text2 = YOUTUBE_RE.sub(repl, text)
    text3 = SPOTIFY_RE.sub(repl, text2)
    return text3, changes

def main() -> None:
    total_files = 0
    total_changes = 0

    for p in ROOT.rglob("*.md"):
        old = p.read_text(encoding="utf-8")
        new, n = transform(old)
        if n:
            p.write_text(new, encoding="utf-8", newline="\n")
            total_files += 1
            total_changes += n

    print(f"✅ Archivos modificados: {total_files}")
    print(f"✅ iframes normalizados: {total_changes}")

if __name__ == "__main__":
    main()
