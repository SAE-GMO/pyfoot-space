"""Das Raumschiff fuer die Uebungen zu logischen Verknuepfungen.

Diese Datei gehoert dir. Fuer Aufgabe 2 des Blattes AB05c nimmst du bei
**einem** Abschnitt die Kommentarzeichen weg, laesst ihn laufen und
vergleichst das Ergebnis mit deiner Vermutung.

Zwei der Abschnitte brauchen `is_asteroid_left()` und `is_asteroid_right()`.
Diese Methoden gibt es noch nicht -- du schreibst sie selbst (Aufgabe 2b).
"""

from __future__ import annotations

from space import SensorSpaceship

__all__ = ["LogicSpaceship"]


class LogicSpaceship(SensorSpaceship):
    """Prueft Vermutungen ueber logische Verknuepfungen."""

    # Eigene Attribute hier eintragen: `__slots__ = ("counter",)`, den Typ
    # bei Bedarf darunter als `counter: int`.
    __slots__ = ()

    def init(self) -> None:
        """Hier steht der Abschnitt, den du gerade untersuchst."""
        # a)
        # while self.is_power_up_here() or self.is_asteroid_left() and self.is_asteroid_right():
        #     self.move()

        # b)
        # while (self.is_power_up_here() or self.is_asteroid_left()) and self.is_asteroid_right():
        #     self.move()

        # c)
        # while (not self.is_power_up_here() or self.is_asteroid_left()) and self.can_move():
        #     self.move()
