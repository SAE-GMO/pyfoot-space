"""Startet die Basiswelt mit eingeschalteter Oberflaeche.

Gedacht zum Ausprobieren und zum Vorfuehren im Unterricht: Dieselbe Welt wie
in den ersten Aufgaben -- `Level0` --, aber mit Bedienleiste und
Klassenanzeige. Damit laesst sich das Programm anhalten, Anweisung fuer
Anweisung mitverfolgen und die Welt mit der Maus umbauen.

Starten mit:
    python main_editor.py

Der Play-Knopf in VS Code tut dasselbe. Eine Umgebungsvariable ist nicht
noetig -- diese Datei schaltet die Oberflaeche selbst ein.

Bedienung
---------
    Leertaste   Start und Pause -- auch mitten in einer Anweisungsfolge
    D           Durchlauf: startet die Anweisungsfolge
    S           Schritt: genau eine Anweisung weiter
    R           zuruecksetzen
    + / -       Tempo
    B           Bearbeiten: Objekte mit der Maus setzen und verschieben
    W           Welt sichern: den Aufbau als Quelltext schreiben
    Esc         beenden

Rechts steht der Klassenbaum. Ein Rechtsklick -- auf eine Klasse dort oder
auf ein Raumschiff in der Welt -- oeffnet das zugehoerige Menue.

Wenn etwas schiefgeht
---------------------
Fliegt ein Raumschiff aus der Welt oder steckt ein Fehler im Code, haelt das
Programm an und zeigt ein Fehlerfenster -- das Fenster bleibt offen.

    E           springt in VS Code an die fehlerhafte Zeile
    R           setzt zurueck; geaenderte Dateien werden dabei neu eingelesen
    Esc         schliesst nur das Fehlerfenster

Also: Fehler ansehen, Zeile korrigieren, zurueck ins Fenster, R, Start.

Welches Raumschiff in der Welt steht, entscheidet `ships/normal_spaceship.py`
-- diese Datei gehoert dir. Fuer eine andere Welt hier `Level0` austauschen.
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

from pyfoot import enable_ui, get_engine, run, set_world  # noqa: E402
from levels import Level0  # noqa: E402


def main() -> None:
    """Baut die Basiswelt auf und startet die Oberflaeche."""
    # Vor set_world einschalten, damit das Fenster gleich Platz fuer
    # Bedienleiste und Klassenanzeige bekommt.
    enable_ui()

    set_world(Level0())

    engine = get_engine()
    engine.step_duration = 0.4
    run()


if __name__ == "__main__":
    main()
