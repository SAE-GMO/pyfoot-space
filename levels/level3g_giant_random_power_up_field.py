"""Level3gGiantRandomPowerUpField -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import RandomPowerUp

__all__ = ["Level3gGiantRandomPowerUpField"]


class Level3gGiantRandomPowerUpField(StartWorld):
    """Eine grosse Welt, in der etwa jedes zweite Feld ein PowerUp traegt."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(25, 25)

    def prepare(self) -> None:
        for x in range(25):
            for y in range(25):
                self.add_object(RandomPowerUp(0.5), x, y)
