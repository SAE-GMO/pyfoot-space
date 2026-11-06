"""Prueft die Markierung des Startfelds.

Der Anlass: In welche Ecke das Raumschiff gehoert, stand bisher nur im
Arbeitsblatt. Fuer die automatische Pruefung der Abgaben muessen Welt, Blatt
und Test denselben Start meinen -- deshalb zeigt die Welt ihn selbst.
"""

from __future__ import annotations

from collections.abc import Callable

import pygame
import pytest

from levels import Level0, Level1PowerUpRow, Level2AsteroidWall
from space import SpaceWorld, StartWorld
from space.assets.generate_assets import CELL_SIZE, START_COLOR
from space.worlds.start_marker import start_background

CELL = SpaceWorld.CELL_SIZE


def _pixel(world: StartWorld, x: int, y: int, dx: int, dy: int) -> tuple[int, int, int]:
    """Liest einen Bildpunkt des Hintergrunds, relativ zur Ecke eines Feldes."""
    surface: pygame.Surface = world._background._surface  # type: ignore[union-attr]
    farbe = surface.get_at((x * CELL + dx, y * CELL + dy))
    return (farbe.r, farbe.g, farbe.b)


def _nah_an_markierung(farbe: tuple[int, int, int]) -> bool:
    """Ein Bildpunkt des Rahmens: deutlich blau-hell, nicht Sternenhimmel."""
    r, g, b = farbe
    return b > 150 and g > 120 and b > r + 60


@pytest.mark.parametrize("welt", [Level0, Level1PowerUpRow, Level2AsteroidWall])
def test_der_rahmen_liegt_auf_dem_startfeld(welt: Callable[[], StartWorld]) -> None:
    """Links in der Mitte des Startfelds verlaeuft der Rahmen."""
    world = welt()
    x, y = world.START

    assert _nah_an_markierung(_pixel(world, x, y, 4, CELL // 2))


def test_andere_felder_bleiben_unmarkiert() -> None:
    """Nur das Startfeld traegt den Rahmen."""
    world = Level2AsteroidWall()
    x, y = Level2AsteroidWall.START

    for anderes in [(x + 1, y), (x, y + 1), (7, 7)]:
        assert not _nah_an_markierung(_pixel(world, *anderes, 4, CELL // 2)), anderes


def test_der_pfeil_zeigt_nach_rechts() -> None:
    """Die Spitze sitzt rechts in der Mitte: Neue Raumschiffe schauen nach rechts."""
    world = Level1PowerUpRow()
    x, y = Level1PowerUpRow.START

    spitze = _pixel(world, x, y, CELL - 9, CELL // 2)
    gegenueber = _pixel(world, x, y, 9, CELL // 2)
    assert _nah_an_markierung(spitze)
    assert not _nah_an_markierung(gegenueber)


def test_die_markierung_ist_kein_objekt_der_welt() -> None:
    """Sie zaehlt bei `objects()` nicht mit und laesst sich nicht verschieben."""
    world = Level1PowerUpRow()

    assert len(world.objects()) == 20


def test_ein_start_ausserhalb_der_welt_bleibt_unmarkiert() -> None:
    """Eine fehlerhafte Angabe darf die Welt nicht zum Absturz bringen."""
    bild = start_background(3, 3, CELL, (5, 5))

    assert bild.width == 3 * CELL and bild.height == 3 * CELL


def test_das_markierungsbild_passt_zur_feldgroesse() -> None:
    """Sonst wuerde es bei jeder Welt neu skaliert -- und unscharf."""
    assert CELL_SIZE == SpaceWorld.CELL_SIZE


def test_die_farbe_hebt_sich_vom_himmel_ab() -> None:
    """Hell und kuehl: weder tuerkis wie das PowerUp noch grau wie der Asteroid."""
    r, g, b, _ = START_COLOR
    assert b > r + 100 and b > 200
