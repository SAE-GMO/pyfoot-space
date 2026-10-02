"""Level4dTunnel -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import Asteroid, PowerUp

__all__ = ["Level4dTunnel"]


class Level4dTunnel(StartWorld):
    """Ein zweiter gewundener Gang -- dieselbe Aufgabe, anderer Verlauf.

    Dieselbe Loesung muss auch hier zum Ziel fuehren.
    """

    __slots__ = ()

    #: Start am Anfang des Gangs, rechts unten.
    START = (9, 8)

    def __init__(self) -> None:
        super().__init__(10, 10)

    def prepare(self) -> None:
        walls = {
            4: (1, 2, 3, 4, 5, 6, 7),
            5: (1, 7),
            6: (1, 3, 4, 5, 7),
            7: (1, 3, 5, 7, 8, 9),
            8: (1, 3, 5),
            9: (5, 6, 7, 8, 9),
        }
        for y, columns in walls.items():
            for x in columns:
                self.add_object(Asteroid(), x, y)

        self.add_object(PowerUp(), 2, 9)
