"""Level4aPowerUpStreet -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import PowerUp, RandomAsteroid

__all__ = ["Level4aPowerUpStreet"]


class Level4aPowerUpStreet(StartWorld):
    """Eine Strasse aus PowerUps mit einem Asteroiden als Wegmarke.

    Der Asteroid liegt mal auf der einen, mal auf der anderen Seite -- und
    manchmal gar nicht. Zum Ausprobieren laesst er sich in der Oberflaeche
    mit der Maus verschieben.
    """

    __slots__ = ()

    #: Start auf dem ersten PowerUp der Strasse.
    START = (1, 5)

    def __init__(self) -> None:
        super().__init__(10, 10)

    def prepare(self) -> None:
        for x in range(1, 8):
            self.add_object(PowerUp(), x, 5)
        self.add_object(RandomAsteroid(0.5), 5, 6)
