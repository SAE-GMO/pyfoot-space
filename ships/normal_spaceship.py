"""Das Raumschiff fuer den Einstieg.

Diese Datei gehoert dir. Schreibe deine Anweisungen in `init` -- sie wird
beim Start genau einmal ausgefuehrt, von oben nach unten.
"""

from __future__ import annotations

from space import Spaceship

__all__ = ["NormalSpaceship"]


class NormalSpaceship(Spaceship):
    """Ein ganz normales Raumschiff."""

    # Zaehlt die eigenen Attribute auf -- wie die Felder einer Klasse in Java.
    # Fuer `self.counter` traegst du hier `("counter",)` ein.
    __slots__ = ()

    def init(self) -> None:
        """Hier kannst du alle Anweisungen eintragen, die das Schiff ausfuehren soll."""
        self.move()
        self.drop_power_up()
        self.move()
        self.turn_left()
