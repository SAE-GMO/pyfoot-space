"""Die gemeinsame Grundlage der Kurswelten.

Die Welten selbst liegen in `levels/` -- eine Datei je Welt. Sie gehoeren
den Schueler:innen und duerfen umgebaut werden. Diese Grundklasse gehoert
zum Kursinhalt und bleibt hier.
"""

from __future__ import annotations

from .space_world import SpaceWorld

__all__ = ["StartWorld"]


class StartWorld(SpaceWorld):
    """Gemeinsame Grundlage der Startwelten.

    Richtet die Ausgangslage ueber `prepare` ein -- **ohne Raumschiff**. Das
    setzen die Schueler:innen selbst ein, mit der Oberflaeche: Rechtsklick auf
    die Klasse, `X() erzeugen`, und auf `START` ziehen. Das richtige Raumschiff
    in die richtige Welt zu setzen ist selbst Lerninhalt.

    Einzige Ausnahme ist `Level0`: Dort steht von Anfang an ein Raumschiff,
    damit der Einstieg ohne Vorbereitung gelingt.
    """

    __slots__ = ()

    #: Feld, auf dem das Raumschiff stehen soll.
    START: tuple[int, int] = (0, 0)

    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)
        self.prepare()

    def prepare(self) -> None:
        """Richtet die Ausgangslage ein.

        Unterklassen ueberschreiben diese Methode.
        """
