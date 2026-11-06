"""Baut die Kursbibliothek fuer CodeLab: `dist\\Space-CodeLab.zip`.

CodeLab prueft die Abgaben der Schueler:innen automatisch. Dafuer braucht
jeder Testlauf die Welten und Raumschiffe dieses Projekts -- als
**Kursbibliothek** in dem Format, das CodeLab vorgibt (Anforderung in
`codelab/STATUS.md`, Abschnitt „Kursbibliothek und Python-Pakete je Kurs“):

    codelab-bibliothek.yaml   format, version, name, release, language, env
    lib/                      kommt in jedem Testlauf vor die Abgabe in den Suchpfad
        pyfoot/  space/  levels/
        ships_template/       Vorlagen fuer `ships` (siehe unten)

**Warum `ships_template/` und nicht `ships/`.** `ships` ist das Paket der
Schueler:innen; in CodeLab bilden es die Tests aus der Abgabe nach. Manche
Welt braucht aber ein Raumschiff, das nicht jede Abgabe mitbringt: `Level0`
bindet `NormalSpaceship` ein. Die Vorlage springt ein, wenn die Abgabe die
Datei nicht enthaelt -- abgegebene Dateien gehen vor.

`pygame` gehoert nicht hinein: Es ist kompiliert und kommt ueber die
Python-Pakete des Kurses in das Image von CodeLab.

Aufruf (im Projektordner):
    python tools\\build_codelab_library.py           -> dist\\Space-CodeLab.zip
    python tools\\build_codelab_library.py --out x   -> anderer Zielordner

Das Werkzeug ist fuer die Lehrkraft gedacht; es geht nicht ins Schuelerpaket.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import get_pyfoot  # noqa: E402 -- liegt neben dieser Datei

#: Der Projektordner, aus dem Ort dieser Datei bestimmt.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Name der fertigen Datei.
LIBRARY_NAME = "Space-CodeLab.zip"

#: Ordner, die vollstaendig nach `lib/` gehen.
FOLDERS = ["pyfoot", "space", "levels"]

#: Dateien aus `ships/`, die als Vorlage nach `lib/ships_template/` gehen.
SHIP_TEMPLATES = ["normal_spaceship.py"]

#: Was nicht mitgeht.
SKIP_NAMES = {"__pycache__", ".mypy_cache", ".pytest_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".bak", ".tmp"}

#: Umgebung fuer jeden Testlauf: pygame ohne Fenster und ohne Ton.
ENV = {
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "PYGAME_HIDE_SUPPORT_PROMPT": "1",
}


def release(root: Path = PROJECT_ROOT) -> str:
    """Der Versions-Tag dieses Stands: `v` und die Version aus `pyproject.toml`."""
    with (root / "pyproject.toml").open("rb") as datei:
        return f"v{tomllib.load(datei)['project']['version']}"


def manifest(version: str) -> str:
    """`codelab-bibliothek.yaml` -- von Hand geschrieben, ohne YAML-Paket."""
    zeilen = [
        "# Kursbibliothek fuer CodeLab, erzeugt von tools/build_codelab_library.py",
        "format: codelab-bibliothek",
        "version: 1",
        "name: Space",
        f"release: {version}",
        "language: python",
        "env:",
        *(f'  {name}: "{wert}"' for name, wert in ENV.items()),
    ]
    return "\n".join(zeilen) + "\n"


def collect(root: Path = PROJECT_ROOT) -> list[tuple[Path, str]]:
    """Sammelt die Dateien der Bibliothek: Quelle und Pfad im Archiv."""
    chosen: list[tuple[Path, str]] = []
    for name in FOLDERS:
        for path in sorted((root / name).rglob("*")):
            relative = path.relative_to(root)
            if (
                path.is_file()
                and path.suffix not in SKIP_SUFFIXES
                and not any(part in SKIP_NAMES for part in relative.parts)
            ):
                chosen.append((path, f"lib/{relative.as_posix()}"))
    for name in SHIP_TEMPLATES:
        chosen.append((root / "ships" / name, f"lib/ships_template/{name}"))
    # Die Lizenz von Space reist mit; die von PyFoot liegt schon in pyfoot/.
    chosen.append((root / "LICENSE", "lib/LICENSE"))
    return chosen


def build(target: Path, root: Path = PROJECT_ROOT) -> Path:
    """Schreibt die Bibliothek als ZIP-Datei."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("codelab-bibliothek.yaml", manifest(release(root)))
        for source, name in collect(root):
            archive.write(source, name)
    return target


def main(arguments: list[str]) -> int:
    """Baut die Bibliothek und meldet, was hineingekommen ist."""
    parser = argparse.ArgumentParser(description="Baut die Kursbibliothek fuer CodeLab.")
    parser.add_argument("--out", default="dist", help="Zielordner (Vorgabe: dist)")
    options = parser.parse_args(arguments)

    try:
        pyfoot_version = get_pyfoot.ensure()
    except (get_pyfoot.PyFootMissing, LookupError) as fehler:
        print(f"PyFoot fehlt, die Bibliothek wurde nicht gebaut: {fehler}")
        return 1

    ziel = build(PROJECT_ROOT / options.out / LIBRARY_NAME)
    with zipfile.ZipFile(ziel) as archive:
        anzahl = len(archive.namelist())
    print(f"Kursbibliothek {release()} mit PyFoot {pyfoot_version}: {anzahl} Dateien -> {ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
