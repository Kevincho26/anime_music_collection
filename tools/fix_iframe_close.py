from __future__ import annotations
import re
from pathlib import Path

ROOT = Path("docs")

# Detecta apertura de iframe (hasta el >)
OPEN_IFRAME = re.compile(r'(<iframe\b[^>]*\bclass="[^"]*\banison-embed\b[^"]*"[^>]*>)', re.IGNORECASE)

def fix_file(text: str) -> tuple[str, int]:
    """
    Si hay <iframe ...> sin </iframe> cercano, lo cierra.
    """
    changes = 0
    out = []
    i = 0

    while True:
        m = OPEN_IFRAME.search(text, i)
        if not m:
            out.append(text[i:])
            break

        start, end = m.span(1)
        out.append(text[i:start])
        open_tag = m.group(1)
        out.append(open_tag)
        i = end

        # Mira lo que sigue inmediatamente después del iframe abierto
        # Si ya hay un cierre cercano, no hace nada.
        tail = text[i:i+500]
        if "</iframe>" not in tail:
            out.append("</iframe>")
            changes += 1

    return "".join(out), changes

def main() -> None:
    changed_files = 0
    total = 0

    for p in ROOT.rglob("*.md"):
        old = p.read_text(encoding="utf-8")
        new, n = fix_file(old)
        if n:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed_files += 1
            total += n

    print(f"✅ Archivos modificados: {changed_files}")
    print(f"✅ </iframe> añadidos: {total}")

if __name__ == "__main__":
    main()
