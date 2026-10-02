"""Tests fuer die Typpruefung der Loesungsdateien."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import check_code  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent

FEHLERHAFT = """from levels import Level0
from space import Spaceship


class MyShip(Spaceship):
    def init(self):
        self.move("drei")
"""

FEHLERFREI = """from space import Spaceship


class MyShip(Spaceship):
    def init(self) -> None:
        self.move()
"""


def test_konfiguration_existiert() -> None:
    assert check_code.CONFIG.is_file()


def test_konfiguration_prueft_rumpfe_ohne_annotation() -> None:
    """Ohne diese Einstellung findet die Pruefung bei Schuelercode nichts."""
    text = check_code.CONFIG.read_text(encoding="utf-8")
    assert "check_untyped_defs = True" in text
    # Annotationen sind bewusst keine Pflicht.
    assert "disallow_untyped_defs" not in text
    assert "strict = True" not in text


def test_fehler_werden_gefunden(tmp_path: Path, monkeypatch: object) -> None:
    datei = tmp_path / "aufgabe.py"
    datei.write_text(FEHLERHAFT, encoding="utf-8")

    code, ausgabe = check_code.run_mypy([datei])

    assert code != 0
    assert "incompatible type" in ausgabe.lower()


def test_fehlerfreie_datei_meldet_nichts(tmp_path: Path) -> None:
    datei = tmp_path / "sauber.py"
    datei.write_text(FEHLERFREI, encoding="utf-8")

    code, ausgabe = check_code.run_mypy([datei])

    assert code == 0
    assert "no issues found" in ausgabe.lower()


def test_projektordner_werden_ausgelassen() -> None:
    """Nur Dateien unmittelbar im Projektordner gelten als Loesungen."""
    gefunden = check_code.solution_files(PROJECT)
    namen = {pfad.name for pfad in gefunden}

    assert "main_space.py" in namen
    # Nichts aus den Ordnern des Projekts selbst
    assert all(pfad.parent == PROJECT for pfad in gefunden)
    assert "spaceship.py" not in namen


def test_rueckgabewert_ist_immer_null(tmp_path: Path, capsys: object) -> None:
    """Die Pruefung ist ein Hinweis, kein Verbot -- sie blockiert nie."""
    datei = tmp_path / "kaputt.py"
    datei.write_text(FEHLERHAFT, encoding="utf-8")

    assert check_code.main([str(datei)]) == 0


def test_fehlende_datei_bricht_nicht_ab() -> None:
    assert check_code.main(["gibt_es_nicht_98765.py"]) == 0
