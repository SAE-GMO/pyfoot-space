"""Prueft die Trennung von Kursinhalt und eigenen Klassen.

Editor-Anforderungsdokument B4b: Was die Oberflaeche anlegt, gehoert nicht in
die Bibliothek des Basisprojekts, sondern in eigene Ordner -- `ships/` fuer
Akteure, `levels/` fuer Welten.

Dazu die Gegenprobe zur wichtigsten Eigenschaft dieser Trennung: Der
Kursinhalt darf **nicht** davon abhaengen, dass die Dateien im Schuelerordner
fehlerfrei sind.
"""

from __future__ import annotations

import ast
from pathlib import Path

from helpers import world_with

from pyfoot.editor import codegen
from ships import NormalSpaceship
from levels import Level0
from space import PowerUp, SensorSpaceship, SpaceWorld, Spaceship, StartWorld

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHIPS = PROJECT_ROOT / "ships"
LEVELS = PROJECT_ROOT / "levels"
COURSE = PROJECT_ROOT / "space"


# ----------------------------------------------------------------------
# Die Ordner
# ----------------------------------------------------------------------


def test_beide_ordner_sind_pakete() -> None:
    """Erst als Paket laesst sich `from ships import ...` schreiben."""
    assert (SHIPS / "__init__.py").is_file()
    assert (LEVELS / "__init__.py").is_file()


def test_das_startschiff_liegt_im_schuelerordner() -> None:
    assert (SHIPS / "normal_spaceship.py").is_file()
    assert codegen.source_file(NormalSpaceship).parent == SHIPS


def test_das_startschiff_ist_kurz_geblieben() -> None:
    """Der Grund fuer die Auslagerung: nicht vom uebrigen Code erschlagen."""
    zeilen = (SHIPS / "normal_spaceship.py").read_text(encoding="utf-8").splitlines()

    assert len(zeilen) < 30, "Die Einstiegsdatei soll ueberschaubar bleiben."


def test_das_startschiff_ist_ein_raumschiff() -> None:
    assert issubclass(NormalSpaceship, Spaceship)


# ----------------------------------------------------------------------
# Wohin die Oberflaeche schreibt
# ----------------------------------------------------------------------


def test_neue_akteure_kommen_nach_ships() -> None:
    assert codegen.class_folder_for(Spaceship) == SHIPS
    assert codegen.class_folder_for(SensorSpaceship) == SHIPS
    assert codegen.class_folder_for(PowerUp) == SHIPS


def test_neue_welten_kommen_nach_levels() -> None:
    assert codegen.class_folder_for(SpaceWorld) == LEVELS
    assert codegen.class_folder_for(Level0) == LEVELS


def test_nichts_landet_mehr_in_der_bibliothek() -> None:
    """Der Befund, der zu B4b gefuehrt hat."""
    for cls in (Spaceship, SensorSpaceship, PowerUp, SpaceWorld, Level0):
        ziel = codegen.class_folder_for(cls)
        assert COURSE not in ziel.parents and ziel != COURSE, cls.__name__


# ----------------------------------------------------------------------
# Der Kursinhalt haengt nicht am Schuelerordner
# ----------------------------------------------------------------------


