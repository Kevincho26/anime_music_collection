# tools/fix_iframe_class_loading.py
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

IFRAME_OPEN_RE = re.compile(r"<iframe\b.*?>", re.IGNORECASE | re.DOTALL)
CLASS_RE = re.compile(r'\bclass\s*=\s*(["\'])(.*?)\1', re.IGNORECASE | re.DOTALL)
LOADING_RE = re.compile(r"\bloading\s*=", re.IGNORECASE)

TARGET_CLASS = "anison-embed"


def ensure_class(tag: str) -> str:
    m = CLASS_RE.search(tag)
    if m:
        quote = m.group(1)
        classes = m.group(2).strip()
        class_list = [c for c in re.split(r"\s+", classes) if c]

        if TARGET_CLASS not in class_list:
            class_list.append(TARGET_CLASS)

        new_val = " ".join(class_list)
        return tag[: m.start(2)] + new_val + tag[m.end(2) :]
    else:
        # Insert before closing >
        return tag[:-1] + f' class="{TARGET_CLASS}">'


def ensure_loading(tag: str) -> str:
    if LOADING_RE.search(tag):
        return tag
    return tag[:-1] + ' loading="lazy">'


def process_file(path: Path) -> tuple[bool, int]:
    original = path.read_text(encoding="utf-8", errors="replace")
    changed = False
    processed = 0

    def repl(m: re.Match) -> str:
        nonlocal changed, processed
        tag = m.group(0)
        new_tag = tag
        new_tag = ensure_class(new_tag)
        new_tag = ensure_loading(new_tag)

        if new_tag != tag:
            changed = True
        processed += 1
        return new_tag

    new_text = IFRAME_OPEN_RE.sub(repl, original)

    if changed:
        path.write_text(new_text, encoding="utf-8")
    return changed, processed


def main() -> None:
    if not DOCS_DIR.exists():
        print(f"❌ No existe carpeta docs: {DOCS_DIR}")
        return

    md_files = sorted(DOCS_DIR.rglob("*.md"))
    total_changed = 0
    total_iframes = 0

    for f in md_files:
        changed, processed = process_file(f)
        total_iframes += processed
        if changed:
            total_changed += 1

    print(f"✅ Archivos modificados: {total_changed}")
    print(f"✅ Iframes procesados: {total_iframes}")


if __name__ == "__main__":
    main()
