"""Beispiel fuer das Basisprojekt -- ohne Oberflaeche.

Entspricht dem Einstiegsbeispiel des Kurses: Ein Raumschiff arbeitet eine
kurze Anweisungsfolge ab. Welche, steht in `ships/normal_spaceship.py`.

Fuer den Unterricht ist `main_editor.py` gedacht -- dort gibt es Bedienleiste
und Klassenanzeige. Diese Datei zeigt nur, wie schmal der Rahmen ohne sie ist.

Starten mit:
    python main_space.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Der Projektordner muss im Suchpfad stehen, sonst findet Python `space` und
# `ships` nicht. Normalerweise legt Python ihn selbst dorthin -- aber nicht
# in jedem Starter: `python -P`, manche Debugger und eingebettete Aufrufe
# lassen ihn weg, und die Fehlermeldung nennt dann nur das fehlende Modul.
_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pyfoot import get_engine, run, set_world  # noqa: E402
from levels import Level0  # noqa: E402


def main() -> None:
    """Baut die Startwelt auf und startet die Simulation."""
    set_world(Level0())
    get_engine().step_duration = 0.4
    run()


if __name__ == "__main__":
    main()
