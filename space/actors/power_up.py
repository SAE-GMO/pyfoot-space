"""PowerUps -- die Objekte, die ein Raumschiff einsammeln und ablegen kann."""

from __future__ import annotations

from pyfoot import Actor, Image, World, random_number

__all__ = ["PowerUp", "RandomPowerUp"]


class PowerUp(Actor):
    """Ein PowerUp, das auf einem Feld liegt."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(image=Image.from_file("power_up.png"))


class RandomPowerUp(PowerUp):
    """Ein PowerUp, das nur mit einer bestimmten Wahrscheinlichkeit erscheint.

    Sobald es einer Welt hinzugefuegt wird, entscheidet der Zufall, ob es
    bestehen bleibt.
    """

    __slots__ = ("_probability",)

    def __init__(self, probability: float = 0.5) -> None:
        """Erzeugt ein PowerUp mit zufaelligem Bestand.

        Args:
            probability: Wahrscheinlichkeit zwischen 0.0 und 1.0, mit der das
                PowerUp bestehen bleibt. 1.0 bedeutet: bleibt immer.
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError(
                f"Die Wahrscheinlichkeit muss zwischen 0.0 und 1.0 liegen, war {probability}."
            )
        super().__init__()
        self._probability = probability

    @property
    def probability(self) -> float:
        """Wahrscheinlichkeit, mit der das PowerUp bestehen bleibt."""
        return self._probability

    def construction_code(self) -> str:
        """Nennt die Wahrscheinlichkeit mit, damit sie beim Sichern bleibt."""
        return f"{type(self).__name__}({self._probability})"

    def on_added_to_world(self, world: World) -> None:
        """Entscheidet beim Einfuegen, ob das PowerUp bestehen bleibt."""
        if random_number(1000) >= self._probability * 1000:
            world.remove_object(self)
