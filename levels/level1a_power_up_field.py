"""Level1aPowerUpField -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import PowerUp

__all__ = ["Level1aPowerUpField"]


class Level1aPowerUpField(StartWorld):
    """Ein rechteckiges Feld aus PowerUps."""

    __slots__ = ()

    #: Start auf der linken oberen Ecke des Feldes.
    START = (3, 3)

    def __init__(self) -> None:
        super().__init__(8, 8)

    def prepare(self) -> None:
        for y in range(3, 6):
            for x in range(3, 7):
                self.add_object(PowerUp(), x, y)
