"""Level4cTunnel -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import Asteroid, PowerUp

__all__ = ["Level4cTunnel"]


class Level4cTunnel(StartWorld):
    """Ein gewundener Gang aus Asteroiden; am Ende liegt ein PowerUp.

    Der Gang ist genau ein Feld breit und hat keine Abzweigungen.
    """

    __slots__ = ()

    #: Start am Anfang des Gangs, unten links.
    START = (0, 8)

    def __init__(self) -> None:
        super().__init__(10, 10)

    def prepare(self) -> None:
        walls = {
            1: (0, 2),
            2: (0, 2),
            3: (0, 2, 3, 4, 5, 6),
            4: (0, 6),
            5: (0, 1, 2, 3, 4, 6),
            6: (4, 6),
            7: (0, 1, 2, 3, 4, 6),
            8: (6,),
            9: (0, 1, 2, 3, 4, 5, 6),
        }
        for y, columns in walls.items():
            for x in columns:
                self.add_object(Asteroid(), x, y)

        self.add_object(PowerUp(), 1, 0)
