"""Welten mit der Maus bearbeiten, sichern und zuruecksetzen (A4c, A5b, A5c, H7).

Anlass (12.09.2026): Beim Sichern kamen nur **neue** Objekte an. Ein
geloeschtes Raumschiff in `Level0` stand nach dem Zuruecksetzen wieder da.
Die Messung fand dazu einen zweiten, schwereren Fehler: `Level1PowerUpRow`
verlor beim Sichern das PowerUp auf (0, 0) -- auch ganz ohne Aenderung.

Die Tests arbeiten in einem eigenen Prozess mit einer Kopie des
Schuelerpakets: Sichern schreibt in `levels/`, und das Projekt selbst soll
dabei unberuehrt bleiben.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from build_student_package import build_folder  # noqa: E402

VORSPANN = textwrap.dedent(
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path.cwd()))

    from pyfoot import enable_ui, get_engine, set_world
    from levels import Level0, Level1PowerUpRow
    from space import PowerUp

    enable_ui()
    engine = get_engine()

    def inhalt():
        return sorted((type(a).__name__, a.x, a.y) for a in engine.world.objects())

    def sichern():
        engine.request_save()
        if engine.status.startswith("Achtung"):
            engine.request_save()
    """
)


@pytest.fixture
def paket(tmp_path: Path) -> Path:
    return build_folder(tmp_path / "Space").target


def ausfuehren(paket: Path, programm: str) -> dict[str, str]:
    """Fuehrt das Programm im Paket aus und liefert seine `NAME wert`-Zeilen."""
    (paket / "probe.py").write_text(VORSPANN + textwrap.dedent(programm), encoding="utf-8")
    umgebung = dict(os.environ)
    umgebung.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONIOENCODING="utf-8")
    umgebung.pop("PYFOOT_UI", None)
    ergebnis = subprocess.run(
        [sys.executable, "probe.py"],
        cwd=paket,
        env=umgebung,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    assert ergebnis.returncode == 0, ergebnis.stderr
    return dict(
        zeile.split(" ", 1) for zeile in ergebnis.stdout.splitlines() if " " in zeile
    )


def test_geloeschtes_raumschiff_bleibt_geloescht(paket: Path) -> None:
    zeilen = ausfuehren(
        paket,
        """
        set_world(Level0())
        mode = engine.edit_mode
        mode.enable()
        mode.select_at(*Level0.START)
        mode.remove_selected()
        mode.select_class(PowerUp)
        mode.place(3, 3)
        sichern()
        print("STATUS", engine.status)
        engine._perform_reset()
        print("INHALT", inhalt())
        """,
    )
    text = (paket / "levels" / "level0.py").read_text(encoding="utf-8")

    assert zeilen["INHALT"] == "[('PowerUp', 3, 3)]"
    assert "NormalSpaceship vom Startfeld entfernt" in zeilen["STATUS"]
    assert "NormalSpaceship" not in text, "Weder Anweisung noch Einfuhr bleiben stehen."
    assert "from space import PowerUp" in text, "Der kurze Weg, wie von Hand geschrieben."


def test_sichern_ohne_aenderung_verliert_nichts(paket: Path) -> None:
    """Der Befund: Das PowerUp auf dem geerbten Startfeld (0, 0) verschwand."""
    zeilen = ausfuehren(
        paket,
        """
        set_world(Level1PowerUpRow())
        vorher = inhalt()
        sichern()
        engine._perform_reset()
        print("GLEICH", inhalt() == vorher)
        print("ANZAHL", len(inhalt()))
        """,
    )

    assert zeilen["GLEICH"] == "True"
    assert zeilen["ANZAHL"] == "20"


def test_geloeschtes_powerup_bleibt_geloescht(paket: Path) -> None:
    zeilen = ausfuehren(
        paket,
        """
        set_world(Level1PowerUpRow())
        mode = engine.edit_mode
        mode.select_at(5, 0)
        mode.remove_selected()
        sichern()
        engine._perform_reset()
        print("DA", ("PowerUp", 5, 0) in inhalt())
        print("ANZAHL", len(inhalt()))
        """,
    )

    assert zeilen["DA"] == "False"
    assert zeilen["ANZAHL"] == "19"


def test_handaenderung_an_der_welt_wird_uebernommen(paket: Path) -> None:
    """H7 fuer Welten: Datei aendern, R -- ohne Neustart."""
    zeilen = ausfuehren(
        paket,
        """
        set_world(Level1PowerUpRow())
        datei = Path("levels/level1_power_up_row.py")
        datei.write_text(
            datei.read_text(encoding="utf-8").replace("range(20)", "range(4)"),
            encoding="utf-8",
        )
        engine._perform_reset()
        print("ANZAHL", len(inhalt()))
        print("STATUS", engine.status)
        """,
    )

    assert zeilen["ANZAHL"] == "4"
    assert zeilen["STATUS"].startswith("Neu eingebunden: level1_power_up_row.py")


def test_handaenderung_wird_vor_dem_sichern_gemeldet(paket: Path) -> None:
    """A4c: Sichern wuerde die Aenderung sonst stillschweigend ueberschreiben."""
    zeilen = ausfuehren(
        paket,
        """
        set_world(Level1PowerUpRow())
        datei = Path("levels/level1_power_up_row.py")
        datei.write_text(
            datei.read_text(encoding="utf-8").replace("range(20)", "range(4)"),
            encoding="utf-8",
        )
        engine.request_save()
        print("STATUS", engine.status)
        print("UNVERAENDERT", "range(4)" in datei.read_text(encoding="utf-8"))
        """,
    )

    assert "level1_power_up_row.py wurde von Hand geändert" in zeilen["STATUS"]
    assert zeilen["UNVERAENDERT"] == "True"
