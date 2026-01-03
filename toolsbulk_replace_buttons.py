from __future__ import annotations
from pathlib import Path

ROOT = Path("docs")  # aquí están tus .md

REPLACES = [
    # Home (y cualquier otra página)
    ("Ver playlist completa en youtube", "Abrir playlist en YouTube"),
    ("Ver playlist completa en Youtube", "Abrir playlist en YouTube"),
    ("Ver playlist completa en YouTube", "Abrir playlist en YouTube"),

    # Páginas de series
    ("Ver playlist en youtube", "Abrir en YouTube"),
    ("Ver playlist en Youtube", "Abrir en YouTube"),
    ("Ver playlist en YouTube", "Abrir en YouTube"),
]

def apply_replaces(text: str) -> tuple[str, int]:
    count = 0
    for a, b in REPLACES:
        if a in text:
            n = text.count(a)
            text = text.replace(a, b)
            count += n
    return text, count

def main() -> None:
    changed_files = []
    total_repl = 0

    for p in ROOT.rglob("*.md"):
        old = p.read_text(encoding="utf-8")
        new, n = apply_replaces(old)
        if n > 0 and new != old:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed_files.append((p.as_posix(), n))
            total_repl += n

    print(f"\n✅ Reemplazos totales: {total_repl}")
    if changed_files:
        print("📝 Archivos cambiados:")
        for f, n in changed_files:
            print(f"  - {f}  ({n})")
    else:
        print("ℹ️ No encontré ocurrencias en docs/**/*.md")

if __name__ == "__main__":
    main()

