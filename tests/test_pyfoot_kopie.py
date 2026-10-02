"""Prueft die mitgelieferte Kopie der Bibliothek PyFoot.

Space liefert PyFoot mit, statt es zu installieren -- an der Schule hat niemand
Administratorrechte. Im Repository liegt die Kopie nicht; `tools/get_pyfoot.py`
holt die Version, die in `pyproject.toml` festgelegt ist. Diese Tests stellen
sicher, dass die Kopie brauchbar ist und genau diese Version hat.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

import get_pyfoot  # noqa: E402
from neighbours import NeighbourMissing, PyFootPin, neighbour, pyfoot_pin  # noqa: E402

COPY = PROJECT_ROOT / "pyfoot"
MARKER = COPY / get_pyfoot.MARKER_NAME

PIN = PyFootPin("9.9.9", "https://example.invalid/pyfoot")


def test_kopie_ist_vorhanden() -> None:
    assert COPY.is_dir(), "PyFoot fehlt. Holen mit: python tools\\get_pyfoot.py"
    assert (COPY / "__init__.py").is_file()


def test_kopie_hat_die_festgelegte_version() -> None:
    """Sonst liefe Space gegen eine Bibliothek, gegen die es nie geprueft wurde."""
    assert get_pyfoot.installed_version() == pyfoot_pin().version, (
        "Falsche PyFoot-Version. Auffrischen mit: python tools\\get_pyfoot.py"
    )


def test_kopie_laesst_sich_einbinden() -> None:
    """Ohne Installation, allein weil sie im Projektordner liegt."""
    import pyfoot

    assert Path(pyfoot.__file__).parent == COPY


def test_typangaben_sind_mitgeliefert() -> None:
    """Ohne py.typed sehen mypy und Pylance die Typen nicht."""
    assert (COPY / "py.typed").is_file()


def test_marker_warnt_vor_bearbeitung() -> None:
    assert MARKER.is_file(), "Der Hinweis auf den Kopie-Charakter fehlt"
    text = MARKER.read_text(encoding="utf-8")
    assert "get_pyfoot" in text
    assert pyfoot_pin().repository in text


def test_kein_archiv_statt_ordner() -> None:
    """Aus einer ZIP koennten mypy und Pylance die Typangaben nicht lesen.

    Gemessen: Die Typpruefung meldete dann faelschlich "keine Fehler". Deshalb
    liegt die Bibliothek bewusst als Ordner vor.
    """
    assert not (PROJECT_ROOT / "pyfoot.zip").exists()
    assert not (PROJECT_ROOT / "lib" / "pyfoot.zip").exists()
    assert COPY.is_dir()


def test_die_kopie_steht_nicht_im_repository() -> None:
    """Sie wird geholt, nicht eingecheckt -- sonst liefe sie auseinander."""
    eintraege = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").split()
    assert "/pyfoot/" in eintraege


# ----------------------------------------------------------------------
# Das Werkzeug selbst, an einer Attrappe
# ----------------------------------------------------------------------


def fake_package(folder: Path, version: str = "9.9.9") -> Path:
    paket = folder / "pyfoot"
    paket.mkdir(parents=True)
    (paket / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    (paket / "py.typed").write_text("", encoding="utf-8")
    (paket / "__pycache__").mkdir()
    (paket / "__pycache__" / "alt.pyc").write_bytes(b"x")
    return paket


def test_version_wird_aus_der_kopie_gelesen(tmp_path: Path) -> None:
    assert get_pyfoot.installed_version(tmp_path / "fehlt") is None
    assert get_pyfoot.installed_version(fake_package(tmp_path)) == "9.9.9"


def test_aus_einem_ordner_uebernehmen(tmp_path: Path) -> None:
    quelle = fake_package(tmp_path / "quelle")
    ziel = tmp_path / "ziel" / "pyfoot"
    ziel.mkdir(parents=True)
    (ziel / "veraltet.py").write_text("", encoding="utf-8")

    version = get_pyfoot.install_from_folder(quelle, "Test", ziel, PIN)

    assert version == "9.9.9"
    assert (ziel / "py.typed").is_file()
    assert not (ziel / "veraltet.py").exists(), "Alte Dateien muessen verschwinden"
    assert not (ziel / "__pycache__").exists()
    assert "Version 9.9.9" in (ziel / get_pyfoot.MARKER_NAME).read_text(encoding="utf-8")


def test_aus_einem_github_archiv_uebernehmen(tmp_path: Path) -> None:
    """GitHub legt alles in einen Ordner `pyfoot-<version>/`."""
    archiv = tmp_path / "v9.9.9.zip"
    with zipfile.ZipFile(archiv, "w") as zip_datei:
        zip_datei.writestr("pyfoot-9.9.9/README.md", "")
        zip_datei.writestr("pyfoot-9.9.9/LICENSE", "MIT License")
        zip_datei.writestr("pyfoot-9.9.9/pyfoot/__init__.py", '__version__ = "9.9.9"\n')
        zip_datei.writestr("pyfoot-9.9.9/pyfoot/py.typed", "")
    ziel = tmp_path / "pyfoot"

    assert get_pyfoot.install_from_archive(archiv, "Test", ziel, PIN) == "9.9.9"
    assert (ziel / "py.typed").is_file()
    assert not (ziel / "README.md").exists()
    assert (ziel / "LICENSE").read_text(encoding="utf-8") == "MIT License"


def test_die_kopie_traegt_den_lizenzhinweis() -> None:
    """Die MIT-Lizenz verlangt ihn in jeder Kopie -- auch im Schuelerpaket."""
    assert (COPY / "LICENSE").is_file(), "Auffrischen mit: python tools\\get_pyfoot.py"
    assert "MIT License" in (COPY / "LICENSE").read_text(encoding="utf-8")


def test_archiv_ohne_paket_wird_gemeldet(tmp_path: Path) -> None:
    archiv = tmp_path / "leer.zip"
    with zipfile.ZipFile(archiv, "w") as zip_datei:
        zip_datei.writestr("irgendwas/README.md", "")

    with pytest.raises(get_pyfoot.PyFootMissing):
        get_pyfoot.install_from_archive(archiv, "Test", tmp_path / "pyfoot", PIN)


def test_archivadresse_nennt_die_version() -> None:
    assert PIN.archive_url == "https://example.invalid/pyfoot/archive/refs/tags/v9.9.9.zip"


def test_fehlender_nachbar_nennt_die_stelle(tmp_path: Path) -> None:
    config = tmp_path / "pyproject.toml"
    config.write_text('[tool.sae-gmo.neighbours]\npyfoot = "../gibt-es-nicht"\n', encoding="utf-8")

    with pytest.raises(NeighbourMissing, match=r"tool\.sae-gmo\.neighbours"):
        neighbour("pyfoot", config)
    with pytest.raises(NeighbourMissing, match="eingetragen"):
        neighbour("course", config)
