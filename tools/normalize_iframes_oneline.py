from __future__ import annotations
import re
from pathlib import Path

ROOT = Path("docs")

# Bloque iframe completo (incluye cualquier salto de línea interno)
IFRAME_BLOCK = re.compile(
    r'(^[ \t]*)<iframe\b[\s\S]*?</iframe>',
    re.IGNORECASE | re.MULTILINE
)

# Extrae el tag de apertura <iframe ...>
OPEN_TAG = re.compile(r'<iframe\b[\s\S]*?>', re.IGNORECASE)

def collapse_open_tag(tag: str) -> str:
    # Colapsa espacios/nuevas líneas dentro del tag a un solo espacio
    tag = re.sub(r'\s+', ' ', tag).strip()
    # Quita espacio antes de ">"
    tag = tag.replace(' >', '>')
    return tag

def repl(match: re.Match) -> str:
    indent = match.group(1)
    block = match.group(0)

    m = OPEN_TAG.search(block)
    if not m:
        return block  # no debería pasar

    open_tag = collapse_open_tag(m.group(0))

    # Reemplazamos TODO el bloque por una sola línea
    return f"{indent}{open_tag}</iframe>"

def main() -> None:
    changed_files = 0
    changed_blocks = 0

    for p in ROOT.rglob("*.md"):
        old = p.read_text(encoding="utf-8")
        new, n = IFRAME_BLOCK.subn(repl, old)
        if n and new != old:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed_files += 1
            changed_blocks += n

    print(f"✅ Archivos modificados: {changed_files}")
    print(f"✅ Iframes normalizados: {changed_blocks}")

if __name__ == "__main__":
    main()
