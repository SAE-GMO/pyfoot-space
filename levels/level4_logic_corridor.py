"""Level4LogicCorridor -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import Asteroid, PowerUp

__all__ = ["Level4LogicCorridor"]


class Level4LogicCorridor(StartWorld):
    """Ein Gang zwischen zwei Asteroidenreihen, mit Luecken und PowerUps.

    Die Welt zu den Uebungen ueber logische Verknuepfungen: Je nachdem, wie
    eine Bedingung geklammert ist, kommt das Raumschiff an einer anderen
    Stelle zum Stehen.
    """

    __slots__ = ()

    #: Start auf dem ersten PowerUp der Reihe.
    START = (1, 4)

    def __init__(self) -> None:
        super().__init__(15, 10)

    def prepare(self) -> None:
        walls = {3: (1, 2, 4, 6, 7, 8, 9), 5: (1, 2, 4, 6, 7, 9)}
        for y, columns in walls.items():
            for x in columns:
                self.add_object(Asteroid(), x, y)

        for x in (1, 2, 3, 5):
            self.add_object(PowerUp(), x, 4)
