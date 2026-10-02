"""Ein Raumschiff, das eine Wahrheitstabelle ausrechnet.

Diese Datei gehoert dir. Sie fliegt nicht, sondern gibt auf der Konsole aus,
was ein logischer Ausdruck fuer alle Belegungen ergibt -- damit laesst sich
eine von Hand ausgefuellte Tabelle ueberpruefen.

Aendere den Ausdruck in `result`, um eine andere Tabelle zu bekommen.
"""

from __future__ import annotations

from space import Spaceship

__all__ = ["BooleanSpaceship"]


class BooleanSpaceship(Spaceship):
    """Gibt eine Wahrheitstabelle auf der Konsole aus."""

    # Eigene Attribute hier eintragen: `__slots__ = ("counter",)`, den Typ
    # bei Bedarf darunter als `counter: int`.
    __slots__ = ()

    def init(self) -> None:
        """Geht alle Belegungen von a und b durch."""
        a = False
        for _ in range(2):
            b = False
            for _ in range(2):
                result = not (a and not b)
                print(f"a = {str(a):<5}  b = {str(b):<5}  ->  {result}")
                b = not b
            a = not a
