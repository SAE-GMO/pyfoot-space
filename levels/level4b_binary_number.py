"""Level4bBinaryNumber -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import Asteroid, PowerUp, RandomAsteroid

__all__ = ["Level4bBinaryNumber"]


class Level4bBinaryNumber(StartWorld):
    """Eine Binaerzahl aus PowerUps unter einer Reihe von Asteroiden.

    Die Asteroiden geben die Anzahl der Stellen an. Ein PowerUp bedeutet 1,
    ein leeres Feld 0.

    Die Welt gibt es in zwei Versionen. Mit `varying_length` erscheint der
    erste Asteroid nur manchmal -- die Zahl ist dann mal acht, mal neun
    Stellen lang, und ein Programm muss beides schaffen. Ohne ihn hat sie
    immer acht Stellen.
    """

    __slots__ = ("_varying_length",)

    #: Start rechts neben der Zahl.
    START = (10, 3)

    def __init__(self, varying_length: bool = True) -> None:
        """Baut die Welt auf.

        Args:
            varying_length: Ob die Zahl mal acht, mal neun Stellen hat.
        """
        # Vor `super()`, denn dieses ruft bereits `prepare` auf.
        self._varying_length = varying_length
        super().__init__(12, 6)

    def prepare(self) -> None:
        if self._varying_length:
            self.add_object(RandomAsteroid(0.3), 1, 2)
        for x in range(2, 10):
            self.add_object(Asteroid(), x, 2)

        for x in (2, 5, 8, 9):
            self.add_object(PowerUp(), x, 3)
