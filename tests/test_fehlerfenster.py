"""Fehler im Kurs: Fehlerfenster statt Absturz (Editor-Anforderungen H1 bis H8).

Die Bibliothek prueft das Verhalten allgemein. Hier geht es um die Fehler,
die im Kurs tatsaechlich vorkommen -- und um den Weg, auf dem Schueler:innen
danach weiterarbeiten:

    Fehler ansehen -> Zeile korrigieren -> speichern -> R -> Start

Die beiden letzten Tests laufen in einem eigenen Prozess mit einer Kopie
des Schuelerpakets. Nur so laesst sich eine Datei in `ships/` aendern, ohne
das Projekt selbst anzufassen.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Callable, Iterator

import pytest

from pyfoot import get_engine
from pyfoot.editor import codegen
from pyfoot.editor.errors import ErrorPanel
from pyfoot.engine import Engine
from space import PopupMessage, PowerUp, Spaceship, SpaceshipError, StartWorld
from space import Asteroid

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from build_student_package import build_folder  # noqa: E402


# ----------------------------------------------------------------------
# Level0 bindet sein Raumschiff oben ein
# ----------------------------------------------------------------------


def test_level0_importiert_das_raumschiff_bei_den_anderen_imports() -> None:
    """Wunsch des Auftraggebers: Imports stehen oben -- das sollen die
    Schueler:innen so lernen. Eine spaete Einfuhr mitten im Code faellt hier auf.
    """
    baum = ast.parse((PROJECT_ROOT / "levels" / "level0.py").read_text(encoding="utf-8"))

    oben = [
        node
        for node in baum.body
        if isinstance(node, ast.ImportFrom) and node.module == "ships"
    ]
    assert [alias.name for node in oben for alias in node.names] == ["NormalSpaceship"]

    for node in ast.walk(baum):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            eingebettet = [n for n in ast.walk(node) if isinstance(n, (ast.Import, ast.ImportFrom))]
            assert not eingebettet, f"Import innerhalb von {node.name}()"


def test_vscode_speichert_beim_wechsel_ins_fenster() -> None:
    """Ohne Speichern gibt es nichts neu einzulesen (H7)."""
    einstellungen = json.loads(
        (PROJECT_ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )
    assert einstellungen["files.autoSave"] == "onFocusChange"


# ----------------------------------------------------------------------
# Die Raumschiff-Fehler im laufenden Editor
# ----------------------------------------------------------------------


class Arena(StartWorld):
    """Kleine Welt: ein PowerUp-freies Startfeld, rechts ein Asteroid."""

    __slots__ = ()

    START = (0, 1)

    def __init__(self) -> None:
        super().__init__(4, 3)

    def prepare(self) -> None:
        self.add_object(Asteroid(), 2, 1)


class LeavesTheWorld(Spaceship):
    __slots__ = ()

    def init(self) -> None:
        self.turn_left()
        self.move(5)


class HitsTheAsteroid(Spaceship):
    __slots__ = ()

    def init(self) -> None:
        self.move()
        self.move()


class CollectsNothing(Spaceship):
    __slots__ = ()

    def init(self) -> None:
        self.collect_power_up()


class DropsWithoutPowerUps(Spaceship):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(0)

    def init(self) -> None:
        self.drop_power_up()


class TypoInName(Spaceship):
    __slots__ = ()

    def init(self) -> None:
        self.mvoe()  # type: ignore[attr-defined]


def run_in_editor(
    monkeypatch: pytest.MonkeyPatch, ship_class: type[Spaceship]
) -> tuple[Engine, Spaceship]:
    """Setzt das Raumschiff in die Arena und drueckt einmal Start.

    Die Ereignisschleife liefert statt echter Fensterereignisse genau einen
    Druck auf Start. Danach wird das Fenster geschlossen, sobald nichts mehr
    laeuft.
    """
    engine = get_engine()
    engine.enable_ui()
    engine.step_duration = 0.0
    world = Arena()
    ship = ship_class()
    world.add_object(ship, *Arena.START)
    engine.set_world(world)

    steps: Iterator[Callable[[Engine], None]] = iter([Engine.resume])

    def fake_pump(self: Engine) -> None:
        try:
            next(steps)(self)
        except StopIteration:
            if self._paused or not self._in_act_cycle:
                self._running = False

    monkeypatch.setattr(Engine, "_pump_events", fake_pump)
    engine.run()
    return engine, ship


def panel_of(engine: Engine) -> ErrorPanel:
    panel = engine.error_panel
    assert panel is not None, "Das Fehlerfenster haette offen sein muessen."
    return panel


@pytest.mark.parametrize(
    ("ship_class", "hinweis", "feld"),
    [
        (LeavesTheWorld, "Hilfe, ich verlasse die Welt!", (0, 0)),
        (HitsTheAsteroid, "Autsch, ein Asteroid!", (1, 1)),
        (CollectsNothing, "Hier ist kein PowerUp!", (0, 1)),
        (DropsWithoutPowerUps, "Keine PowerUps mehr an Bord!", (0, 1)),
    ],
)
def test_jeder_raumschiff_fehler_oeffnet_das_fehlerfenster(
    monkeypatch: pytest.MonkeyPatch,
    ship_class: type[Spaceship],
    hinweis: str,
    feld: tuple[int, int],
) -> None:
    """H2: alle vier Fehler gleich -- das Programm laeuft weiter."""
    engine, ship = run_in_editor(monkeypatch, ship_class)

    report = panel_of(engine).report
    assert report.name == SpaceshipError.__name__
    assert report.title == "Fehler mitten im Lauf"
    assert engine.is_paused()
    # Der Hinweis in der Welt bleibt wie bisher.
    assert engine.world.objects(PopupMessage), f"'{hinweis}' fehlt in der Welt."
    # Das Raumschiff steht auf dem letzten gueltigen Feld.
    assert (ship.x, ship.y) == feld


def test_python_fehler_im_raumschiff_mit_deutschem_hinweis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, _ = run_in_editor(monkeypatch, TypoInName)

    report = panel_of(engine).report
    assert report.name == "AttributeError"
    assert "noch nicht geschrieben" in report.hint


def test_gezeigt_wird_die_zeile_im_eigenen_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """H3: nicht `spaceship.py`, wo der Fehler ausgeloest wird.

    Die Schuelerklassen liegen in `ships/`. Hier stehen sie in dieser
    Testdatei -- deshalb wird fuer den Test dieser Ordner angemeldet.
    """
    monkeypatch.setattr(codegen, "_actor_folder", Path(__file__).resolve().parent)
    engine, _ = run_in_editor(monkeypatch, HitsTheAsteroid)

    report = panel_of(engine).report
    assert report.file == Path(__file__).resolve()
    assert report.code == "self.move()"


def test_ohne_anmeldung_stuende_dort_die_bibliothek(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Gegenprobe zu H3: Ohne angemeldeten Ordner fuehrt die Spur in `space/`."""
    monkeypatch.setattr(codegen, "_actor_folder", PROJECT_ROOT / "ships")
    monkeypatch.setattr(codegen, "_world_folder", PROJECT_ROOT / "levels")
    engine, _ = run_in_editor(monkeypatch, HitsTheAsteroid)

    report = panel_of(engine).report
    assert report.file is not None
    assert report.file.name == "spaceship.py"


