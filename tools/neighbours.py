"""Liest die Projektangaben aus `pyproject.toml`.

Zwei Dinge stehen dort an genau einer Stelle:

- `[tool.sae-gmo.pyfoot]`: welche PyFoot-Version mitgeliefert wird und woher
  sie kommt.
- `[tool.sae-gmo.neighbours]`: wo die Nachbarprojekte liegen, relativ zu
  diesem Ordner. Wird ein Projekt umbenannt oder verschoben, aendert sich nur
  diese Zeile.

Beispiel:
    from neighbours import neighbour
    pyfoot = neighbour("pyfoot")
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, NamedTuple

#: Der Projektordner, aus dem Ort dieser Datei bestimmt.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Die Datei mit den Angaben.
CONFIG = PROJECT_ROOT / "pyproject.toml"

__all__ = ["neighbour", "pyfoot_pin", "PyFootPin", "NeighbourMissing"]


class NeighbourMissing(LookupError):
    """Ein Nachbarprojekt ist nicht eingetragen oder liegt nicht dort."""


class PyFootPin(NamedTuple):
    """Die festgelegte PyFoot-Version."""

    version: str
    repository: str

    @property
    def archive_url(self) -> str:
        """Das Archiv dieser Version auf GitHub."""
        return f"{self.repository}/archive/refs/tags/v{self.version}.zip"


def _section(name: str, config: Path = CONFIG) -> dict[str, Any]:
    with config.open("rb") as datei:
        daten = tomllib.load(datei)
    abschnitt: dict[str, Any] = daten.get("tool", {}).get("sae-gmo", {}).get(name, {})
    return abschnitt


def pyfoot_pin(config: Path = CONFIG) -> PyFootPin:
    """Die PyFoot-Version, die dieses Projekt mitliefert."""
    abschnitt = _section("pyfoot", config)
    return PyFootPin(str(abschnitt["version"]), str(abschnitt["repository"]))


def neighbour(name: str, config: Path = CONFIG) -> Path:
    """Der Ordner des Nachbarprojekts `name`.

    Raises:
        NeighbourMissing: Wenn es nicht eingetragen ist oder der Ordner fehlt.
            Die Meldung nennt die Stelle, die anzupassen ist.
    """
    eintraege = _section("neighbours", config)
    if name not in eintraege:
        raise NeighbourMissing(
            f"Kein Nachbarprojekt '{name}' eingetragen. "
            f"Nachtragen in {config.name}, Abschnitt [tool.sae-gmo.neighbours]."
        )
    ordner = (config.parent / str(eintraege[name])).resolve()
    if not ordner.is_dir():
        raise NeighbourMissing(
            f"Das Nachbarprojekt '{name}' liegt nicht unter {ordner}. "
            f"Den Pfad anpassen in {config.name}, Abschnitt [tool.sae-gmo.neighbours]."
        )
    return ordner
