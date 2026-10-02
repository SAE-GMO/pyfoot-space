"""Level3fRandomPowerUpField -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import Asteroid, PowerUp, RandomPowerUp

__all__ = ["Level3fRandomPowerUpField"]


class Level3fRandomPowerUpField(StartWorld):
    """Gemischte Ausgangslage aus PowerUps unterschiedlicher Haeufigkeit."""

    __slots__ = ()

    #: Start auf der linken oberen Ecke des mittleren Feldes.
    START = (3, 1)

    def __init__(self) -> None:
        super().__init__(8, 8)

    def prepare(self) -> None:
        self.add_object(RandomPowerUp(0.9), 3, 3)
        self.add_object(RandomPowerUp(0.9), 4, 3)
        self.add_object(RandomPowerUp(0.1), 5, 3)

        for y in (1, 2):
            for x in (3, 4, 5):
                self.add_object(RandomPowerUp(0.5), x, y)

        for x in range(self.width):
            self.add_object(PowerUp(), x, 5)
            self.add_object(Asteroid(), x, 6)
