"""Prueft die Kursbibliothek fuer CodeLab (`tools/build_codelab_library.py`).

Das Format gibt CodeLab vor: `codelab-bibliothek.yaml` und der Ordner `lib/`.
Der wichtigste Test spielt einen Testlauf in CodeLab nach -- Bibliothek
entpackt, daneben nur die Abgabe, kein `ships/` aus diesem Projekt.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from build_codelab_library import build, collect, manifest, release  # noqa: E402


def test_oben_liegen_nur_manifest_und_lib(tmp_path: Path) -> None:
    with zipfile.ZipFile(build(tmp_path / "bib.zip")) as archive:
        oben = {name.split("/")[0] for name in archive.namelist()}

    assert oben == {"codelab-bibliothek.yaml", "lib"}


def test_das_manifest_nennt_format_und_version() -> None:
    text = manifest("v9.8.7")

    assert "format: codelab-bibliothek\n" in text
    assert "version: 1\n" in text
    assert "release: v9.8.7\n" in text
    assert "language: python\n" in text
    assert '  SDL_VIDEODRIVER: "dummy"\n' in text


def test_die_version_ist_die_des_projekts() -> None:
    import tomllib

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as datei:
        version = tomllib.load(datei)["project"]["version"]
    assert release() == f"v{version}"


def test_ships_ist_nur_als_vorlage_dabei() -> None:
    """`ships` bilden die Tests aus der Abgabe nach -- hier stuende es im Weg."""
    ziele = [ziel for _, ziel in collect()]

    assert not any(z.startswith("lib/ships/") for z in ziele)
    assert "lib/ships_template/normal_spaceship.py" in ziele


def test_nichts_von_lehrkraft_oder_tests() -> None:
    ziele = [ziel for _, ziel in collect()]

    for ziel in ziele:
        assert not ziel.startswith(("lib/tests/", "lib/tools/")), ziel
        assert "__pycache__" not in ziel and not ziel.endswith(".pyc"), ziel


def test_lizenzen_reisen_mit() -> None:
    ziele = [ziel for _, ziel in collect()]

    assert "lib/LICENSE" in ziele
    assert "lib/pyfoot/LICENSE" in ziele


#: Ein Testlauf wie in CodeLab: `ships` aus Abgabe und Vorlage, Abgabe zuerst.
CODELAB_LAUF = textwrap.dedent(
    """
    import sys, types
    from pathlib import Path

    lib, src = Path(sys.argv[1]), Path(sys.argv[2])
    sys.path[:0] = [str(lib), str(src)]

    ships = types.ModuleType("ships")
    ships.__path__ = [str(src), str(lib / "ships_template")]

    def _klasse(name):
        import importlib, re
        modul = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return getattr(importlib.import_module(f"ships.{modul}"), name)

    ships.__getattr__ = _klasse
    sys.modules["ships"] = ships

    import levels
    from ships import ScoutShip

    welt = levels.Level1PowerUpRow()
    welt.add_object(ScoutShip(), *welt.START)
    welt._act_cycle()
    print("REST", len(welt.objects()) - 1)
    print("LEVEL0", type(levels.Level0().objects()[0]).__name__)
    """
)

SCOUT_SHIP = textwrap.dedent(
    """
    from space import SensorSpaceship

    class ScoutShip(SensorSpaceship):
        __slots__ = ()

        def init(self) -> None:
            while self.is_power_up_here():
                self.collect_power_up()
                if self.can_move():
                    self.move()
    """
)


def test_ein_testlauf_wie_in_codelab(tmp_path: Path) -> None:
    """Nur `scout_ship.py` abgegeben: `levels` laesst sich trotzdem laden."""
    with zipfile.ZipFile(build(tmp_path / "bib.zip")) as archive:
        archive.extractall(tmp_path / "bib")
    src = tmp_path / "src"
    src.mkdir()
    (src / "scout_ship.py").write_text(SCOUT_SHIP, encoding="utf-8")
    (tmp_path / "lauf.py").write_text(CODELAB_LAUF, encoding="utf-8")

    umgebung = {
        **os.environ,
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
        "PYGAME_HIDE_SUPPORT_PROMPT": "1",
        "PYTHONPATH": "",
    }
    ergebnis = subprocess.run(
        [sys.executable, "-I", str(tmp_path / "lauf.py"), str(tmp_path / "bib" / "lib"), str(src)],
        capture_output=True,
        text=True,
        env=umgebung,
        cwd=tmp_path,
        timeout=120,
    )

    assert ergebnis.returncode == 0, ergebnis.stderr
    assert "REST 0" in ergebnis.stdout
    assert "LEVEL0 NormalSpaceship" in ergebnis.stdout
