"""Raumschiffe -- die Akteure, die im Kurs gesteuert werden.

`Spaceship` stellt die Grundbefehle bereit. Ein Raumschiff nimmt seine
Umgebung dabei bewusst *nicht* wahr: Es fuehrt seine Anweisungen blind aus
und meldet einen Fehler, wenn eine Anweisung nicht moeglich ist. Die
Wahrnehmung kommt erst mit `SensorSpaceship` dazu, wenn im Kurs die
Verzweigungen eingefuehrt werden.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import NoReturn

from pyfoot import Image, ScriptActor, redraws

from .asteroid import Asteroid
from .popup_message import show_alert
from .power_up import PowerUp

__all__ = ["Spaceship", "SpaceshipError"]


class SpaceshipError(RuntimeError):
    """Wird ausgeloest, wenn ein Raumschiff eine unmoegliche Anweisung erhaelt."""


class Spaceship(ScriptActor):
    """Ein Raumschiff, das Anweisungen von oben nach unten abarbeitet."""

    __slots__ = ("_power_ups",)

    #: Anzahl der PowerUps, die ein Raumschiff von Anfang an mitfuehrt.
    DEFAULT_POWER_UPS: int = 5000

    def __init__(self, power_ups: int = DEFAULT_POWER_UPS) -> None:
        """Erzeugt ein Raumschiff.

        Args:
            power_ups: Anzahl der PowerUps, die das Schiff mitfuehrt.
        """
        if power_ups < 0:
            raise ValueError("Die Anzahl der PowerUps darf nicht negativ sein.")
        super().__init__(image=Image.from_file("spaceship.png"))
        self._power_ups = power_ups

    @abstractmethod
    def init(self) -> None:
        """Hier stehen die Anweisungen, die das Raumschiff ausfuehren soll."""

    # ------------------------------------------------------------------
    # Zustand
    # ------------------------------------------------------------------

    @property
    def power_up_count(self) -> int:
        """Anzahl der PowerUps, die das Raumschiff gerade mitfuehrt."""
        return self._power_ups

    # ------------------------------------------------------------------
    # Fliegen
    # ------------------------------------------------------------------

    def move(self, distance: int = 1) -> None:
        """Fliegt in Blickrichtung weiter.

        Jedes Feld wird einzeln geprueft. Fuehrt der Weg aus der Welt hinaus
        oder auf einen Asteroiden, bricht der Flug mit einer Meldung ab.

        Args:
            distance: Anzahl der Felder. Negative Werte fliegen rueckwaerts.

        Raises:
            SpaceshipError: Wenn der Weg blockiert ist oder aus der Welt fuehrt.
        """
        step = 1 if distance >= 0 else -1
        for _ in range(abs(distance)):
            self._check_step(step)
            super().move(step)

    def _check_step(self, step: int) -> None:
        """Prueft, ob das naechste Feld angeflogen werden darf."""
        dx, dy = self.direction_offset()
        target_x = self.x + dx * step
        target_y = self.y + dy * step
        world = self.world

        if not world.contains(target_x, target_y):
            self._fail(
                "Hilfe, ich verlasse die Welt!",
                f"wollte von ({self.x}, {self.y}) nach ({target_x}, {target_y}) "
                "fliegen, aber dort endet die Welt.",
            )

        if world.objects_at(target_x, target_y, Asteroid):
            self._fail(
                "Autsch, ein Asteroid!",
                f"wollte von ({self.x}, {self.y}) nach ({target_x}, {target_y}) "
                "fliegen, aber dort liegt ein Asteroid.",
            )

    def turn_left(self) -> None:
        """Dreht das Raumschiff um eine Vierteldrehung nach links."""
        self.turn(-90)

    # ------------------------------------------------------------------
    # PowerUps
    # ------------------------------------------------------------------

    @redraws
    def collect_power_up(self) -> None:
        """Sammelt das PowerUp auf, das auf dem eigenen Feld liegt.

        Raises:
            SpaceshipError: Wenn auf dem Feld kein PowerUp liegt.
        """
        power_up = self.object_at_offset(0, 0, PowerUp)
        if power_up is None:
            self._fail(
                "Hier ist kein PowerUp!",
                f"wollte bei ({self.x}, {self.y}) ein PowerUp aufsammeln, "
                "aber dort liegt keines.",
            )
        self.world.remove_object(power_up)
        self._power_ups += 1

    @redraws
    def drop_power_up(self) -> None:
        """Legt ein PowerUp auf dem eigenen Feld ab.

        Raises:
            SpaceshipError: Wenn das Raumschiff keine PowerUps mehr mitfuehrt.
        """
        if self._power_ups <= 0:
            self._fail(
                "Keine PowerUps mehr an Bord!",
                f"wollte bei ({self.x}, {self.y}) ein PowerUp ablegen, "
                "hat aber keines mehr.",
            )
        self.world.add_object(PowerUp(), self.x, self.y)
        self._power_ups -= 1

    # ------------------------------------------------------------------
    # Ausgabe
    # ------------------------------------------------------------------

    @redraws
    def say(self, text: object) -> None:
        """Zeigt einen Text ueber dem Raumschiff an und gibt ihn aus."""
        row = self.y - 1
        if row < 0:
            row = self.y + 1
        self.world.show_text(str(text), self.x, row)
        print(f"{type(self).__name__} sagt: {text}")

    # ------------------------------------------------------------------
    # Fehlerbehandlung
    # ------------------------------------------------------------------

    def _fail(self, hint: str, reason: str) -> NoReturn:
        """Zeigt den Hinweis in der Welt an und loest einen Fehler aus.

        Raises:
            SpaceshipError: immer.
        """
        if self.has_world:
            show_alert(self.world, hint)
            self.update_screen()
        raise SpaceshipError(f"{type(self).__name__} {reason}")

