"""Die Weltraumwelt, in der die Raumschiffe fliegen.

Eigenstaendige Neuentwicklung: Die Vorlage `WorldRabbitWorld.java` stammt von
Dritten und wurde bewusst nicht uebersetzt, sondern nur ihr Verhalten
uebernommen (Anforderungsdokument 4.9.2, Auflage 2).
"""

from __future__ import annotations

from pyfoot import World

from ..actors.popup_message import PopupMessage, show_alert

__all__ = ["SpaceWorld"]


class SpaceWorld(World):
    """Ein Gitterausschnitt des Weltraums.

    Bringt den Sternenhintergrund, die Zeichenreihenfolge der Objekte und die
    Anzeige von Hinweisen mit.
    """

    __slots__ = ()

    #: Kantenlaenge eines Feldes in Bildpunkten.
    CELL_SIZE: int = 60

    def __init__(self, width: int = 8, height: int = 8) -> None:
        """Erzeugt eine Weltraumwelt.

        Args:
            width: Anzahl der Spalten.
            height: Anzahl der Zeilen.
        """
        super().__init__(width, height, SpaceWorld.CELL_SIZE)

        # Lokale Einfuhr, damit sich Welt und Akteure nicht gegenseitig
        # importieren muessen.
        from ..actors.asteroid import Asteroid
        from ..actors.power_up import PowerUp
        from ..actors.spaceship import Spaceship

        self.set_background("starfield.png")
        # Hinweise liegen ganz oben, darunter die Raumschiffe.
        self.set_paint_order(PopupMessage, Spaceship, PowerUp, Asteroid)

    def alert(self, text: str) -> None:
        """Zeigt einen Hinweis mitten in der Welt an."""
        show_alert(self, text)

    def clear_alerts(self) -> None:
        """Entfernt alle angezeigten Hinweise."""
        for message in self.objects(PopupMessage):
            self.remove_object(message)
