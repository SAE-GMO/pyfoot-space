"""Level6ForLoop -- eine Welt des Kurses.

Diese Datei gehoert dir. Baue die Welt um, wie du magst -- oder lege
mit der Oberflaeche eine eigene daneben.
"""

from __future__ import annotations

from space import StartWorld

__all__ = ["Level6ForLoop"]


class Level6ForLoop(StartWorld):
    """Eine leere Welt mit viel Platz -- fuer die Zaehlschleife.

    Gross genug fuer ein Quadrat aus 10 mal 10 Feldern. Das Raumschiff
    startet unten links, damit nach oben und nach rechts Platz bleibt.
    """

    __slots__ = ()

    #: Start unten links, mit Platz nach oben und nach rechts.
    START = (1, 10)

    def __init__(self) -> None:
        super().__init__(13, 13)
