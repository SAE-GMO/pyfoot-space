"""Hinweisfenster fuer Fehlermeldungen.

Wird eine Anweisung ausgefuehrt, die nicht moeglich ist, erscheint der Grund
zusaetzlich zur Fehlermeldung mitten in der Welt. Genau diese Rueckmeldung
brauchen Schueler:innen beim Suchen nach Fehlern.
"""

from __future__ import annotations

from pyfoot import Actor, Color, Image, World

__all__ = ["PopupMessage", "show_alert"]


class PopupMessage(Actor):
    """Ein Hinweistext, der ueber der Welt liegt."""

    __slots__ = ()

    def __init__(self, text: str, size: int = 30) -> None:
        super().__init__(
            image=Image.from_text(
                text,
                size,
                Color.WHITE,
                background=Color(150, 30, 40, 235),
                border=Color.WHITE,
            )
        )


def show_alert(world: World, text: str) -> None:
    """Zeigt einen Hinweis mitten in der Welt an.

    Ein bereits sichtbarer Hinweis wird zuvor entfernt, damit sich mehrere
    Meldungen nicht ueberlagern.
    """
    for previous in world.objects(PopupMessage):
        world.remove_object(previous)
    world.add_object(PopupMessage(text), world.width // 2, world.height // 2)
