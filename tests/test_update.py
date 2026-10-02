"""Prueft das Auffrischen eines Schuelerprojekts.

Der Anlass: Wer eine neue Version bekommt, darf dabei nicht seine Arbeit
verlieren. `tools/update_space.py` entscheidet das anhand des Manifests, das
jedes Paket mitbringt -- hier wird nachgesehen, ob es richtig entscheidet.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from update_space import (  # noqa: E402
    Change,
    apply,
    backup,
    data_hash,
    find_package,
    manifest_of,
    merge_init,
    package_files,
    plan,
)

INIT = '''"""Eigene Raumschiffe."""

from __future__ import annotations

from .normal_spaceship import NormalSpaceship
from .sensor_spaceship import SensorSpaceship

__all__ = [
    "NormalSpaceship",
    "SensorSpaceship",
]
'''


@pytest.fixture
def projekt(tmp_path: Path) -> Path:
    """Legt ein kleines Projekt mit zwei Dateien an."""
    (tmp_path / "ships").mkdir()
    (tmp_path / "ships" / "normal_spaceship.py").write_text("alt\n", encoding="utf-8")
    (tmp_path / "main_space.py").write_text("start\n", encoding="utf-8")
    return tmp_path


# ----------------------------------------------------------------------
# Pruefsummen
# ----------------------------------------------------------------------


def test_zeilenenden_machen_aus_einer_datei_keine_andere() -> None:
    """Ein Editor, der `\\n` zu `\\r\\n` macht, darf keine Meldung ausloesen."""
    assert data_hash(b"a\r\nb\r\n", ".py") == data_hash(b"a\nb\n", ".py")


def test_bei_bilddateien_zaehlt_jedes_byte() -> None:
    """Dort waere das Ersetzen von Zeichen eine Beschaedigung."""
    assert data_hash(b"a\r\nb", ".png") != data_hash(b"a\nb", ".png")


# ----------------------------------------------------------------------
# Das Paket lesen
# ----------------------------------------------------------------------


def test_der_oberste_ordner_des_archivs_faellt_weg(tmp_path: Path) -> None:
    ziel = tmp_path / "Space.zip"
    with zipfile.ZipFile(ziel, "w") as archive:
        archive.writestr("Space/main_space.py", "start\n")
        archive.writestr("Space/ships/normal_spaceship.py", "neu\n")

    assert sorted(package_files(ziel)) == ["main_space.py", "ships/normal_spaceship.py"]


def test_ein_leeres_paket_wird_gemeldet(tmp_path: Path) -> None:
    ziel = tmp_path / "leer.zip"
    with zipfile.ZipFile(ziel, "w"):
        pass

    with pytest.raises(ValueError):
        package_files(ziel)


def test_die_neueste_zip_wird_gefunden(tmp_path: Path) -> None:
    alt = tmp_path / "Space.zip"
    neu = tmp_path / "Space_neu.zip"
    alt.write_bytes(b"1")
    neu.write_bytes(b"2")
    import os

    os.utime(neu, (alt.stat().st_mtime + 60, alt.stat().st_mtime + 60))

    assert find_package([tmp_path]) == neu


# ----------------------------------------------------------------------
# Was mit welcher Datei geschieht
# ----------------------------------------------------------------------


def test_eine_unberuehrte_datei_wird_aufgefrischt(projekt: Path) -> None:
    bekannt = {"ships/normal_spaceship.py": data_hash(b"alt\n", ".py")}

    changes = plan(projekt, {"ships/normal_spaceship.py": b"neu\n"}, bekannt)

    assert changes == [Change("ships/normal_spaceship.py", "aktualisiert")]


def test_eine_selbst_geaenderte_datei_bleibt(projekt: Path) -> None:
    """Der Kern der Sache: Hier steckt die Arbeit der Schuelerin."""
    bekannt = {"ships/normal_spaceship.py": data_hash(b"ausgeliefert\n", ".py")}

    changes = plan(projekt, {"ships/normal_spaceship.py": b"neu\n"}, bekannt)

    assert changes == [Change("ships/normal_spaceship.py", "eigene")]


def test_ohne_manifest_bleibt_der_eigene_ordner_unberuehrt(projekt: Path) -> None:
    """Beim ersten Auffrischen eines alten Projekts gibt es keine Pruefsummen."""
    changes = plan(projekt, {"ships/normal_spaceship.py": b"neu\n"}, {})

    assert changes == [Change("ships/normal_spaceship.py", "eigene")]


def test_ohne_manifest_wird_mitgeliefertes_erneuert(projekt: Path) -> None:
    """`main_space.py` und `pyfoot\\` schreibt niemand um -- sonst blieben sie
    fuer immer auf dem alten Stand.
    """
    changes = plan(projekt, {"main_space.py": b"neu\n"}, {})

    assert changes == [Change("main_space.py", "aktualisiert")]


def test_eine_fehlende_datei_kommt_dazu(projekt: Path) -> None:
    changes = plan(projekt, {"ships/delta_spaceship.py": b"neu\n"}, {})

    assert changes == [Change("ships/delta_spaceship.py", "neu")]


def test_eine_gleiche_datei_bleibt_unangetastet(projekt: Path) -> None:
    changes = plan(projekt, {"main_space.py": b"start\n"}, {})

    assert changes == [Change("main_space.py", "gleich")]


def test_eine_entfallene_datei_wird_nur_gemeldet(projekt: Path) -> None:
    """Geloescht wird nichts -- vielleicht steht dort eigene Arbeit."""
    bekannt = {"main_space.py": data_hash(b"start\n", ".py")}

    changes = plan(projekt, {"ships/delta_spaceship.py": b"x\n"}, bekannt)

    assert Change("main_space.py", "entfallen") in changes


def test_die_eigene_datei_wird_nicht_ueberschrieben(projekt: Path) -> None:
    changes = [Change("ships/normal_spaceship.py", "eigene")]

    hinweise = apply(projekt, {"ships/normal_spaceship.py": b"neu\n"}, changes)

    assert (projekt / "ships" / "normal_spaceship.py").read_text(encoding="utf-8") == "alt\n"
    assert (projekt / "ships" / "normal_spaceship.py.neu").read_bytes() == b"neu\n"
    assert hinweise and "normal_spaceship.py.neu" in hinweise[0]


def test_die_neue_version_traegt_keine_endung_py(projekt: Path) -> None:
    """Sonst stuende sie im Klassenbaum und mypy pruefte sie mit."""
    apply(projekt, {"ships/normal_spaceship.py": b"neu\n"}, [Change("ships/normal_spaceship.py", "eigene")])

    assert not list((projekt / "ships").glob("*.neu.py"))


# ----------------------------------------------------------------------
# Paketdateien zusammenfuehren
# ----------------------------------------------------------------------


def test_eigene_klassen_ueberstehen_das_zusammenfuehren() -> None:
    eigen = INIT.replace(
        "from .sensor_spaceship import SensorSpaceship",
        "from .sensor_spaceship import SensorSpaceship\nfrom .alpha_ship import AlphaShip",
    ).replace('    "SensorSpaceship",\n]', '    "SensorSpaceship",\n    "AlphaShip",\n]')
    neu = INIT.replace(
        "from .sensor_spaceship import SensorSpaceship",
        "from .sensor_spaceship import SensorSpaceship\nfrom .delta_spaceship import DeltaSpaceship",
    ).replace('    "SensorSpaceship",\n]', '    "SensorSpaceship",\n    "DeltaSpaceship",\n]')

    zusammen = merge_init(neu, eigen)

    assert zusammen is not None
    assert "from .alpha_ship import AlphaShip" in zusammen
    assert "from .delta_spaceship import DeltaSpaceship" in zusammen
    assert '    "AlphaShip",' in zusammen


def test_die_eigene_klasse_steht_hinter_der_grundklasse() -> None:
    """Sonst bricht der Start ab: `partially initialized module`."""
    eigen = INIT.replace(
        "__all__", "from .alpha_ship import AlphaShip\n\n__all__"
    ).replace('    "SensorSpaceship",\n]', '    "SensorSpaceship",\n    "AlphaShip",\n]')

    zusammen = merge_init(INIT, eigen)

    assert zusammen is not None
    zeilen = zusammen.splitlines()
    assert zeilen.index("from .normal_spaceship import NormalSpaceship") < zeilen.index(
        "from .alpha_ship import AlphaShip"
    )


def test_ohne_eigene_klassen_bleibt_die_neue_datei_wie_sie_ist() -> None:
    assert merge_init(INIT, INIT) == INIT


def test_eine_unbekannte_paketdatei_wird_nicht_angeruehrt() -> None:
    """Wer dort von Hand aufgeraeumt hat, soll es so wiederfinden."""
    assert merge_init("# nichts drin\n", INIT) is None


def test_zeilenenden_verdoppeln_sich_nicht() -> None:
    """Auf Windows machte ein unachtsames Schreiben aus `\\r\\n` ein `\\r\\r\\n`."""
    eigen = INIT.replace("\n", "\r\n").replace(
        "from .sensor_spaceship import SensorSpaceship\r\n",
        "from .sensor_spaceship import SensorSpaceship\r\nfrom .alpha_ship import AlphaShip\r\n",
    ).replace('    "SensorSpaceship",\r\n]', '    "SensorSpaceship",\r\n    "AlphaShip",\r\n]')

    zusammen = merge_init(INIT.replace("\n", "\r\n"), eigen)

    assert zusammen is not None
    assert "\r\r" not in zusammen


# ----------------------------------------------------------------------
# Backup
# ----------------------------------------------------------------------


def test_die_sicherung_enthaelt_das_projekt(projekt: Path) -> None:
    (projekt / "ships" / "__pycache__").mkdir()
    (projekt / "ships" / "__pycache__" / "x.pyc").write_bytes(b"0")

    ziel = backup(projekt, when="probe")

    with zipfile.ZipFile(ziel) as archive:
        namen = archive.namelist()
    assert "ships/normal_spaceship.py" in namen
    assert not [n for n in namen if "__pycache__" in n]


# ----------------------------------------------------------------------
# Manifest
# ----------------------------------------------------------------------


def test_das_manifest_nennt_sich_nicht_selbst() -> None:
    """Seine eigene Pruefsumme koennte er nicht kennen."""
    text = manifest_of({"tools/paket.json": b"{}", "main_space.py": b"x\n"}, "2026-10-01")

    assert "tools/paket.json" not in text
    assert "main_space.py" in text
