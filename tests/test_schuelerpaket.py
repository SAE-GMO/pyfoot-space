"""Prueft das Paket, das die Schueler:innen bekommen.

Editor-Anforderungsdokument E12. Der Anlass war handfest: Die
**Musterloesungen** der Hausaufgaben standen frueher in diesem Projekt, und wer
den Projektordner unveraendert hochlud, lieferte sie mit. Heute liegen sie im
privaten Projekt pyfoot-course.

Diese Tests bleiben das Sicherheitsnetz dafuer. Sie bauen das Paket in einen
Testordner und sehen nach, was drin ist.
"""

from __future__ import annotations

import ast
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from build_student_package import (  # noqa: E402
    FOLDERS,
    TOOLS,
    build_folder,
    build_zip,
    collect,
    missing_tools,
    package_version,
)

#: Namen, die im Paket nichts zu suchen haben. Sie stehen fuer die
#: Musterloesungen der beiden Hausaufgaben aus M5.
SOLUTIONS = ["WaveShip", "SquareShip", "ChainShip", "RowHarvester", "FigureEightShip"]


@pytest.fixture
def package(tmp_path: Path) -> Path:
    """Baut das Paket als Ordner in einen Testordner."""
    return build_folder(tmp_path / "Space").target


# ----------------------------------------------------------------------
# Was nicht mitgehen darf
# ----------------------------------------------------------------------


def test_die_musterloesungen_bleiben_draussen(package: Path) -> None:
    """Der Grund, aus dem es dieses Werkzeug gibt."""
    gefunden: list[str] = []
    for datei in package.rglob("*.py"):
        text = datei.read_text(encoding="utf-8")
        for name in SOLUTIONS:
            if name in text:
                gefunden.append(f"{datei.name}: {name}")

    assert not gefunden, "Loesungen im Schuelerpaket: " + ", ".join(gefunden)


def test_der_testordner_fehlt(package: Path) -> None:
    assert not (package / "tests").exists()


def test_die_lehrkraftwerkzeuge_fehlen(package: Path) -> None:
    for name in ("check_project.py", "get_pyfoot.py", "build_student_package.py"):
        assert not (package / "tools" / name).exists(), name


def test_kein_zwischenstand_geht_mit(package: Path) -> None:
    """Zwischenordner und Sicherungskopien gehoeren niemandem sonst."""
    for datei in package.rglob("*"):
        assert "__pycache__" not in datei.parts, datei
        assert datei.suffix not in (".pyc", ".bak", ".tmp"), datei


def test_es_wird_nach_einer_erlaubnisliste_gepackt() -> None:
    """Eine spaeter hinzugefuegte Datei der Lehrkraft darf nicht mitgehen."""
    ziele = {ziel for _, ziel in collect()}

    for ziel in ziele:
        oben = ziel.split("/")[0]
        assert oben in FOLDERS or oben == "tools" or "/" not in ziel, ziel
    for ziel in ziele:
        if ziel.startswith("tools/"):
            assert Path(ziel).name in TOOLS, ziel


# ----------------------------------------------------------------------
# Was drin sein muss
# ----------------------------------------------------------------------


def test_alles_zum_arbeiten_ist_dabei(package: Path) -> None:
    for name in ("pyfoot", "space", "ships", "levels"):
        assert (package / name).is_dir(), name
    for name in ("main_space.py", "main_editor.py"):
        assert (package / name).is_file(), name


def test_die_schuelerwerkzeuge_sind_dabei(package: Path) -> None:
    """Die Anleitung verweist auf sie -- ohne waere sie falsch."""
    for name in TOOLS:
        assert (package / "tools" / name).is_file(), name


def test_das_manifest_liegt_bei(package: Path) -> None:
    """Ohne ihn wuesste `update_space.py` nicht, woran gearbeitet wurde."""
    import json

    inhalt = json.loads((package / "tools" / "paket.json").read_text(encoding="utf-8"))

    assert inhalt["version"]
    assert inhalt["dateien"]["main_space.py"]
    assert "tools/paket.json" not in inhalt["dateien"]


def test_die_version_heisst_wie_der_tag(package: Path) -> None:
    """Aus `version = "0.1.2"` wird `v0.1.2` -- wie der Tag auf GitHub.

    Nur dann erkennt `update_space.py` nach dem Entpacken einer `Space.zip`,
    dass die neueste Version schon da ist.
    """
    import json
    import tomllib

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as datei:
        version = tomllib.load(datei)["project"]["version"]
    inhalt = json.loads((package / "tools" / "paket.json").read_text(encoding="utf-8"))

    assert inhalt["version"] == f"v{version}"


def test_ohne_versionsangabe_gilt_die_uhrzeit(tmp_path: Path) -> None:
    """Ein Projekt ohne lesbare `pyproject.toml` bekommt trotzdem eine Version."""
    assert package_version(tmp_path)[:2] == "20"


