"""Die gemeinsame Grundlage der Kurswelten.

Die Welten selbst liegen in `levels/` -- eine Datei je Welt. Sie gehoeren
den Schueler:innen und duerfen umgebaut werden. Diese Grundklasse gehoert
zum Kursinhalt und bleibt hier.
"""

from __future__ import annotations

from .space_world import SpaceWorld
from .start_marker import start_background

__all__ = ["StartWorld"]


class StartWorld(SpaceWorld):
    """Gemeinsame Grundlage der Startwelten.

    Richtet die Ausgangslage ueber `prepare` ein -- **ohne Raumschiff**. Das
    setzen die Schueler:innen selbst ein, mit der Oberflaeche: Rechtsklick auf
    die Klasse, `X() erzeugen`, und auf `START` ziehen. Das richtige Raumschiff
    in die richtige Welt zu setzen ist selbst Lerninhalt.

    Einzige Ausnahme ist `Level0`: Dort steht von Anfang an ein Raumschiff,
    damit der Einstieg ohne Vorbereitung gelingt.

    Das Feld `START` ist im Hintergrund markiert, mit einem Pfeil in
    Blickrichtung (siehe `start_marker.py`).
    """

    __slots__ = ()

    #: Feld, auf dem das Raumschiff stehen soll.
    START: tuple[int, int] = (0, 0)

    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)
        self.set_background(
            start_background(width, height, SpaceWorld.CELL_SIZE, self.START)
        )
        self.prepare()

    def prepare(self) -> None:
        """Richtet die Ausgangslage ein.

        Unterklassen ueberschreiben diese Methode.
        """
