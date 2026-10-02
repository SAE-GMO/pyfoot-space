"""Raumschiffe mit Sensorik.

Waehrend ein `Spaceship` seine Anweisungen blind ausfuehrt, kann ein
`SensorSpaceship` seine Umgebung wahrnehmen. Diese Trennung ist Absicht:
Die Sensorik wird im Kurs erst eingefuehrt, wenn Verzweigungen an der Reihe
sind und man mit den Antworten auch etwas anfangen kann.
"""

from __future__ import annotations

from pyfoot import EAST, NORTH, SOUTH, WEST

from .asteroid import Asteroid
from .power_up import PowerUp
from .spaceship import Spaceship

__all__ = ["SensorSpaceship"]


class SensorSpaceship(Spaceship):
    """Ein Raumschiff, das seine Umgebung wahrnehmen kann."""

    __slots__ = ()

    def is_power_up_here(self) -> bool:
        """Liegt auf dem eigenen Feld ein PowerUp?"""
        return self.object_at_offset(0, 0, PowerUp) is not None

    def can_move(self) -> bool:
        """Ist das Feld vor dem Raumschiff frei?

        Frei heisst: Es liegt innerhalb der Welt und es liegt kein Asteroid
        darauf.
        """
        dx, dy = self.direction_offset()
        target_x = self.x + dx
        target_y = self.y + dy
        world = self.world
        if not world.contains(target_x, target_y):
            return False
        return not world.objects_at(target_x, target_y, Asteroid)

    def is_facing_north(self) -> bool:
        """Schaut das Raumschiff nach Norden?"""
        return self.rotation == NORTH

    def is_facing_south(self) -> bool:
        """Schaut das Raumschiff nach Sueden?"""
        return self.rotation == SOUTH

    def is_facing_east(self) -> bool:
        """Schaut das Raumschiff nach Osten?"""
        return self.rotation == EAST

    def is_facing_west(self) -> bool:
        """Schaut das Raumschiff nach Westen?"""
        return self.rotation == WEST

    # Hinweis fuer spaetere Kapitel:
    # Die Methoden is_asteroid_left() und is_asteroid_right() fehlen hier
    # absichtlich. Sie zu schreiben ist eine Aufgabe im Kapitel zu den
    # logischen Verknuepfungen und darf hier nicht vorweggenommen werden.