def test_das_manifest_passt_zum_paket(package: Path) -> None:
    """Jede Pruefsumme muss zu der Datei passen, die daneben liegt."""
    import json

    sys.path.insert(0, str(PROJECT_ROOT / "tools"))
    from update_space import file_hash

    inhalt = json.loads((package / "tools" / "paket.json").read_text(encoding="utf-8"))
    falsch = [
        ziel
        for ziel, summe in inhalt["dateien"].items()
        if file_hash(package / ziel) != summe
    ]

    assert falsch == []


def test_die_lizenzhinweise_sind_dabei(package: Path) -> None:
    """MIT verlangt den Hinweis in jeder Kopie: fuer Space und fuer PyFoot."""
    assert (package / "LICENSE").is_file()
    assert (package / "pyfoot" / "LICENSE").is_file()
    assert (package / "docs" / "LICENSE.md").is_file()


def test_die_anleitungen_sind_dabei(package: Path) -> None:
    """`check_environment.py` verweist auf die Installationsanleitung."""
    for name in ("ANLEITUNG", "SUPPORT_INSTALLATION"):
        assert (package / "docs" / f"{name}.md").is_file(), name
        assert (package / "docs" / f"{name}.pdf").is_file(), name


def test_das_startschiff_ist_dabei(package: Path) -> None:
    assert (package / "ships" / "normal_spaceship.py").is_file()


def test_die_bilder_sind_dabei(package: Path) -> None:
    bilder = list((package / "space" / "assets" / "images").glob("*.png"))

    assert len(bilder) >= 4


def test_die_editoreinstellungen_sind_dabei(package: Path) -> None:
    """`typeCheckingMode: basic` liefert die Typwarnungen im Editor."""
    settings = package / ".vscode" / "settings.json"

    assert settings.is_file()
    assert "typeCheckingMode" in settings.read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# Ist das Paket brauchbar?
# ----------------------------------------------------------------------


def test_jede_datei_im_paket_ist_uebersetzbar(package: Path) -> None:
    for datei in sorted(package.rglob("*.py")):
        quelle = datei.read_text(encoding="utf-8")
        ast.parse(quelle, filename=str(datei))


def test_kein_verweis_geht_ins_leere(package: Path) -> None:
    """Kein Startskript darf eine Datei nennen, die nicht mitgekommen ist."""
    for name in ("main_space.py", "main_editor.py"):
        text = (package / name).read_text(encoding="utf-8")
        for zeile in text.splitlines():
            if "tools\\" in zeile:
                werkzeug = zeile.split("tools\\")[1].split()[0].strip("`\"' ")
                assert (package / "tools" / werkzeug).is_file(), werkzeug


# ----------------------------------------------------------------------
# Das ZIP
# ----------------------------------------------------------------------


def test_das_zip_hat_einen_obersten_ordner(tmp_path: Path) -> None:
    """Sonst verstreuten sich die Dateien beim Entpacken."""
    ziel = build_zip(tmp_path / "Space.zip").target

    with zipfile.ZipFile(ziel) as archiv:
        namen = archiv.namelist()

    assert namen, "Das Archiv ist leer."
    assert all(name.startswith("Space/") for name in namen)


def test_das_zip_enthaelt_dieselben_dateien(tmp_path: Path) -> None:
    ordner = build_folder(tmp_path / "als_ordner").target
    archiv_pfad = build_zip(tmp_path / "Space.zip").target

    with zipfile.ZipFile(archiv_pfad) as archiv:
        im_archiv = {name[len("Space/") :] for name in archiv.namelist()}
    im_ordner = {p.relative_to(ordner).as_posix() for p in ordner.rglob("*") if p.is_file()}

    assert im_archiv == im_ordner


def test_der_bericht_nennt_das_ausgelassene(tmp_path: Path) -> None:
    report = build_zip(tmp_path / "Space.zip")

    assert report.files > 20
    assert "check_project.py" in report.skipped_tools
    assert "Space.zip" in report.summary()


def test_ein_zweiter_lauf_ueberschreibt(tmp_path: Path) -> None:
    """Die Lehrkraft baut das Paket mehrfach -- das darf nicht scheitern."""
    build_folder(tmp_path / "Space")
    (tmp_path / "Space" / "alt.txt").write_text("veraltet", encoding="utf-8")

    build_folder(tmp_path / "Space")

    assert not (tmp_path / "Space" / "alt.txt").exists()


def test_die_liste_der_ausgelassenen_werkzeuge_stimmt() -> None:
    ausgelassen = missing_tools()

    assert "check_project.py" in ausgelassen
    assert "check_environment.py" not in ausgelassen
