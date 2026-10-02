"""Das Raumschiff, das verschluesseln kann -- die vorgegebene Grundlage.

Diese Klasse bringt die Hilfsmittel mit, die fuer die Caesar-Chiffre gebraucht
werden: zwei Alphabete, eine Ausgabe und die Suche nach einem Textbaustein.
Die Chiffre selbst schreiben die Schueler:innen in `ships/caesar_spaceship.py`.

Ein Text ist hier eine **Liste von Zeichen**, keine Zeichenkette -- so wie in
Kapitel 06. `list("HALLO")` macht aus einer Zeichenkette eine solche Liste,
`"".join(zeichen)` fuehrt wieder zurueck.
"""

from __future__ import annotations

from .spaceship import Spaceship

__all__ = ["CryptographicSpaceship"]

#: Erster und letzter Grossbuchstabe im ASCII-Zeichensatz.
FIRST_UPPER = 65
LAST_UPPER = 90

#: Erstes und letztes sichtbares ASCII-Zeichen -- Leerzeichen bis Tilde.
FIRST_VISIBLE = 32
LAST_VISIBLE = 126


class CryptographicSpaceship(Spaceship):
    """Ein Raumschiff mit Werkzeug zum Ver- und Entschluesseln."""

    __slots__ = ()

    def upper_case_alphabet(self) -> list[str]:
        """Liefert alle Grossbuchstaben von A bis Z."""
        return self._alphabet_between(FIRST_UPPER, LAST_UPPER)

    def alphabet(self) -> list[str]:
        """Liefert alle sichtbaren ASCII-Zeichen.

        Vom Leerzeichen bis zur Tilde -- also auch Ziffern, Kleinbuchstaben
        und Satzzeichen.
        """
        return self._alphabet_between(FIRST_VISIBLE, LAST_VISIBLE)

    def _alphabet_between(self, first: int, last: int) -> list[str]:
        """Baut ein Alphabet aus allen Zeichen zwischen zwei ASCII-Nummern."""
        zeichen: list[str] = []
        for nummer in range(first, last + 1):
            zeichen.append(chr(nummer))
        return zeichen

    def print_text(self, text: list[str]) -> None:
        """Gibt eine Zeichenliste als eine Zeile auf der Konsole aus."""
        print("".join(text))

    def contains(self, text: list[str], snippet: list[str]) -> bool:
        """Gibt an, ob der Textbaustein im Text vorkommt.

        Beispiel: `["H", "a", "l", "l", "o"]` enthaelt `["a", "l", "l"]`,
        aber nicht `["l", "a"]`.
        """
        return "".join(snippet) in "".join(text)
