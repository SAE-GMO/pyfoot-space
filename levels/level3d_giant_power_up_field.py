"""Level3dGiantPowerUpField -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import PowerUp

__all__ = ["Level3dGiantPowerUpField"]


class Level3dGiantPowerUpField(StartWorld):
    """Eine grosse Welt, in der jedes Feld ein PowerUp traegt."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(25, 25)

    def prepare(self) -> None:
        for x in range(25):
            for y in range(25):
                self.add_object(PowerUp(), x, y)
