"""Ein Raumschiff, das eine Zaehlschleife benutzt.

Diese Datei gehoert dir. Sie ist der Ausgangspunkt fuer `AB08a`: Jemand hat
die Aufgabe schon geloest -- lies den Quelltext, aendere ihn und sieh nach,
was sich aendert.
"""

from __future__ import annotations

from space import Spaceship

__all__ = ["ForLoopSpaceship"]


class ForLoopSpaceship(Spaceship):
    """Legt eine Reihe aus genau zehn PowerUps."""

    # Eigene Attribute hier eintragen: `__slots__ = ("counter",)`, den
    # Typ bei Bedarf darunter als `counter: int`.
    __slots__ = ()

    def init(self) -> None:
        """Hier kannst du alle Anweisungen eintragen, die das Schiff ausfuehren soll."""
        for i in range(10):
            self.drop_power_up()
            self.move()