def test_powerup_ausserhalb_der_welt_wird_gemeldet() -> None:
    """H8: Vorher stand es still und unsichtbar neben der Welt."""
    welt = Arena()
    with pytest.raises(ValueError, match="ausserhalb der Welt"):
        welt.add_object(PowerUp(), 4, 0)


# ----------------------------------------------------------------------
# Der ganze Weg in einer Kopie des Schuelerpakets
# ----------------------------------------------------------------------


@pytest.fixture
def paket(tmp_path: Path) -> Path:
    """Ein frisch gebautes Schuelerpaket in einem Testordner."""
    return build_folder(tmp_path / "Space").target


def run_script(folder: Path, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Fuehrt ein Programm im Paketordner aus -- ohne sichtbares Fenster."""
    umgebung = dict(os.environ)
    umgebung.update(
        SDL_VIDEODRIVER="dummy",
        SDL_AUDIODRIVER="dummy",
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
    )
    umgebung.pop("PYFOOT_UI", None)
    return subprocess.run(
        [sys.executable, script, *arguments],
        cwd=folder,
        env=umgebung,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


WEITERARBEITEN = textwrap.dedent(
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path.cwd()))

    from pyfoot import enable_ui, get_engine, set_world
    from levels import Level0

    enable_ui()
    set_world(Level0())
    engine = get_engine()

    def schiff():
        return [a for a in engine.world.objects() if type(a).__name__ == "NormalSpaceship"][0]

    datei = Path("ships/normal_spaceship.py")
    original = datei.read_text(encoding="utf-8")

    # 1. Die Schuelerin aendert ihre Datei -- das Schiff soll 20 Felder fliegen.
    alt = schiff()
    datei.write_text(original.replace("self.move()", "self.move(20)", 1), encoding="utf-8")
    engine._perform_reset()
    neu = schiff()
    print("NEUE_KLASSE", type(neu) is not type(alt))
    print("NEUER_CODE", 20 in type(neu).init.__code__.co_consts)
    print("STATUS", engine.status)

    # 2. Ein Tippfehler macht die Datei unlesbar.
    welt = engine.world
    datei.write_text(original.replace("def init(self)", "def init(self", 1), encoding="utf-8")
    engine._perform_reset()
    panel = engine.error_panel
    print("FEHLER", panel.report.name if panel else None)
    print("STELLE", panel.report.location() if panel else None)
    print("WELT_BLEIBT", engine.world is welt)

    # 3. Repariert -- es geht weiter.
    datei.write_text(original, encoding="utf-8")
    engine._perform_reset()
    print("REPARIERT", engine.error_panel is None)
    """
)


