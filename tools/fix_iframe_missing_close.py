from __future__ import annotations
from pathlib import Path

ROOT = Path("docs")

def fix_text(text: str) -> tuple[str, int]:
    """
    Recorre el Markdown y, por cada <iframe ...>, verifica si existe un </iframe>
    antes del siguiente <iframe. Si NO existe, inserta </iframe> justo después del '>'.
    """
    changes = 0
    i = 0
    out = []

    while True:
        s = text.find("<iframe", i)
        if s == -1:
            out.append(text[i:])
            break

        # copia lo anterior
        out.append(text[i:s])

        # encuentra el fin del tag de apertura (>)
        e = text.find(">", s)
        if e == -1:
            # tag roto, salimos sin tocar
            out.append(text[s:])
            break

        open_tag = text[s:e+1]
        out.append(open_tag)
        i = e + 1

        # si ya está cerrado inmediatamente, seguimos
        j = i
        while j < len(text) and text[j].isspace():
            j += 1
        if text.startswith("</iframe>", j):
            continue

        # busca el próximo cierre y el próximo iframe
        close_pos = text.find("</iframe>", i)
        next_iframe = text.find("<iframe", i)

        # Si no hay cierre, o el próximo iframe viene antes del cierre → falta cierre
        if close_pos == -1 or (next_iframe != -1 and next_iframe < close_pos):
            out.append("</iframe>")
            changes += 1

    return "".join(out), changes


def main() -> None:
    files_changed = 0
    total_changes = 0

    for p in ROOT.rglob("*.md"):
        old = p.read_text(encoding="utf-8")
        new, n = fix_text(old)
        if n:
            p.write_text(new, encoding="utf-8", newline="\n")
            files_changed += 1
            total_changes += n

    print(f"✅ Archivos modificados: {files_changed}")
    print(f"✅ </iframe> añadidos: {total_changes}")

if __name__ == "__main__":
    main()
