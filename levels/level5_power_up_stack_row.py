"""Level5PowerUpStackRow -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld
from space import RandomPowerUp

__all__ = ["Level5PowerUpStackRow"]


class Level5PowerUpStackRow(StartWorld):
    """Eine Reihe aus fuenf Stapeln, jeder von zufaelliger Hoehe.

    Auf jedem der Felder (3, 5) bis (7, 5) liegen bis zu zehn PowerUps
    uebereinander -- wie viele es wirklich sind, entscheidet der Zufall.
    Ein Stapel kann auch leer bleiben; dann ist der Weg bis zum ersten
    Stapel laenger.
    """

    __slots__ = ()

    #: Start links neben der Reihe.
    START = (0, 5)

    #: Feld des ersten und des letzten Stapels.
    FIRST_STACK = 3
    LAST_STACK = 7

    #: Hoechstzahl der PowerUps je Stapel.
    STACK_LIMIT = 10

    def __init__(self) -> None:
        super().__init__(15, 10)

    def prepare(self) -> None:
        for x in range(self.FIRST_STACK, self.LAST_STACK + 1):
            for _ in range(self.STACK_LIMIT):
                self.add_object(RandomPowerUp(0.5), x, 5)
