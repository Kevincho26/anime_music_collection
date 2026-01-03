from pathlib import Path

ROOT = Path("docs")  # o "docs/series" si quieres limitarlo

def main():
    files_changed = []
    total = 0

    for p in ROOT.rglob("*.md"):
        text = p.read_text(encoding="utf-8")

        # Caso 1: ya existe 21/9 inline
        new = text.replace("aspect-ratio:21/9;", "aspect-ratio:16/9;")

        # Caso 2 (opcional): si alguien puso 21 / 9 con espacios
        new = new.replace("aspect-ratio: 21/9;", "aspect-ratio:16/9;")
        new = new.replace("aspect-ratio: 21 / 9;", "aspect-ratio:16/9;")

        if new != text:
            p.write_text(new, encoding="utf-8", newline="\n")
            c = text.count("aspect-ratio:21/9;") + text.count("aspect-ratio: 21/9;") + text.count("aspect-ratio: 21 / 9;")
            total += max(c, 1)
            files_changed.append(p.as_posix())

    print(f"✅ Archivos modificados: {len(files_changed)}")
    print(f"✅ Reemplazos totales aprox.: {total}")
    for f in files_changed[:30]:
        print(" -", f)
    if len(files_changed) > 30:
        print(f" ... y {len(files_changed)-30} más")

if __name__ == "__main__":
    main()
