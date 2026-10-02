"""Level3cPowerUpStack -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import RandomPowerUp

__all__ = ["Level3cPowerUpStack"]


class Level3cPowerUpStack(StartWorld):
    """Ein Stapel aus vielen PowerUps auf einem einzigen Feld."""

    __slots__ = ()

    #: Start auf dem Stapel.
    START = (2, 2)

    def __init__(self) -> None:
        super().__init__(8, 8)

    def prepare(self) -> None:
        for _ in range(250):
            self.add_object(RandomPowerUp(0.5), 2, 2)
