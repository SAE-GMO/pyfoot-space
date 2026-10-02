"""Prueft Vorlage und Bildzuweisung an den echten Kursklassen.

Editor-Anforderungsdokument B4 und B5. Gearbeitet wird auf Kopien in einem
Testordner; die Kursdateien selbst werden nie veraendert.
"""

from __future__ import annotations

import ast
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

from pyfoot.editor import codegen
from pyfoot.editor.mode import callable_members
from ships import NormalSpaceship
from space import PowerUp, SensorSpaceship, Spaceship

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POWER_UP_SOURCE = PROJECT_ROOT / "space" / "actors" / "power_up.py"


# ----------------------------------------------------------------------
# B4 -- neue Unterklasse
# ----------------------------------------------------------------------


def test_die_vorlage_nimmt_den_kurzen_einfuhrweg() -> None:
    """`from space import Spaceship`, nicht der Weg ueber das Untermodul."""
    text = codegen.render_subclass(Spaceship, "MyShip")

    assert "from space import Spaceship" in text
    assert "space.actors.spaceship" not in text


def test_die_vorlage_legt_init_an() -> None:
    """`init` ist im Kurs die Methode, in die geschrieben wird."""
    text = codegen.render_subclass(Spaceship, "MyShip")

    assert "class MyShip(Spaceship):" in text
    assert "def init(self) -> None:" in text


def test_die_vorlage_liefert_keine_fehlenden_methoden_mit() -> None:
    """Didaktische Auflage E2: `turn_right` bleibt Aufgabe der Schueler:innen."""
    text = codegen.render_subclass(Spaceship, "MyShip")

    assert "turn_right" not in text
    assert "is_asteroid_left" not in text


def test_die_vorlage_traegt_slots() -> None:
    """`__slots__` wirkt nur, wenn es jede Klasse der Kette hat.

    Eine im Editor erzeugte Unterklasse ohne die Angabe holt das `__dict__`
    fuer alle Instanzen zurueck und hebt den Schutz der gesamten Hierarchie
    auf -- auch fuer die Klassen aus `pyfoot` und `space`.
    """
    text = codegen.render_subclass(Spaceship, "MyShip")

    assert "__slots__ = ()" in text


def test_die_neue_klasse_ist_sofort_verwendbar(tmp_path: Path) -> None:
    """Anforderung B4: ohne Nacharbeit lauffaehig."""
    path = codegen.create_subclass(Spaceship, "MyShip", folder=tmp_path)

    specification = importlib.util.spec_from_file_location("my_ship_test", path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    try:
        specification.loader.exec_module(module)
        created = module.MyShip  # type: ignore[attr-defined]
        ship = created()
    finally:
        del sys.modules[specification.name]

    assert isinstance(ship, Spaceship)
    assert not created.__abstractmethods__, "Die Klasse darf nichts Offenes haben."
    assert not hasattr(ship, "__dict__"), "Die Vorlage darf kein `__dict__` oeffnen."


def test_auch_ein_sensorschiff_laesst_sich_ableiten(tmp_path: Path) -> None:
    path = codegen.create_subclass(SensorSpaceship, "Scout", folder=tmp_path)

    text = path.read_text(encoding="utf-8")
    assert "from space import SensorSpaceship" in text
    ast.parse(text)


def test_die_kursdateien_bleiben_unberuehrt(tmp_path: Path) -> None:
    before = POWER_UP_SOURCE.read_text(encoding="utf-8")

    codegen.create_subclass(Spaceship, "MyShip", folder=tmp_path)

    assert POWER_UP_SOURCE.read_text(encoding="utf-8") == before


# ----------------------------------------------------------------------
# B5 -- Bild zuweisen
# ----------------------------------------------------------------------


@pytest.fixture
def power_up_copy(tmp_path: Path) -> Path:
    """Legt eine Arbeitskopie der Akteursdatei an."""
    target = tmp_path / "power_up.py"
    shutil.copyfile(POWER_UP_SOURCE, target)
    return target


def test_die_bilder_des_projekts_werden_gefunden() -> None:
    images = codegen.available_images()

    assert "power_up.png" in images
    assert "asteroid.png" in images


def test_ein_bild_laesst_sich_zuweisen(power_up_copy: Path) -> None:
    codegen.assign_image(PowerUp, "asteroid.png", path=power_up_copy)

    text = power_up_copy.read_text(encoding="utf-8")
    assert 'Image.from_file("asteroid.png")' in text
    assert 'Image.from_file("power_up.png")' not in text
    ast.parse(text)


def test_nur_die_gemeinte_klasse_aendert_sich(power_up_copy: Path) -> None:
    """In der Datei stehen zwei Klassen."""
    codegen.assign_image(PowerUp, "asteroid.png", path=power_up_copy)

    text = power_up_copy.read_text(encoding="utf-8")
    assert "class RandomPowerUp(PowerUp):" in text
    assert "def construction_code(self) -> str:" in text


def test_vor_dem_zuweisen_entsteht_eine_sicherungskopie(power_up_copy: Path) -> None:
    original = power_up_copy.read_text(encoding="utf-8")

    backup = codegen.assign_image(PowerUp, "asteroid.png", path=power_up_copy)

    assert backup.read_text(encoding="utf-8") == original


# ----------------------------------------------------------------------
# D1 -- was das Menue eines Raumschiffs zeigt
# ----------------------------------------------------------------------


def test_das_menue_zeigt_die_kursbefehle() -> None:
    ship = NormalSpaceship()
    members = callable_members(ship)

    for expected in ("move", "turn_left", "collect_power_up", "drop_power_up"):
        assert expected in members, expected


def test_das_menue_taeuscht_keine_fehlenden_befehle_vor() -> None:
    """Didaktische Auflage E2 -- sonst suchten Schueler:innen an falscher Stelle."""
    members = callable_members(NormalSpaceship())

    assert "turn_right" not in members


def test_befehle_mit_werten_erscheinen_nicht() -> None:
    """`say` braucht einen Text und ist deshalb nicht dabei (D3)."""
    assert "say" not in callable_members(NormalSpaceship())


def test_die_wahrnehmung_erscheint_nur_beim_sensorschiff() -> None:
    plain = callable_members(NormalSpaceship())
    assert "can_move" not in plain
