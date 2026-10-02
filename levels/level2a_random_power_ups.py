"""Level2aRandomPowerUps -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import RandomPowerUp

__all__ = ["Level2aRandomPowerUps"]


class Level2aRandomPowerUps(StartWorld):
    """Zwei PowerUps, die nur manchmal da sind."""

    __slots__ = ()

    #: Start auf dem ersten der beiden Felder.
    START = (3, 3)

    def __init__(self) -> None:
        super().__init__(8, 8)

    def prepare(self) -> None:
        self.add_object(RandomPowerUp(0.5), 3, 3)
        self.add_object(RandomPowerUp(0.5), 4, 3)
