"""Prueft das Sichern eines Weltaufbaus an den echten Kursdateien.

PyFoot prueft die Quelltexterzeugung an eigenen Vorlagen. Hier wird sie
gegen eine Datei aus `levels/` gefuehrt -- dort liegt seit M7 jede Welt
einzeln, und genau diese Dateien werden im Unterricht veraendert.

Gearbeitet wird ausschliesslich auf einer Kopie in einem Testordner. Die
Kursdateien selbst werden nie angeruehrt.
"""

from __future__ import annotations

import ast
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

from pyfoot import Actor, World
from pyfoot.editor.codegen import save_world
from ships import NormalSpaceship
from levels import (
    Level1aPowerUpField,
    Level2AsteroidWall,
)
from space import (
    Asteroid,
    PowerUp,
    RandomAsteroid,
    RandomPowerUp,
    Spaceship,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEVEL_SOURCE = PROJECT_ROOT / "levels" / "level1a_power_up_field.py"
LEVELS = PROJECT_ROOT / "levels"


@pytest.fixture
def level_copy(tmp_path: Path) -> Path:
    """Legt eine Arbeitskopie der Kursdatei an."""
    target = tmp_path / LEVEL_SOURCE.name
    shutil.copyfile(LEVEL_SOURCE, target)
    return target


def ship_of(world: Level1aPowerUpField | Level2AsteroidWall) -> Spaceship:
    """Setzt ein Raumschiff auf das Startfeld und liefert es.

    Ausser `Level0` bringt keine Welt eines mit -- beim Sichern muss aber
    eines da sein, damit Anforderung A5 (Schiff als `START` schreiben)
    ueberhaupt greift.
    """
    ships: list[Spaceship] = world.objects(Spaceship)
    if not ships:
        ship = NormalSpaceship()
        world.add_object(ship, *type(world).START)
        return ship
    return ships[0]


def test_die_kursdatei_ist_vorhanden() -> None:
    """Sonst liefen die folgenden Tests stillschweigend ins Leere."""
    assert LEVEL_SOURCE.is_file()


def test_ein_level_laesst_sich_sichern(level_copy: Path) -> None:
    world = Level1aPowerUpField()
    ship = ship_of(world)

    report = save_world(world, ship, path=level_copy)

    text = level_copy.read_text(encoding="utf-8")
    assert report.objects == 12, "Das PowerUp-Feld hat 3 mal 4 Felder."
    assert "self.add_object(PowerUp(), 3, 3)" in text
    ast.parse(text)


def test_die_uebrigen_weltdateien_bleiben_unberuehrt(tmp_path: Path) -> None:
    """Seit M7 liegt jede Welt in einer eigenen Datei -- 15 andere.

    Gesichert wird immer nur die eine. Waeren die Dateien vertauschbar,
    verlore man beim Sichern fremde Welten.
    """
    vorher = {
        datei.name: datei.read_text(encoding="utf-8")
        for datei in sorted(LEVELS.glob("*.py"))
    }
    assert len(vorher) > 10, "Es muessen viele einzelne Weltdateien sein."

    kopie = tmp_path / LEVEL_SOURCE.name
    kopie.write_text(LEVEL_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    world = Level1aPowerUpField()
    save_world(world, ship_of(world), path=kopie)

    nachher = {
        datei.name: datei.read_text(encoding="utf-8")
        for datei in sorted(LEVELS.glob("*.py"))
    }
    assert nachher == vorher


def test_der_rumpf_der_klasse_bleibt_erhalten(level_copy: Path) -> None:
    """Alles ausserhalb von `prepare` bleibt stehen (Anforderung A4)."""
    world = Level1aPowerUpField()

    save_world(world, ship_of(world), path=level_copy)
    after = level_copy.read_text(encoding="utf-8")

    for marker in (
        "from __future__ import annotations",
        "from space import StartWorld",
        '__all__ = ["Level1aPowerUpField"]',
        "class Level1aPowerUpField(StartWorld):",
    ):
        assert marker in after, marker


def test_das_raumschiff_wird_als_start_geschrieben(level_copy: Path) -> None:
    """Anforderung A5 -- sonst stuende das Schiff doppelt in der Welt."""
    world = Level1aPowerUpField()
    ship = ship_of(world)
    ship.set_location(6, 1)

    report = save_world(world, ship, path=level_copy)

    text = level_copy.read_text(encoding="utf-8")
    assert report.start == (6, 1)
    assert "    START = (6, 1)" in text
    assert "self.add_object(NormalSpaceship(), 6, 1)" not in text


def test_der_kommentar_ueber_start_bleibt_stehen(level_copy: Path) -> None:
    world = Level1aPowerUpField()
    ship = ship_of(world)
    ship.set_location(1, 1)

    save_world(world, ship, path=level_copy)

    text = level_copy.read_text(encoding="utf-8")
    assert "#: Start auf der linken oberen Ecke des Feldes." in text


def test_zufallswerte_bleiben_erhalten(level_copy: Path) -> None:
    """`RandomPowerUp(0.5)` darf nicht zu `RandomPowerUp()` werden.

    Die Wahrscheinlichkeit 1.0 sorgt dafuer, dass das PowerUp bestehen bleibt
    -- sonst entfernte es sich beim Einfuegen womoeglich selbst.
    """
    world = Level1aPowerUpField()
    world.add_object(RandomPowerUp(1.0), 0, 7)

    save_world(world, ship_of(world), path=level_copy)

    assert "self.add_object(RandomPowerUp(1.0), 0, 7)" in level_copy.read_text(
        encoding="utf-8"
    )


def test_eine_schleife_im_aufbau_wird_gemeldet(level_copy: Path) -> None:
    """Die Welten des Kurses bauen sich mit Schleifen auf."""
    world = Level1aPowerUpField()

    report = save_world(world, ship_of(world), path=level_copy)

    assert report.flattened is True, (
        "Der Verlust der Schleife muss gemeldet werden, damit niemand "
        "versehentlich lesbaren Code gegen eine lange Liste tauscht."
    )


def test_hinweistexte_werden_uebergangen(level_copy: Path) -> None:
    """Ein Hinweisfenster ist kein Teil des Weltaufbaus."""
    world = Level1aPowerUpField()
    world.alert("Achtung")

    report = save_world(world, ship_of(world), path=level_copy)

    assert "PopupMessage" in report.skipped
    assert "PopupMessage" not in level_copy.read_text(encoding="utf-8")


def load_copy(level_copy: Path) -> object:
    """Laedt die gesicherte Kopie als Modul.

    Die Datei bindet `space` absolut ein und laesst sich deshalb einzeln
    laden -- anders als frueher, als alle Welten in einem Paketmodul standen.
    """
    specification = importlib.util.spec_from_file_location(
        "levels._level_copy", level_copy
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    try:
        specification.loader.exec_module(module)
    finally:
        del sys.modules[specification.name]
    return module


def test_die_gesicherte_datei_baut_dieselbe_welt_auf(level_copy: Path) -> None:
    """Die Gegenprobe: Der erzeugte Aufbau muss dasselbe ergeben.

    Gewaehlt ist eine Welt ohne Zufall -- nur dann ist ein Vergleich Objekt
    fuer Objekt ueberhaupt aussagekraeftig.
    """
    world = Level1aPowerUpField()
    ship = ship_of(world)
    original: list[Actor] = world.objects()
    before = sorted(
        (type(a).__name__, a.x, a.y) for a in original if a is not ship
    )

    save_world(world, ship, path=level_copy)
    module = load_copy(level_copy)

    rebuilt: World = module.Level1aPowerUpField()  # type: ignore[attr-defined]
    # Das Raumschiff setzt die Welt selbst ueber `START` ein; verglichen wird
    # der Aufbau aus `prepare`, also alles ausser dem Schiff (Anforderung A5).
    alle: list[Actor] = rebuilt.objects()
    present = [a for a in alle if not isinstance(a, Spaceship)]
    after = sorted((type(a).__name__, a.x, a.y) for a in present)

    assert after == before


def test_zufall_bleibt_zufall() -> None:
    """Gesichert wird der Zufall selbst, nicht sein Ergebnis.

    Die Asteroidenwand hat eine zufaellige Luecke. Wuerde das Sichern das
    gewuerfelte Ergebnis festschreiben -- etwa als Wahrscheinlichkeit 1.0 --,
    laege die Luecke fortan immer an derselben Stelle, und die Aufgabe
    dahinter waere verloren.

    Geprueft wird ohne Welt: Ob ein zufaelliger Akteur ueberhaupt bestehen
    bleibt, entscheidet der Zufall -- das duerfte sonst ueber den Ausgang des
    Tests mitbestimmen.
    """
    assert RandomAsteroid(0.5).construction_code() == "RandomAsteroid(0.5)"
    assert RandomPowerUp(0.9).construction_code() == "RandomPowerUp(0.9)"


def test_die_kursdatei_selbst_bleibt_unveraendert(level_copy: Path) -> None:
    """Sicherheitsnetz: Kein Test darf die echte Datei anfassen."""
    world = Level1aPowerUpField()
    original = LEVEL_SOURCE.read_text(encoding="utf-8")

    save_world(world, ship_of(world), path=level_copy)

    assert LEVEL_SOURCE.read_text(encoding="utf-8") == original
    assert not LEVEL_SOURCE.with_suffix(".py.bak").exists()


def test_asteroiden_und_powerups_stehen_gemeinsam_im_aufbau(level_copy: Path) -> None:
    world = Level1aPowerUpField()
    world.add_object(Asteroid(), 7, 7)
    world.add_object(PowerUp(), 0, 0)

    save_world(world, ship_of(world), path=level_copy)

    text = level_copy.read_text(encoding="utf-8")
    assert "self.add_object(Asteroid(), 7, 7)" in text
    assert "self.add_object(PowerUp(), 0, 0)" in text
