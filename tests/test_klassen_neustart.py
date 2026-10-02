"""Angelegte und geloeschte Klassen ueberstehen einen Neustart (Anforderung B4f).

Befund vom 12.09.2026, nachgemessen an einer Kopie des Schuelerpakets:

- Ein in der Oberflaeche angelegtes Raumschiff stand sofort im Klassenbaum,
  fehlte aber nach dem Neustart: `ships/__init__.py` band es nicht ein.
- Nach dem Loeschen von `Level7Grid` **startete der Editor nicht mehr**:
  `levels/__init__.py` band die umbenannte Datei weiter ein.

Jeder Test arbeitet in einer frischen Paketkopie; ein "Neustart" ist ein
eigener Prozess, der die Klassen so einliest wie `main_editor.py`.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from build_student_package import build_folder  # noqa: E402


@pytest.fixture
def paket(tmp_path: Path) -> Path:
    return build_folder(tmp_path / "Space").target


def starten(paket: Path, programm: str) -> subprocess.CompletedProcess[str]:
    """Startet einen eigenen Prozess im Paketordner -- ohne Fenster."""
    (paket / "probe.py").write_text(
        "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path.cwd()))\n"
        + textwrap.dedent(programm),
        encoding="utf-8",
    )
    umgebung = dict(os.environ)
    umgebung.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONIOENCODING="utf-8")
    umgebung.pop("PYFOOT_UI", None)
    return subprocess.run(
        [sys.executable, "probe.py"],
        cwd=paket,
        env=umgebung,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


NEUSTART = """
from pyfoot import enable_ui, set_world
from pyfoot.editor.sidebar import class_tree
from levels import Level0

enable_ui()
set_world(Level0())
print("KLASSEN", " ".join(sorted(row.cls.__name__ for row in class_tree())))
"""


def klassen_nach_neustart(paket: Path) -> list[str]:
    ergebnis = starten(paket, NEUSTART)
    assert ergebnis.returncode == 0, ergebnis.stderr
    zeile = [z for z in ergebnis.stdout.splitlines() if z.startswith("KLASSEN ")][0]
    return zeile.split()[1:]


def test_angelegte_klassen_ueberstehen_den_neustart(paket: Path) -> None:
    ergebnis = starten(
        paket,
        """
        from pyfoot import enable_ui, get_engine, set_world
        from levels import Level0
        from space import Spaceship, StartWorld

        enable_ui()
        set_world(Level0())
        engine = get_engine()
        engine.create_subclass(Spaceship, "ProbeShip")
        print("STATUS", engine.status)
        engine.create_subclass(StartWorld, "ProbeLevel")
        """,
    )
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "in ships/__init__.py eingetragen" in ergebnis.stdout

    klassen = klassen_nach_neustart(paket)

    assert "ProbeShip" in klassen
    assert "ProbeLevel" in klassen


def test_unterklasse_eines_eigenen_raumschiffs_ueberlebt_den_neustart(paket: Path) -> None:
    """Befund vom 18.09.2026: `AlphaShip(NormalSpaceship)` legte den Start lahm.

    Die neue Datei schreibt `from ships import NormalSpaceship`. Stand ihre
    Einfuhr in `ships/__init__.py` alphabetisch **vor** der von
    `normal_spaceship`, gab es diesen Namen dort noch nicht:
    `ImportError: cannot import name 'NormalSpaceship' from partially
    initialized module 'ships'`.
    """
    ergebnis = starten(
        paket,
        """
        from pyfoot import enable_ui, get_engine, set_world
        from levels import Level0
        from ships import NormalSpaceship

        enable_ui()
        set_world(Level0())
        get_engine().create_subclass(NormalSpaceship, "AlphaShip")
        """,
    )
    assert ergebnis.returncode == 0, ergebnis.stderr

    text = (paket / "ships" / "__init__.py").read_text(encoding="utf-8")
    assert text.index("from .normal_spaceship import") < text.index("from .alpha_ship import")
    assert text.index('"NormalSpaceship"') < text.index('"AlphaShip"')
    assert "AlphaShip" in klassen_nach_neustart(paket)


def test_nach_dem_loeschen_startet_der_editor_weiter(paket: Path) -> None:
    ergebnis = starten(
        paket,
        """
        from pyfoot import enable_ui, get_engine, set_world
        from levels import Level0, Level7Grid

        enable_ui()
        set_world(Level0())
        engine = get_engine()
        engine.delete_class(Level7Grid)
        engine.delete_class(Level7Grid)
        print("STATUS", engine.status)
        """,
    )
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "Level7Grid entfernt" in ergebnis.stdout

    klassen = klassen_nach_neustart(paket)

    assert "Level7Grid" not in klassen
    assert "Level6ForLoop" in klassen


def test_die_paketdateien_bestehen_die_typpruefung(paket: Path) -> None:
    """Die Eintraege muessen so aussehen, wie sie von Hand geschrieben wuerden."""
    ergebnis = starten(
        paket,
        """
        from pyfoot import enable_ui, get_engine, set_world
        from levels import Level0
        from space import Spaceship

        enable_ui()
        set_world(Level0())
        get_engine().create_subclass(Spaceship, "ProbeShip")
        """,
    )
    assert ergebnis.returncode == 0, ergebnis.stderr

    pruefung = subprocess.run(
        # Geprueft werden nur die Schuelerordner; die Bibliothek hat ihre
        # eigene, projektbezogene Pruefung (`check_project.py`).
        [sys.executable, "-m", "mypy", "--strict", "--follow-imports=silent", "ships", "levels"],
        cwd=paket,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert pruefung.returncode == 0, pruefung.stdout
    text = (paket / "ships" / "__init__.py").read_text(encoding="utf-8")
    assert "from .probe_ship import ProbeShip\n" in text
    assert '    "ProbeShip",\n' in text
