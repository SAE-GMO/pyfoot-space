"""Die Startkonfigurationen fuer PyCharm (`.run/`).

PyCharm liest sie beim Oeffnen des Projektordners und bietet sie oben rechts
zur Wahl an. Getestet werden kann hier nur ihr Inhalt, nicht PyCharm selbst.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from build_student_package import PACKAGE_NAME  # noqa: E402

KONFIGURATIONEN = sorted((PROJECT_ROOT / ".run").glob("*.run.xml"))


def _optionen(datei: Path) -> tuple[ET.Element, dict[str, str]]:
    konfiguration = ET.parse(datei).getroot().find("configuration")
    assert konfiguration is not None
    optionen = {
        o.get("name", ""): o.get("value", "") for o in konfiguration.findall("option")
    }
    return konfiguration, optionen


def test_es_gibt_beide_startkonfigurationen() -> None:
    assert [d.name for d in KONFIGURATIONEN] == ["Editor.run.xml", "Raumschiff.run.xml"]


@pytest.mark.parametrize("datei", KONFIGURATIONEN, ids=lambda d: d.stem)
def test_das_startskript_gibt_es(datei: Path) -> None:
    _, optionen = _optionen(datei)
    skript = optionen["SCRIPT_NAME"].replace("$PROJECT_DIR$", str(PROJECT_ROOT))

    assert Path(skript).is_file()


@pytest.mark.parametrize("datei", KONFIGURATIONEN, ids=lambda d: d.stem)
def test_gestartet_wird_im_projektordner(datei: Path) -> None:
    """Sonst stimmen die relativen Pfade nicht -- wie `cwd` in VS Code."""
    _, optionen = _optionen(datei)

    assert optionen["WORKING_DIRECTORY"] == "$PROJECT_DIR$"


@pytest.mark.parametrize("datei", KONFIGURATIONEN, ids=lambda d: d.stem)
def test_das_modul_heisst_wie_der_ordner_im_paket(datei: Path) -> None:
    """PyCharm benennt das Modul nach dem geoeffneten Ordner.

    Die Schueler:innen oeffnen `SpaceProject`; heisst das Modul anders, meldet
    PyCharm die Konfiguration als fehlerhaft.
    """
    konfiguration, _ = _optionen(datei)
    modul = konfiguration.find("module")

    assert modul is not None and modul.get("name") == PACKAGE_NAME


@pytest.mark.parametrize("datei", KONFIGURATIONEN, ids=lambda d: d.stem)
def test_kein_fest_eingetragenes_python(datei: Path) -> None:
    """Das Python waehlt jeder Rechner selbst; ein Pfad hier passte nur auf einen."""
    _, optionen = _optionen(datei)

    assert optionen["SDK_HOME"] == ""
    assert optionen["IS_MODULE_SDK"] == "true"
