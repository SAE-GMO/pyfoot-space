"""Holt die Bibliothek PyFoot in den Projektordner.

Space liefert PyFoot mit, statt es zu installieren: An der Schule hat niemand
Administratorrechte. Im Git-Repository liegt der Ordner `pyfoot/` aber nicht.
Welche Version gebraucht wird, steht in `pyproject.toml` unter
`[tool.sae-gmo.pyfoot]` -- und dieses Werkzeug holt genau sie.

Bewusst als Ordner, **nicht** als ZIP-Datei: Aus einem Archiv koennen weder
mypy noch Pylance die Typangaben lesen. Die Typpruefung meldete dann
faelschlich "keine Fehler", statt die vorhandenen zu zeigen.

Aufruf (im Ordner pyfoot-space):
    python tools\\get_pyfoot.py            festgelegte Version von GitHub holen
    python tools\\get_pyfoot.py --local    Stand des Nachbarprojekts pyfoot
                                           uebernehmen (zum Entwickeln)

Das Schuelerpaket enthaelt PyFoot bereits; im Unterricht wird das Werkzeug
nicht gebraucht.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from neighbours import PyFootPin, neighbour, pyfoot_pin  # noqa: E402 -- liegt daneben

#: Der Projektordner, aus dem Ort dieser Datei bestimmt.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Wohin die Bibliothek kommt.
TARGET = PROJECT_ROOT / "pyfoot"

MARKER_NAME = "KOPIE_NICHT_BEARBEITEN.md"

#: Was beim Kopieren nicht mitgeht.
_SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", ".mypy_cache", ".pytest_cache")

_VERSION = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)

__all__ = [
    "installed_version",
    "install_from_folder",
    "install_from_archive",
    "fetch",
    "ensure",
    "PyFootMissing",
]


class PyFootMissing(RuntimeError):
    """PyFoot liess sich nicht beschaffen."""


def marker_text(version: str, source: str, pin: PyFootPin) -> str:
    """Der Hinweis, der in der Kopie liegt."""
    return f"""# Kopie -- hier bitte nichts aendern

Dieser Ordner ist eine Kopie der Bibliothek **PyFoot**, Version {version}
(Quelle: {source}). Er wird mitgeliefert, damit das Projekt ohne Installation
laeuft.

**Aenderungen gehoeren in das Projekt PyFoot:** {pin.repository}

Eine andere Version holen: sie in `pyproject.toml` unter `[tool.sae-gmo.pyfoot]`
eintragen, dann im Projektordner:

    python tools\\get_pyfoot.py
"""


def installed_version(target: Path = TARGET) -> str | None:
    """Die Version der vorhandenen Kopie, oder None, wenn keine da ist."""
    init = target / "__init__.py"
    if not init.is_file():
        return None
    gefunden = _VERSION.search(init.read_text(encoding="utf-8"))
    return gefunden.group(1) if gefunden else None


def install_from_folder(
    source: Path, description: str, target: Path = TARGET, pin: PyFootPin | None = None
) -> str:
    """Kopiert den Paketordner `source` nach `target`.

    Erst in einen Nachbarordner, dann getauscht: Bricht das Kopieren ab, bleibt
    die bisherige Kopie stehen.

    Returns:
        Die Version der neuen Kopie.
    """
    version = installed_version(source)
    if version is None:
        raise PyFootMissing(f"In {source} liegt keine PyFoot-Bibliothek.")

    neu = target.with_name(target.name + ".neu")
    if neu.exists():
        shutil.rmtree(neu)
    shutil.copytree(source, neu, ignore=_SKIP)
    # Die MIT-Lizenz verlangt ihren Hinweis in jeder Kopie. Er liegt im
    # Repository neben dem Paketordner, nicht darin.
    lizenz = source.parent / "LICENSE"
    if lizenz.is_file():
        shutil.copyfile(lizenz, neu / "LICENSE")
    (neu / MARKER_NAME).write_text(
        marker_text(version, description, pin or pyfoot_pin()), encoding="utf-8"
    )
    if target.exists():
        shutil.rmtree(target)
    neu.rename(target)
    return version


def install_from_archive(
    archive: Path, description: str, target: Path = TARGET, pin: PyFootPin | None = None
) -> str:
    """Entpackt ein Archiv des PyFoot-Repositorys und uebernimmt `pyfoot/` daraus.

    GitHub legt alles in einen Ordner `pyfoot-<version>/`; darin liegt das
    Paket `pyfoot/`.
    """
    with tempfile.TemporaryDirectory() as ordner:
        with zipfile.ZipFile(archive) as zip_datei:
            zip_datei.extractall(ordner)
        pakete = sorted(Path(ordner).glob("*/pyfoot/__init__.py"))
        if not pakete:
            raise PyFootMissing(f"Das Archiv {archive.name} enthaelt kein Paket pyfoot/.")
        return install_from_folder(pakete[0].parent, description, target, pin)


def _download(url: str, ziel: Path) -> None:
    try:
        with urllib.request.urlopen(url, timeout=60) as antwort:
            ziel.write_bytes(antwort.read())
    except urllib.error.HTTPError as fehler:
        raise PyFootMissing(
            f"{url} ist nicht abrufbar ({fehler.code}). Gibt es die Version schon?"
        ) from fehler
    except (urllib.error.URLError, TimeoutError) as fehler:
        raise PyFootMissing(
            f"Keine Verbindung zu {url}. Besteht eine Internetverbindung?"
        ) from fehler


def fetch(local: bool = False, target: Path = TARGET) -> str:
    """Holt PyFoot: die festgelegte Version von GitHub oder den lokalen Stand.

    Returns:
        Die Version der neuen Kopie.
    """
    pin = pyfoot_pin()
    if local:
        quelle = neighbour("pyfoot") / "pyfoot"
        return install_from_folder(quelle, "Nachbarprojekt pyfoot (lokal)", target, pin)

    with tempfile.TemporaryDirectory() as ordner:
        archiv = Path(ordner) / "pyfoot.zip"
        _download(pin.archive_url, archiv)
        version = install_from_archive(archiv, pin.archive_url, target, pin)
    if version != pin.version:
        raise PyFootMissing(
            f"Das Archiv enthaelt Version {version} statt {pin.version}."
        )
    return version


def ensure(target: Path = TARGET) -> str:
    """Sorgt dafuer, dass die festgelegte Version vorliegt; holt sie sonst.

    Returns:
        Die Version der Kopie.
    """
    vorhanden = installed_version(target)
    if vorhanden == pyfoot_pin().version:
        return vorhanden
    return fetch(target=target)


def main(arguments: list[str]) -> int:
    """Holt PyFoot und meldet, welche Version jetzt vorliegt."""
    parser = argparse.ArgumentParser(description="Holt die Bibliothek PyFoot in dieses Projekt.")
    parser.add_argument(
        "--local",
        action="store_true",
        help="den Stand aus dem Nachbarprojekt pyfoot uebernehmen (zum Entwickeln)",
    )
    options = parser.parse_args(arguments)

    pin = pyfoot_pin()
    try:
        version = fetch(local=options.local)
    except (PyFootMissing, LookupError) as fehler:
        print(f"PyFoot konnte nicht geholt werden: {fehler}")
        return 1

    print(f"PyFoot {version} liegt jetzt in {TARGET}")
    if version != pin.version:
        print(f"Hinweis: Festgelegt ist Version {pin.version} (pyproject.toml).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
