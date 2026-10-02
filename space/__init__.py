"""Das Basisprojekt: Raumschiffe, PowerUps und Asteroiden.

Dieses Paket setzt auf PyFoot auf und stellt die Klassen bereit, mit denen
im Kurs gearbeitet wird. Es greift ausschliesslich auf die Schnittstelle von
PyFoot zu, niemals direkt auf pygame.
"""

from __future__ import annotations

from pathlib import Path

from pyfoot import add_image_folder, set_class_folders

# Die Grafiken des Basisprojekts bekannt machen, damit sie ueber ihren
# Dateinamen geladen werden koennen.
add_image_folder(Path(__file__).resolve().parent / "assets" / "images")

# Wohin die Oberflaeche selbst geschriebene Klassen legt. Getrennt vom
# Kursinhalt, damit sich beides nicht vermischt und nur dort geloescht
# werden darf (Editor-Anforderungsdokument B4b).
_ROOT = Path(__file__).resolve().parent.parent
set_class_folders(actors=_ROOT / "ships", worlds=_ROOT / "levels")

from .actors.asteroid import Asteroid, RandomAsteroid  # noqa: E402
from .actors.popup_message import PopupMessage, show_alert  # noqa: E402
from .actors.power_up import PowerUp, RandomPowerUp  # noqa: E402
from .actors.cryptographic_spaceship import CryptographicSpaceship  # noqa: E402
from .actors.sensor_spaceship import SensorSpaceship  # noqa: E402
from .actors.spaceship import Spaceship, SpaceshipError  # noqa: E402
from .worlds.space_world import SpaceWorld  # noqa: E402
from .worlds.start_world import StartWorld  # noqa: E402

__all__ = [
    "Spaceship",
    "SensorSpaceship",
    "CryptographicSpaceship",
    "SpaceshipError",
    "PowerUp",
    "RandomPowerUp",
    "Asteroid",
    "RandomAsteroid",
    "PopupMessage",
    "show_alert",
    "SpaceWorld",
    "StartWorld",
]
