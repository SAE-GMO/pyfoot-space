"""Erzeugt die Grafiken des Basisprojekts.

Alle Bilder entstehen hier aus geometrischen Grundformen. Es werden keine
fremden Vorlagen verwendet, damit das Projekt ohne Lizenzfragen
veroeffentlicht werden kann (Anforderungsdokument 4.9).

Aufruf:
    python space/assets/generate_assets.py
"""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

CELL_SIZE = 60
ACTOR_SIZE = 48
#: Die Hintergrundkachel ist ein Vielfaches der Feldgroesse, damit sich das
#: Sternmuster nicht in jedem Feld wiederholt.
STARFIELD_SIZE = CELL_SIZE * 4

IMAGE_DIR = Path(__file__).resolve().parent / "images"

Rgba = tuple[int, int, int, int]


def _new_surface(width: int, height: int) -> pygame.Surface:
    """Erzeugt eine durchsichtige Zeichenflaeche."""
    return pygame.Surface((width, height), pygame.SRCALPHA)


def make_spaceship(size: int = ACTOR_SIZE) -> pygame.Surface:
    """Zeichnet ein Raumschiff, das nach rechts zeigt.

    Nach rechts, weil das der Blickrichtung 0 Grad entspricht. PyFoot dreht
    das Bild beim Zeichnen passend zur aktuellen Blickrichtung.
    """
    surface = _new_surface(size, size)
    center = size / 2

    hull: Rgba = (222, 230, 245, 255)
    shade: Rgba = (150, 165, 195, 255)
    canopy: Rgba = (90, 190, 245, 255)
    flame: Rgba = (255, 170, 60, 255)

    # Triebwerksflamme hinten links
    pygame.draw.polygon(
        surface,
        flame,
        [
            (size * 0.06, center),
            (size * 0.24, center - size * 0.11),
            (size * 0.24, center + size * 0.11),
        ],
    )

    # Rumpf: eine nach rechts gerichtete Pfeilform
    body = [
        (size * 0.94, center),
        (size * 0.34, center - size * 0.30),
        (size * 0.22, center - size * 0.10),
        (size * 0.22, center + size * 0.10),
        (size * 0.34, center + size * 0.30),
    ]
    pygame.draw.polygon(surface, hull, body)
    pygame.draw.polygon(surface, shade, body, width=2)

    # Untere Haelfte leicht abdunkeln, damit das Schiff plastisch wirkt
    pygame.draw.polygon(
        surface,
        shade,
        [
            (size * 0.94, center),
            (size * 0.34, center + size * 0.30),
            (size * 0.22, center + size * 0.10),
            (size * 0.22, center),
        ],
    )

    # Cockpit
    pygame.draw.circle(surface, canopy, (int(size * 0.60), int(center)), int(size * 0.11))
    pygame.draw.circle(
        surface, shade, (int(size * 0.60), int(center)), int(size * 0.11), width=2
    )

    return surface


def make_power_up(size: int = ACTOR_SIZE) -> pygame.Surface:
    """Zeichnet ein PowerUp als leuchtenden Kristall."""
    surface = _new_surface(size, size)
    center = size / 2

    glow: Rgba = (90, 240, 200, 60)
    highlight: Rgba = (170, 255, 230, 255)
    core: Rgba = (40, 210, 170, 255)
    edge: Rgba = (20, 130, 110, 255)

    pygame.draw.circle(surface, glow, (int(center), int(center)), int(size * 0.44))

    diamond = [
        (center, size * 0.12),
        (size * 0.84, center),
        (center, size * 0.88),
        (size * 0.16, center),
    ]
    pygame.draw.polygon(surface, core, diamond)

    # Lichtkante auf der oberen Haelfte
    pygame.draw.polygon(
        surface,
        highlight,
        [
            (center, size * 0.12),
            (size * 0.84, center),
            (center, center),
            (size * 0.16, center),
        ],
    )
    pygame.draw.polygon(surface, edge, diamond, width=2)

    return surface


def make_asteroid(size: int = ACTOR_SIZE, seed: int = 7) -> pygame.Surface:
    """Zeichnet einen Asteroiden als unregelmaessiges Vieleck."""
    surface = _new_surface(size, size)
    center = size / 2
    rng = random.Random(seed)

    rock: Rgba = (128, 122, 118, 255)
    light: Rgba = (163, 157, 152, 255)
    dark: Rgba = (84, 79, 76, 255)

    corners = 11
    outline: list[tuple[float, float]] = []
    for i in range(corners):
        angle = 2 * math.pi * i / corners
        radius = size * rng.uniform(0.33, 0.46)
        outline.append(
            (center + radius * math.cos(angle), center + radius * math.sin(angle))
        )

    pygame.draw.polygon(surface, rock, outline)
    pygame.draw.polygon(surface, dark, outline, width=2)

    # Ein paar Krater
    for _ in range(4):
        crater_x = int(center + rng.uniform(-0.22, 0.22) * size)
        crater_y = int(center + rng.uniform(-0.22, 0.22) * size)
        crater_radius = int(rng.uniform(0.04, 0.08) * size)
        pygame.draw.circle(surface, dark, (crater_x, crater_y), crater_radius)
        pygame.draw.circle(
            surface, light, (crater_x - 1, crater_y - 1), crater_radius, width=1
        )

    return surface


def make_starfield(size: int = STARFIELD_SIZE, seed: int = 3) -> pygame.Surface:
    """Zeichnet eine kachelbare Sternenfeld-Flaeche.

    Der Hintergrund ist bewusst einfarbig: Ein Farbverlauf wuerde an jeder
    Kachelgrenze zurueckspringen und eine sichtbare Naht erzeugen. Die Kachel
    ist deutlich groesser als ein Feld, damit sich das Sternmuster nicht von
    Feld zu Feld wiederholt. Sterne halten Abstand zum Rand, damit an den
    Kachelgrenzen keine halbierten Punkte entstehen.
    """
    surface = pygame.Surface((size, size))
    rng = random.Random(seed)

    surface.fill((14, 16, 30))

    margin = 3
    count = max(8, (size * size) // 900)
    for _ in range(count):
        x = rng.randint(margin, size - margin - 1)
        y = rng.randint(margin, size - margin - 1)
        brightness = rng.randint(110, 255)
        radius = 1 if brightness < 215 else 2
        color = (brightness, brightness, min(255, brightness + 20))
        pygame.draw.circle(surface, color, (x, y), radius)

    return surface


def generate_all(target_dir: Path | None = None) -> dict[str, Path]:
    """Erzeugt alle Grafiken und speichert sie als PNG.

    Args:
        target_dir: Zielordner; ohne Angabe der Ordner `images` neben dieser Datei.

    Returns:
        Zuordnung von Dateiname zu geschriebenem Pfad.
    """
    if not pygame.get_init():
        pygame.init()

    directory = target_dir if target_dir is not None else IMAGE_DIR
    directory.mkdir(parents=True, exist_ok=True)

    images: dict[str, pygame.Surface] = {
        "spaceship.png": make_spaceship(),
        "power_up.png": make_power_up(),
        "asteroid.png": make_asteroid(),
        "starfield.png": make_starfield(),
    }

    written: dict[str, Path] = {}
    for name, surface in images.items():
        path = directory / name
        pygame.image.save(surface, str(path))
        written[name] = path

    return written


def main() -> None:
    """Erzeugt die Grafiken und meldet, was geschrieben wurde."""
    for name, path in generate_all().items():
        print(f"{name:>16}  ->  {path}")


if __name__ == "__main__":
    main()
