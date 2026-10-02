"""Prueft Loesungsdateien auf Typfehler und meldet sie auf der Konsole.

Dies ist die Konsolenversion der Warnungen, die VS Code beim Schreiben
anzeigt. Sie ist bewusst **nicht blockierend**: Sie meldet, was ihr auffaellt,
verhindert aber nichts. Das Programm laesst sich auch dann starten, wenn hier
etwas bemaengelt wird.

Geprueft wird milder als das Projekt selbst: Typangaben sind keine Pflicht,
aber die Rumpfe von Methoden ohne Angabe werden trotzdem durchgesehen. Ohne
diese Einstellung uebergeht die Pruefung sie stillschweigend und findet nichts.

Aufruf (im Projektordner):
    python tools\\check_code.py                 alle Loesungsdateien
    python tools\\check_code.py aufgabe01.py    nur eine bestimmte Datei
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

#: Ordner des Projekts selbst. Sie werden mit der strengeren Einstellung aus
#: pyproject.toml geprueft und hier ausgelassen.
PROJECT_PACKAGES = {"pyfoot", "space", "tools", "tests", "_structure"}

#: Der Projektordner wird aus dem Ort dieser Datei bestimmt, nicht aus dem
#: Arbeitsverzeichnis. Damit laesst sich die Pruefung von ueberall aufrufen.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG = Path(__file__).resolve().parent / "mypy_student.ini"


def solution_files(root: Path) -> list[Path]:
    """Sammelt die Loesungsdateien im Projektordner.

    Das sind alle Python-Dateien unmittelbar im Projektordner -- also die
    Dateien, die im Unterricht angelegt werden. Die Ordner des Projekts selbst
    bleiben aussen vor.
    """
    return sorted(
        path
        for path in root.glob("*.py")
        if path.is_file() and path.parent.name not in PROJECT_PACKAGES
    )


def run_mypy(files: list[Path]) -> tuple[int, str]:
    """Ruft mypy fuer die angegebenen Dateien auf.

    Returns:
        Rueckgabewert von mypy und die gesammelte Ausgabe.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--config-file",
            str(CONFIG),
            *[str(path.resolve()) for path in files],
        ],
        capture_output=True,
        text=True,
        # Aus dem Projektordner heraus, damit pyfoot und space gefunden werden --
        # unabhaengig davon, wo die Konsole gerade steht.
        cwd=str(PROJECT_ROOT),
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def main(arguments: list[str]) -> int:
    """Prueft die Loesungsdateien und meldet das Ergebnis.

    Der Rueckgabewert ist immer 0: Die Pruefung ist ein Hinweis, kein Verbot.
    """
    if arguments:
        # Angegebene Dateien zuerst im Arbeitsverzeichnis suchen, sonst im
        # Projektordner -- damit der Aufruf von ueberall gelingt.
        files = []
        missing = []
        for name in arguments:
            candidate = Path(name)
            if not candidate.is_file():
                candidate = PROJECT_ROOT / name
            if candidate.is_file():
                files.append(candidate)
            else:
                missing.append(name)
        if missing:
            for name in missing:
                print(f"Datei nicht gefunden: {name}")
            return 0
    else:
        files = solution_files(PROJECT_ROOT)

    if not files:
        print("Keine Loesungsdateien gefunden.")
        print("")
        print("Lege deine Loesung als eigene Datei im Projektordner an,")
        print("zum Beispiel als aufgabe01.py, und rufe die Pruefung erneut auf.")
        return 0

    print("Geprueft werden:")
    for path in files:
        print(f"  {path.name}")
    print("")

    try:
        code, output = run_mypy(files)
    except FileNotFoundError:
        print("mypy ist nicht installiert. Wende dich an den IT-Support.")
        return 0

    if output:
        print(output)
        print("")

    if code == 0:
        print("Keine Typfehler gefunden.")
    else:
        print("Hinweis: Diese Meldungen verhindern das Starten nicht.")
        print("Dein Programm laesst sich trotzdem ausfuehren -- meistens")
        print("steckt an den gemeldeten Stellen aber schon der Fehler.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
