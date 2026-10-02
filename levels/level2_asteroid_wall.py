"""Level2AsteroidWall -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import Asteroid, RandomAsteroid

__all__ = ["Level2AsteroidWall"]


class Level2AsteroidWall(StartWorld):
    """Eine senkrechte Asteroidenwand mit einer zufaelligen Luecke."""

    __slots__ = ()

    #: Start auf Hoehe der Luecke -- sonst waere die Wand nie zu durchfliegen.
    START = (0, 3)

    def __init__(self) -> None:
        super().__init__(8, 8)

    def prepare(self) -> None:
        for y in range(8):
            if y == 3:
                self.add_object(RandomAsteroid(0.5), 3, y)
            else:
                self.add_object(Asteroid(), 3, y)
