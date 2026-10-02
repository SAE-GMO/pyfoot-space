"""Stellt sicher, dass der Kursinhalt ohne Maus und Tastatur auskommt.

Anforderungsdokument 4.10.5: PyFoot stellt Eingabe bereit (G5), im Projekt
`Space` wird sie aber nicht verwendet (G7). Der Grund ist didaktisch: Die
Aufgaben des Kurses fuehren eine Anweisungsfolge aus und sollen nicht von
Eingaben abhaengen. Ein Test haelt das fest, damit es nicht unbemerkt
einreisst.

Geprueft wird der Quelltext, nicht die Laufzeit -- ein zur Laufzeit nie
erreichter Aufruf waere sonst unsichtbar.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COURSE_CODE = PROJECT_ROOT / "space"

#: Namen aus PyFoot, die Eingaben abfragen.
INPUT_NAMES = frozenset(
    {
        "is_key_down",
        "get_key",
        "mouse_info",
        "mouse_clicked",
        "mouse_pressed",
        "mouse_dragged",
        "mouse_moved",
        "MouseInfo",
    }
)

#: Module, die nicht eingebunden werden duerfen.
FORBIDDEN_MODULES = frozenset({"pyfoot.input", "pygame"})

#: Ausnahme: Dieses Werkzeug erzeugt die Bilddateien und zeichnet sie mit
#: pygame. Es gehoert nicht zum Kursinhalt und laeuft nur bei der Lehrkraft.
TOOLS_WITHOUT_COURSE_CONTENT = frozenset({"generate_assets.py"})


def source_files() -> list[Path]:
    """Liefert alle Python-Dateien des Kursinhalts."""
    return sorted(COURSE_CODE.rglob("*.py"))


def course_files() -> list[Path]:
    """Liefert die Dateien, die im Unterricht gelesen und ausgefuehrt werden."""
    return [p for p in source_files() if p.name not in TOOLS_WITHOUT_COURSE_CONTENT]


def test_es_gibt_ueberhaupt_quelltext_zu_pruefen() -> None:
    """Sonst waeren die folgenden Tests stillschweigend wirkungslos."""
    assert len(source_files()) >= 5


@pytest.mark.parametrize("path", source_files(), ids=lambda p: p.name)
def test_keine_eingabefunktion_wird_verwendet(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in INPUT_NAMES:
            used.add(node.id)
        elif isinstance(node, ast.Attribute) and node.attr in INPUT_NAMES:
            used.add(node.attr)

    assert not used, (
        f"{path.name} verwendet Eingabe: {', '.join(sorted(used))}. "
        "Der Kursinhalt bleibt eingabefrei (Anforderung G7)."
    )


@pytest.mark.parametrize("path", course_files(), ids=lambda p: p.name)
def test_kein_eingabemodul_wird_eingebunden(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)

    forbidden = imported & FORBIDDEN_MODULES
    assert not forbidden, (
        f"{path.name} bindet {', '.join(sorted(forbidden))} ein. "
        "Der Kursinhalt spricht nur PyFoot an und bleibt eingabefrei."
    )


def test_die_eingabe_ist_in_pyfoot_aber_vorhanden() -> None:
    """Gegenprobe: G7 verbietet die Verwendung, nicht das Vorhandensein (G5)."""
    import pyfoot

    for name in sorted(INPUT_NAMES):
        assert hasattr(pyfoot, name), f"PyFoot fehlt die Eingabefunktion {name}."
