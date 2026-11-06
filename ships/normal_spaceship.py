"""Das Raumschiff fuer den Einstieg -- diese Datei gehoert dir.

Jede Aufgabe hat ihre eigene Methode; `init` ruft die auf, an der du arbeitest.
"""

from __future__ import annotations

from space import Spaceship

__all__ = ["NormalSpaceship"]


class NormalSpaceship(Spaceship):
    """Ein ganz normales Raumschiff."""

    __slots__ = ()

    def init(self) -> None:
        self.draw_letter()

    def draw_letter(self) -> None:
        """Aufgabe 1: der erste Buchstabe deines Vornamens aus PowerUps."""
        self.move()
        self.drop_power_up()
        self.move()
        self.turn_left()

    def fly_eight(self) -> None:
        """Aufgabe 2: die Acht aus dem Zielbild, ein PowerUp auf jedem Feld."""
