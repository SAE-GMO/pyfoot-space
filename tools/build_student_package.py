"""Baut das Paket, das die Schueler:innen bekommen.

Das Projekt enthaelt mehr, als in den Unterricht gehoert: Tests und
Werkzeuge der Lehrkraft. (Die **Musterloesungen** liegen gar nicht hier,
sondern im privaten Projekt pyfoot-course.)

Dieses Werkzeug erzeugt daraus ein Paket mit genau dem, was gebraucht wird.
Die Bibliothek PyFoot kommt in der Version hinein, die `pyproject.toml`
festlegt; fehlt sie oder ist sie veraltet, wird sie vorher geholt
(`tools/get_pyfoot.py`).

Aufruf (im Projektordner):
    python tools\\build_student_package.py                 -> dist\\Space.zip
    python tools\\build_student_package.py --folder        -> dist\\Space\\
    python tools\\build_student_package.py --out abgabe    -> anderer Zielort

Aufgenommen wird nach einer **Erlaubnisliste**, nicht nach einer
Ausschlussliste: Was hier nicht steht, kommt nicht ins Paket. Eine spaeter
hinzugefuegte Datei der Lehrkraft kann so nicht versehentlich mitgehen.

Das Werkzeug ist fuer die Lehrkraft gedacht; im Unterricht wird es nicht
gebraucht.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import get_pyfoot  # noqa: E402 -- liegt neben dieser Datei
import update_space  # noqa: E402

#: Der Projektordner, aus dem Ort dieser Datei bestimmt.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Ordner, die vollstaendig mitgehen.
FOLDERS = ["pyfoot", "space", "ships", "levels", "docs", ".vscode"]

#: Einzelne Dateien im Projektordner.
FILES = ["main_space.py", "main_editor.py", "README.md", "LICENSE", "pyproject.toml"]

#: Werkzeuge, die Schueler:innen selbst aufrufen. Alles Uebrige aus `tools/`
#: -- etwa `check_project.py` und `get_pyfoot.py` -- bleibt draussen.
TOOLS = [
    "check_environment.py",
    "check_code.py",
    "update_space.py",
    "mypy_student.ini",
]

#: Das Manifest des Pakets. Es wird beim Packen erzeugt, nicht kopiert, und
#: sagt spaeter beim Auffrischen, welche Dateien unveraendert sind -- nur die
#: darf `update_space.py` ueberschreiben.
MANIFEST = "tools/paket.json"

#: Was innerhalb der aufgenommenen Ordner nicht mitgeht.
SKIP_NAMES = {"__pycache__", ".mypy_cache", ".pytest_cache", ".venv"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".bak", ".tmp"}

#: Name des obersten Ordners im Paket. Ohne ihn verstreuten sich die Dateien
#: beim Entpacken.
PACKAGE_NAME = "Space"


class PackageReport(NamedTuple):
    """Auskunft darueber, was ins Paket gewandert ist."""

    target: Path
    files: int
    bytes: int
    skipped_tools: list[str]

    def summary(self) -> str:
        """Fasst das Ergebnis in einem Satz zusammen."""
        groesse = self.bytes / 1024
        return f"{self.files} Datei(en), {groesse:.0f} KiB -> {self.target}"


def is_wanted(path: Path) -> bool:
    """Gibt an, ob eine Datei ins Paket gehoert."""
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    return not any(part in SKIP_NAMES for part in path.parts)


def collect(root: Path = PROJECT_ROOT) -> list[tuple[Path, str]]:
    """Sammelt die Dateien des Pakets.

    Returns:
        Paare aus Quellpfad und Zielpfad innerhalb des Pakets.
    """
    chosen: list[tuple[Path, str]] = []

    for name in FOLDERS:
        folder = root / name
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_file() and is_wanted(path.relative_to(root)):
                chosen.append((path, path.relative_to(root).as_posix()))

    for name in FILES:
        path = root / name
        if path.is_file():
            chosen.append((path, name))

    for name in TOOLS:
        path = root / "tools" / name
        if path.is_file():
            chosen.append((path, f"tools/{name}"))

    return chosen


def missing_tools(root: Path = PROJECT_ROOT) -> list[str]:
    """Nennt die Werkzeuge, die bewusst draussen bleiben."""
    tools = root / "tools"
    if not tools.is_dir():
        return []
    return sorted(
        p.name for p in tools.glob("*") if p.is_file() and p.name not in TOOLS
    )


def package_version() -> str:
    """Nennt die Version: Tag und Uhrzeit des Packens."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def manifest(chosen: list[tuple[Path, str]], version: str) -> str:
    """Baut das Manifest des Pakets.

    Es nennt zu jeder Datei eine Pruefsumme. `update_space.py` erkennt damit
    spaeter, an welchen Dateien gearbeitet wurde -- nur die uebrigen darf es
    ueberschreiben. Gerechnet wird mit derselben Funktion wie dort, damit
    beide Seiten dasselbe Ergebnis bekommen.
    """
    inhalt = {relative: source.read_bytes() for source, relative in chosen}
    return update_space.manifest_of(inhalt, version)


def build_folder(target: Path, root: Path = PROJECT_ROOT) -> PackageReport:
    """Legt das Paket als Ordner an."""
    if target.exists():
        shutil.rmtree(target)

    total = 0
    chosen = collect(root)
    for source, relative in chosen:
        ziel = target / relative
        ziel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, ziel)
        total += ziel.stat().st_size

    ziel = target / MANIFEST
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(manifest(chosen, package_version()), encoding="utf-8")

    return PackageReport(target, len(chosen) + 1, total, missing_tools(root))


def build_zip(target: Path, root: Path = PROJECT_ROOT) -> PackageReport:
    """Legt das Paket als ZIP-Datei an."""
    target.parent.mkdir(parents=True, exist_ok=True)
    chosen = collect(root)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for source, relative in chosen:
            archive.write(source, f"{PACKAGE_NAME}/{relative}")
        archive.writestr(f"{PACKAGE_NAME}/{MANIFEST}", manifest(chosen, package_version()))

    return PackageReport(
        target, len(chosen) + 1, target.stat().st_size, missing_tools(root)
    )


def main(arguments: list[str]) -> int:
    """Baut das Paket und meldet, was hineingekommen ist."""
    parser = argparse.ArgumentParser(
        description="Baut das Schuelerpaket ohne Tests und Lehrkraftwerkzeuge."
    )
    parser.add_argument(
        "--folder", action="store_true", help="als Ordner statt als ZIP anlegen"
    )
    parser.add_argument("--out", default="dist", help="Zielordner (Vorgabe: dist)")
    options = parser.parse_args(arguments)

    try:
        version = get_pyfoot.ensure()
    except (get_pyfoot.PyFootMissing, LookupError) as fehler:
        print(f"PyFoot fehlt, das Paket wurde nicht gebaut: {fehler}")
        return 1

    ziel = PROJECT_ROOT / options.out
    if options.folder:
        report = build_folder(ziel / PACKAGE_NAME)
    else:
        report = build_zip(ziel / f"{PACKAGE_NAME}.zip")

    print("Schuelerpaket gebaut")
    print("=" * 52)
    print(f"  {report.summary()}")
    print(f"  mit PyFoot {version}")
    print("")
    print("Bewusst nicht enthalten:")
    print("  tests\\                  die Tests des Projekts")
    for name in report.skipped_tools:
        print(f"  tools\\{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
