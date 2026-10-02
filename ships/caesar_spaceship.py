"""Das Raumschiff fuer die Caesar-Chiffre.

Diese Datei gehoert dir. Zwei Methoden sind noch leer -- sie zu schreiben ist
die Aufgabe (siehe `AB10`).

Ein Text ist hier eine **Liste von Zeichen**: `list("HALLO")`. Zurueck geht es
mit `"".join(zeichen)`.
"""

from __future__ import annotations

from space import CryptographicSpaceship

__all__ = ["CaesarSpaceship"]


class CaesarSpaceship(CryptographicSpaceship):
    """Verschluesselt und entschluesselt mit der Caesar-Chiffre."""

    # Eigene Attribute hier eintragen: `__slots__ = ("counter",)`, den
    # Typ bei Bedarf darunter als `counter: int`.
    __slots__ = ()

    def init(self) -> None:
        """Hier kannst du alle Anweisungen eintragen, die das Schiff ausfuehren soll."""
        cryptic = list("SALVEASTERIX")
        alphabet = self.upper_case_alphabet()
        secret = 3

        self.print_text(cryptic)
        result = self.apply_chiffre(cryptic, alphabet, secret)
        self.print_text(result)

    def apply_chiffre(
        self, text: list[str], alphabet: list[str], secret: int
    ) -> list[str]:
        """Wendet die Caesar-Chiffre auf den Text an.

        Args:
            text: Der zu ver- oder entschluesselnde Text.
            alphabet: Alle erlaubten Zeichen, in ihrer Reihenfolge.
            secret: Um wie viele Stellen verschoben wird.

        Returns:
            Der verschobene Text.
        """
        return text

    def get_ordinal_number(self, alphabet: list[str], character: str) -> int:
        """Sucht das Zeichen im Alphabet und liefert seine Stelle.

        Args:
            alphabet: Alle erlaubten Zeichen.
            character: Das gesuchte Zeichen.

        Returns:
            Die Stelle des Zeichens im Alphabet.
        """
        return -1
