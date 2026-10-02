"""Level0 -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from ships import NormalSpaceship
from space import StartWorld

__all__ = ["Level0"]


class Level0(StartWorld):
    """Leere Welt mit einem Raumschiff -- der Einstieg.

    Die einzige Welt, die ein Raumschiff mitbringt: Hier soll man sofort
    loslegen koennen, ohne erst eines einsetzen zu muessen.
    """

    __slots__ = ()

    START = (0, 5)

    def __init__(self) -> None:
        super().__init__(9, 9)
        self.add_object(NormalSpaceship(), *self.START)
