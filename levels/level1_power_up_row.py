"""Level1PowerUpRow -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import PowerUp

__all__ = ["Level1PowerUpRow"]


class Level1PowerUpRow(StartWorld):
    """Eine durchgehende Reihe von PowerUps am oberen Rand."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(20, 25)

    def prepare(self) -> None:
        for x in range(20):
            self.add_object(PowerUp(), x, 0)