def module_level_imports(path: Path) -> set[str]:
    """Sammelt die Module, die eine Datei beim Einlesen einbindet.

    Einfuhren innerhalb einer Funktion zaehlen nicht mit -- sie laufen erst
    beim Aufruf.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module.split(".")[0])
    return names


def test_der_kursinhalt_bindet_den_schuelerordner_nicht_beim_start_ein() -> None:
    """Die entscheidende Eigenschaft der Trennung.

    Wuerde eine Datei unter `space/` den Ordner `ships` schon beim Einlesen
    einbinden, legte ein Tippfehler in der Schuelerdatei `import space` lahm
    -- und damit jede Aufgabe, auch die ohne Bezug dazu.
    """
    schuldige = [
        p.relative_to(PROJECT_ROOT)
        for p in sorted(COURSE.rglob("*.py"))
        if {"ships", "levels"} & module_level_imports(p)
    ]

    assert not schuldige, (
        "Diese Kursdateien binden den Schuelerordner beim Start ein: "
        + ", ".join(str(p) for p in schuldige)
    )


def test_das_startlevel_setzt_trotzdem_ein_raumschiff_ein() -> None:
    """Level0 ist der Einstieg -- ohne Schiff koennte niemand loslegen."""
    world = Level0()

    ships: list[Spaceship] = world.objects(Spaceship)
    assert len(ships) == 1
    assert isinstance(ships[0], NormalSpaceship)
    assert (ships[0].x, ships[0].y) == Level0.START


def test_ein_selbst_gesetztes_raumschiff_steht_in_der_welt() -> None:
    """So, wie es die Schueler:innen in der Oberflaeche tun."""
    class ProbeShip(Spaceship):
        def init(self) -> None:
            pass

    from levels import Level1PowerUpRow

    world = world_with(Level1PowerUpRow, ProbeShip)

    ships: list[Spaceship] = world.objects(Spaceship)
    assert len(ships) == 1
    assert isinstance(ships[0], ProbeShip)
    assert (ships[0].x, ships[0].y) == Level1PowerUpRow.START


def test_die_uebrigen_welten_bleiben_ohne_schiff() -> None:
    """Entscheidung des Auftraggebers: Nur `Level0` bringt eines mit.

    In allen anderen Welten setzen die Schueler:innen ihr Raumschiff
    selbst ein -- das richtige Schiff in die richtige Welt zu bringen ist
    selbst Lerninhalt.
    """
    from levels import Level1PowerUpRow

    world = Level1PowerUpRow()

    assert world.objects(Spaceship) == []


# ----------------------------------------------------------------------
# B8 -- der Loeschschutz am echten Projekt
# ----------------------------------------------------------------------


def test_kein_kursbestandteil_laesst_sich_loeschen() -> None:
    """Die Erlaubnisliste muss den vorgegebenen Teil abdecken.

    Die Welten stehen **nicht** mehr darin: Sie liegen seit M7 in `levels/`
    und gehoeren den Schueler:innen (siehe unten).
    """
    from space import Asteroid, PopupMessage, RandomPowerUp

    geschuetzt = [
        Spaceship,
        SensorSpaceship,
        PowerUp,
        RandomPowerUp,
        Asteroid,
        PopupMessage,
        SpaceWorld,
        StartWorld,
    ]
    for cls in geschuetzt:
        erlaubt, grund = codegen.can_delete(cls)
        assert erlaubt is False, f"{cls.__name__} duerfte nicht loeschbar sein"
        assert grund, f"{cls.__name__} nennt keinen Grund"


def test_die_welten_gehoeren_den_schuelern_und_sind_loeschbar() -> None:
    """Entscheidung des Auftraggebers: Die Level liegen in `levels/`.

    Sie sollen umgebaut werden duerfen -- dann darf die Oberflaeche sie auch
    wieder wegraeumen. Geschuetzt bleibt nur die Grundklasse `StartWorld`.
    """
    from levels import Level0, Level1PowerUpRow

    for cls in (Level0, Level1PowerUpRow):
        erlaubt, grund = codegen.can_delete(cls)
        assert erlaubt is True, f"{cls.__name__}: {grund}"


def test_auch_pyfoot_selbst_ist_geschuetzt() -> None:
    from pyfoot import Actor, World

    assert codegen.can_delete(Actor)[0] is False
    assert codegen.can_delete(World)[0] is False


def test_das_startschiff_gehoert_den_schuelern_und_ist_loeschbar() -> None:
    """`normal_spaceship.py` liegt bewusst im eigenen Bereich.

    Die Datei wird im Unterricht zur Datei der Schueler:innen -- also darf
    die Oberflaeche sie auch wieder wegraeumen.
    """
    erlaubt, grund = codegen.can_delete(NormalSpaceship)

    assert erlaubt is True, grund


# ----------------------------------------------------------------------
# B7 -- Weltwechsel am echten Projekt
# ----------------------------------------------------------------------


def test_jede_kurswelt_laesst_sich_ohne_werte_erzeugen() -> None:
    """Sonst waere sie ueber das Kontextmenue nicht erreichbar."""
    import levels
    from pyfoot.editor.mode import can_construct

    welten = [
        getattr(levels, name)
        for name in levels.__all__
        if isinstance(getattr(levels, name), type)
        and issubclass(getattr(levels, name), SpaceWorld)
    ]
    assert len(welten) >= 10
    for welt in welten:
        assert can_construct(welt), f"{welt.__name__} braucht Werte im Konstruktor"


def test_nur_das_startlevel_bringt_ein_schiff_mit() -> None:
    """Der Einstieg soll ohne Vorbereitung gelingen -- alles Weitere nicht."""
    from levels import Level1PowerUpRow, Level2AsteroidWall

    assert len(Level0().objects(Spaceship)) == 1
    assert Level1PowerUpRow().objects(Spaceship) == []
    assert Level2AsteroidWall().objects(Spaceship) == []
