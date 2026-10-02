"""Level7Grid -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld

__all__ = ["Level7Grid"]


class Level7Grid(StartWorld):
    """Ein leeres Gitter aus 8 mal 8 Feldern.

    Die Welt fuer Kapitel 06: Was hier steht, tragen die Schueler:innen selbst
    ein -- aus einer Liste heraus. Das Startfeld ist die linke obere Ecke,
    damit sich die Welt Zeile fuer Zeile ablaufen laesst.
    """

    __slots__ = ()

    #: Start in der linken oberen Ecke -- von dort laeuft man die Welt ab.
    START = (0, 0)

    def __init__(self) -> None:
        super().__init__(8, 8)