def test_datei_aendern_und_zuruecksetzen(paket: Path) -> None:
    """H7 mit dem echten Projekt: `levels` bindet `ships` oben ein."""
    (paket / "probe_weiterarbeiten.py").write_text(WEITERARBEITEN, encoding="utf-8")

    ergebnis = run_script(paket, "probe_weiterarbeiten.py")
    zeilen = dict(
        line.split(" ", 1) for line in ergebnis.stdout.splitlines() if " " in line
    )

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert zeilen["NEUE_KLASSE"] == "True"
    assert zeilen["NEUER_CODE"] == "True"
    assert zeilen["STATUS"].startswith("Neu eingebunden: normal_spaceship.py")
    assert zeilen["FEHLER"] == "SyntaxError"
    assert zeilen["STELLE"].startswith("ships/normal_spaceship.py, Zeile")
    assert zeilen["WELT_BLEIBT"] == "True"
    assert zeilen["REPARIERT"] == "True"


def test_fehler_beim_start_mit_zusammenfassung(paket: Path) -> None:
    """H6: Vor dem Fenster gibt es nur die Konsole -- dort steht, wo es klemmt."""
    datei = paket / "ships" / "normal_spaceship.py"
    text = datei.read_text(encoding="utf-8")
    datei.write_text(text.replace("def init(self)", "def init(self", 1), encoding="utf-8")

    ergebnis = run_script(paket, "main_editor.py")

    assert ergebnis.returncode != 0
    ausgabe = ergebnis.stderr
    assert "Traceback" in ausgabe
    assert "Fehler vor dem Start: SyntaxError" in ausgabe
    assert "Stelle: ships/normal_spaceship.py:" in ausgabe
