"""Gemeinsame Helfer der Tests.

Getrennt von `conftest.py`, damit auch Werkzeuge ausserhalb von pytest die
Testmodule einlesen koennen. Mitbenutzt vom privaten Projekt pyfoot-course:
Dessen Musterloesungen und `tools/render_figure.py` binden diesen Helfer ein.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pyfoot.world import World

__all__ = ["world_with"]

_W = TypeVar("_W", bound=World)


def world_with(world_class: type[_W], ship_class: type, **kwargs: Any) -> _W:
    """Baut eine Welt und setzt ein Raumschiff auf ihr Startfeld.

    Ausser `Level0` bringt keine Welt ein Raumschiff mit -- es einzusetzen ist
    Aufgabe der Schueler:innen. Dieser Helfer tut fuer den Test genau das, was
    sie in der Oberflaeche tun: ein Objekt erzeugen und auf `START` ziehen.
    """
    welt = world_class(**kwargs)
    # `Level0` bringt ein Raumschiff mit; die Schueler:innen nehmen es heraus.
    # Bliebe es stehen, liefe sein `init()` mit -- und ein Test pruefte die
    # Arbeit zweier Schiffe (Befund vom 26.09.2026, siehe
    # `test_das_zielbild_zeigt_die_loesung` in pyfoot-course).
    from space import Spaceship

    for schiff in welt.objects(Spaceship):
        welt.remove_object(schiff)
    start: tuple[int, int] = getattr(world_class, "START", (0, 0))
    welt.add_object(ship_class(), *start)
    return welt
