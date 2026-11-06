"""Zeichnet das Startfeld einer Welt in ihren Hintergrund.

Wer sein Raumschiff aus dem Klassenbaum in eine Welt zieht, soll sehen,
wohin: Das Feld `START` bekommt einen Rahmen und einen Pfeil in die
Blickrichtung, mit der ein neues Raumschiff startet (nach rechts). Dasselbe
Feld benutzen die Tests -- Arbeitsblatt, Welt und Abgabe meinen also
denselben Start.

Die Markierung gehoert zum Hintergrund und ist kein Objekt der Welt. So
zaehlt sie bei `objects()` nicht mit, laesst sich nicht verschieben und
stoert keine Aufgabe. Das Bild `start_marker.png` entsteht mit den uebrigen
Bildern in `space/assets/generate_assets.py`.
"""

from __future__ import annotations

from pyfoot import Image

__all__ = ["start_background"]


def start_background(
    width: int, height: int, cell_size: int, start: tuple[int, int]
) -> Image:
    """Baut den Sternenhimmel einer Welt mit markiertem Startfeld.

    Args:
        width: Anzahl der Spalten.
        height: Anzahl der Zeilen.
        cell_size: Kantenlaenge eines Feldes in Bildpunkten.
        start: Das Startfeld `(x, y)`. Liegt es ausserhalb der Welt, bleibt
            der Himmel ohne Markierung.

    Returns:
        Ein Bild in der Groesse der ganzen Welt.
    """
    pixel_width, pixel_height = width * cell_size, height * cell_size
    background = Image.blank(pixel_width, pixel_height)

    # Den Sternenhimmel kacheln, wie es die Welt sonst selbst taete.
    stars = Image.from_file("starfield.png")
    for x in range(0, pixel_width, stars.width):
        for y in range(0, pixel_height, stars.height):
            background.draw_image(stars, x, y)

    column, row = start
    if 0 <= column < width and 0 <= row < height:
        marker = Image.from_file("start_marker.png")
        if marker.width != cell_size:
            marker = marker.scaled(cell_size, cell_size)
        background.draw_image(marker, column * cell_size, row * cell_size)
    return background
