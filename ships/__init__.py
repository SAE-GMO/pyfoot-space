"""Eigene Raumschiffe und Akteure.

Hier liegen die Klassen, die **du** schreibst. Die Oberflaeche legt neue
Akteursklassen ebenfalls hier ab, und nur hier darf sie wieder loeschen --
der Kursinhalt in `space/` bleibt unberuehrt.

`normal_spaceship.py` ist mitgeliefert. Es ist der Einstieg: Schreibe deine
ersten Anweisungen einfach dort hinein.
"""

from __future__ import annotations

from .boolean_spaceship import BooleanSpaceship
from .caesar_spaceship import CaesarSpaceship
from .for_loop_spaceship import ForLoopSpaceship
from .logic_spaceship import LogicSpaceship
from .normal_spaceship import NormalSpaceship

__all__ = [
    "BooleanSpaceship",
    "CaesarSpaceship",
    "ForLoopSpaceship",
    "LogicSpaceship",
    "NormalSpaceship",
]
