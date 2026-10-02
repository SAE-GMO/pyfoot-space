"""Frischt das Projekt auf eine neue Version auf -- ohne eigene Arbeit zu verlieren.

Aufruf (im Projektordner):

    python tools\\update_space.py --dry-run        zeigt nur, was geschehen wuerde
    python tools\\update_space.py                  holt die neueste Version von GitHub
    python tools\\update_space.py C:\\Pfad\\Space.zip   nimmt genau diese Datei

**Woher die neue Version kommt.** Ohne Pfad fragt das Werkzeug per `git` bei
GitHub nach dem neuesten Versions-Tag (`v0.1.1` usw.), holt diesen Stand und
die PyFoot-Version, die er festlegt, und baut daraus das Paket -- mit dem
Werkzeug aus genau diesem Stand, also so, wie es auch im Release liegt. Das
Repository ist oeffentlich; eine Anmeldung ist nicht noetig. Geht das nicht
(kein `git`, kein Netz), nennt das Werkzeug den Grund; dann hilft der Weg
ueber eine heruntergeladene `Space.zip`.

**Was angefasst wird und was nicht.** Jedes Paket bringt ein Manifest mit
(`tools/paket.json`): darin steht zu jeder Datei eine Pruefsumme. Beim
Auffrischen wird jede Datei mit dem Stand verglichen, der zuletzt ausgeliefert
wurde:

- Datei fehlt          -> wird angelegt.
- Datei unveraendert   -> wird ersetzt; daran hat niemand gearbeitet.
- Datei veraendert     -> **bleibt, wie sie ist.** Die neue Version landet
                          daneben als `name.py.neu` -- zum Vergleichen.
- Datei nur bei dir    -> bleibt unberuehrt; eigene Raumschiffe und Welten
                          gehen nie verloren.

Die beiden Paketdateien `ships/__init__.py` und `levels/__init__.py` sind ein
Sonderfall: Dort steht sowohl Mitgeliefertes als auch Eigenes. Sie werden
**zusammengefuehrt**, damit neue mitgelieferte Klassen im Klassenbaum
erscheinen und die eigenen dort bleiben.

Vor jeder Aenderung legt das Werkzeug ein Backup des ganzen Projekts unter
`backup\\` ab.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

#: Der Projektordner, aus dem Ort dieser Datei bestimmt.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Das Manifest im Paket: Version und Pruefsumme je Datei.
MANIFEST = "tools/paket.json"

#: Dateien, bei denen Zeilenenden nichts bedeuten. Ein Editor, der aus `\n`
#: ein `\r\n` macht, soll keine Datei als "veraendert" erscheinen lassen.
TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".ini", ".txt", ".cfg"}

#: Paketdateien, die Mitgeliefertes **und** Eigenes enthalten.
SHARED_FILES = {"ships/__init__.py", "levels/__init__.py"}

#: Die Ordner, in denen die Schueler:innen arbeiten. Alles ausserhalb ist
#: mitgeliefert -- `pyfoot/` traegt sogar ein "nicht bearbeiten" im Namen der
#: beiliegenden Datei. Das zaehlt nur, solange kein Manifest vorliegt: Mit
#: Manifest entscheidet die Pruefsumme, und zwar ueberall.
STUDENT_FOLDERS = ("ships/", "levels/")

#: Was nicht mit ins Backup wandert -- Zwischenstaende und alte Backups.
SKIP_NAMES = {"__pycache__", ".mypy_cache", ".pytest_cache", ".venv", "backup", "dist"}

#: Ordner, in denen nach einer `Space.zip` gesucht wird, wenn GitHub nicht
#: erreichbar ist -- fuer den Hinweis, wie es trotzdem geht.
SEARCH_FOLDERS = [Path.home() / "Downloads", Path.home() / "Desktop", Path.cwd()]

#: Wo die Versionen liegen, falls `pyproject.toml` es nicht sagt. Aeltere
#: Pakete hatten dort noch keine Angabe.
REPOSITORY = "https://github.com/SAE-GMO/pyfoot-space"

#: Wie lange ein einzelner Schritt (Abfrage, Herunterladen, Bauen) dauern
#: darf, in Sekunden.
TIMEOUT = 300

__all__ = [
    "data_hash",
    "file_hash",
    "manifest_of",
    "package_files",
    "plan",
    "merge_init",
    "apply",
    "backup",
    "find_package",
    "FetchFailed",
    "repository_of",
    "newest_tag",
    "latest_tag",
    "fetch_package",
]


# ----------------------------------------------------------------------
# Pruefsummen
# ----------------------------------------------------------------------


def data_hash(data: bytes, suffix: str) -> str:
    """Berechnet die Pruefsumme eines Inhalts.

    Bei Textdateien werden die Zeilenenden vorher vereinheitlicht: Sonst
    zaehlte jede Datei als veraendert, die ein Editor einmal gespeichert hat.
    """
    if suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str:
    """Berechnet die Pruefsumme einer Datei auf der Platte."""
    return data_hash(path.read_bytes(), path.suffix)


def manifest_of(files: dict[str, bytes], version: str) -> str:
    """Baut das Manifest eines Pakets als JSON-Text."""
    inhalt = {
        "paket": "Space",
        "version": version,
        "dateien": {
            ziel: data_hash(daten, Path(ziel).suffix)
            for ziel, daten in sorted(files.items())
            if ziel != MANIFEST
        },
    }
    return json.dumps(inhalt, indent=2, ensure_ascii=False) + "\n"


# ----------------------------------------------------------------------
# Das neue Paket lesen
# ----------------------------------------------------------------------


def package_files(source: Path) -> dict[str, bytes]:
    """Liest ein Paket -- als ZIP-Datei oder als Ordner.

    Ein ZIP traegt oben den Ordner `Space/`; der wird abgeschnitten, damit die
    Pfade zu denen im Projekt passen.

    Raises:
        ValueError: Wenn die Quelle weder ZIP noch Ordner ist.
    """
    if source.is_dir():
        gefunden = {
            p.relative_to(source).as_posix(): p.read_bytes()
            for p in sorted(source.rglob("*"))
            if p.is_file() and not any(teil in SKIP_NAMES for teil in p.parts)
        }
    elif source.is_file() and source.suffix.lower() == ".zip":
        gefunden = {}
        with zipfile.ZipFile(source) as archive:
            for eintrag in archive.infolist():
                if eintrag.is_dir():
                    continue
                gefunden[eintrag.filename] = archive.read(eintrag)
        gefunden = _without_top_folder(gefunden)
    else:
        raise ValueError(f"Weder ZIP-Datei noch Ordner: {source}")

    if not gefunden:
        raise ValueError(f"Das Paket ist leer: {source}")
    return gefunden


def _without_top_folder(files: dict[str, bytes]) -> dict[str, bytes]:
    """Schneidet einen gemeinsamen obersten Ordner ab."""
    oben = {name.split("/")[0] for name in files if "/" in name}
    if len(oben) != 1 or any("/" not in name for name in files):
        return files
    schnitt = len(oben.pop()) + 1
    return {name[schnitt:]: daten for name, daten in files.items()}


def find_package(folders: list[Path] | None = None) -> Path | None:
    """Sucht die neueste `Space*.zip` in den ueblichen Ordnern."""
    gefunden: list[Path] = []
    for ordner in folders if folders is not None else SEARCH_FOLDERS:
        if ordner.is_dir():
            gefunden.extend(ordner.glob("Space*.zip"))
    if not gefunden:
        return None
    return max(gefunden, key=lambda p: p.stat().st_mtime)


# ----------------------------------------------------------------------
# Vergleichen
# ----------------------------------------------------------------------

#: Was mit einer Datei geschieht.
KINDS = ("neu", "aktualisiert", "zusammengefuehrt", "eigene", "gleich", "entfallen")


class Change(NamedTuple):
    """Eine Datei und das, was mit ihr geschieht."""

    path: str
    kind: str

    def line(self) -> str:
        """Beschreibt den Fall in einem Satz."""
        texte = {
            "neu": "kommt dazu",
            "aktualisiert": "wird aufgefrischt",
            "zusammengefuehrt": "wird zusammengefuehrt (Eigenes bleibt)",
            "eigene": "bleibt -- du hast sie geaendert; neue Version als .neu daneben",
            "gleich": "ist schon aktuell",
            "entfallen": "gehoert nicht mehr zum Paket (bleibt liegen)",
        }
        return f"{self.path}: {texte[self.kind]}"


def plan(project: Path, files: dict[str, bytes], known: dict[str, str]) -> list[Change]:
    """Stellt fest, was mit jeder Datei geschehen soll.

    Args:
        project: Der Projektordner.
        files: Die Dateien des neuen Pakets.
        known: Die Pruefsummen der zuletzt ausgelieferten Version. Fehlt das
            Manifest -- etwa beim ersten Auffrischen eines aelteren
            Projekts --, entscheidet der Ordner: In `ships/` und `levels/`
            wird nichts ueberschrieben, alles Uebrige ist mitgeliefert und
            wird erneuert.

    Returns:
        Je Datei ein `Change`, nach Pfad sortiert.
    """
    changes: list[Change] = []
    for ziel, daten in sorted(files.items()):
        if ziel == MANIFEST:
            continue
        hier = project / ziel
        neu = data_hash(daten, Path(ziel).suffix)
        if not hier.is_file():
            changes.append(Change(ziel, "neu"))
        elif file_hash(hier) == neu:
            changes.append(Change(ziel, "gleich"))
        elif known.get(ziel) == file_hash(hier):
            changes.append(Change(ziel, "aktualisiert"))
        elif ziel in SHARED_FILES:
            changes.append(Change(ziel, "zusammengefuehrt"))
        elif ziel in known or ziel.startswith(STUDENT_FOLDERS):
            changes.append(Change(ziel, "eigene"))
        else:
            changes.append(Change(ziel, "aktualisiert"))

    for ziel in sorted(set(known) - set(files)):
        if (project / ziel).is_file():
            changes.append(Change(ziel, "entfallen"))
    return changes


# ----------------------------------------------------------------------
# Paketdateien zusammenfuehren
# ----------------------------------------------------------------------

#: Eine Einfuhr in einer Paketdatei: `from .normal_spaceship import NormalSpaceship`.
_IMPORT = re.compile(r"^from \.(\w+) import (\w+)\s*$")


def merge_init(new_text: str, own_text: str) -> str | None:
    """Traegt die eigenen Klassen in die neue Paketdatei ein.

    Grundlage ist die **neue** Datei: Ihre Reihenfolge stimmt, und ein
    Grundklassen-Eintrag steht dort vor denen, die von ihm erben. Die eigenen
    Klassen kommen dahinter, in ihrer bisherigen Reihenfolge.

    Returns:
        Den neuen Text -- oder `None`, wenn die Datei nicht dem erwarteten
        Aufbau folgt. Dann bleibt sie unberuehrt.
    """
    neu = _imports(new_text)
    eigen = [paar for paar in _imports(own_text) if paar not in neu]
    if not neu:
        return None
    if not eigen:
        return new_text

    lines = new_text.splitlines(keepends=True)
    umbruch = "\r\n" if new_text.count("\r\n") > new_text.count("\n") // 2 else "\n"
    letzte = max(n for n, zeile in enumerate(lines) if _IMPORT.match(zeile))
    lines[letzte + 1 : letzte + 1] = [
        f"from .{modul} import {name}{umbruch}" for modul, name in eigen
    ]

    ergaenzt = _extended_all(lines, [name for _, name in eigen], umbruch)
    if ergaenzt is None:
        return None
    return "".join(ergaenzt)


def _imports(text: str) -> list[tuple[str, str]]:
    """Liefert die Einfuhren einer Paketdatei in ihrer Reihenfolge."""
    treffer = (_IMPORT.match(zeile) for zeile in text.splitlines())
    return [(m.group(1), m.group(2)) for m in treffer if m is not None]


def _extended_all(lines: list[str], names: list[str], umbruch: str) -> list[str] | None:
    """Haengt Namen an die `__all__`-Liste an."""
    anfang = next((n for n, z in enumerate(lines) if z.startswith("__all__")), None)
    if anfang is None:
        return None
    ende = next((n for n in range(anfang, len(lines)) if lines[n].rstrip() == "]"), None)
    if ende is None:
        return None
    lines[ende:ende] = [f'    "{name}",{umbruch}' for name in names]
    return lines


# ----------------------------------------------------------------------
# Backup und Anwenden
# ----------------------------------------------------------------------


def backup(project: Path, when: str | None = None) -> Path:
    """Legt ein Backup des ganzen Projekts als ZIP unter `backup\\` ab.

    Returns:
        Der Pfad des Backups.
    """
    stempel = when if when is not None else datetime.now().strftime("%Y-%m-%d_%H%M%S")
    ziel = project / "backup" / f"Space_{stempel}.zip"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as archive:
        for pfad in sorted(project.rglob("*")):
            teile = pfad.relative_to(project).parts
            if pfad.is_file() and not any(teil in SKIP_NAMES for teil in teile):
                archive.write(pfad, "/".join(teile))
    return ziel


def apply(project: Path, files: dict[str, bytes], changes: list[Change]) -> list[str]:
    """Fuehrt den Plan aus.

    Returns:
        Die Meldungen zu allem, was Aufmerksamkeit braucht.
    """
    hinweise: list[str] = []
    for change in changes:
        ziel = project / change.path
        if change.kind in ("neu", "aktualisiert"):
            ziel.parent.mkdir(parents=True, exist_ok=True)
            ziel.write_bytes(files[change.path])
        elif change.kind == "zusammengefuehrt":
            _merge_file(ziel, files[change.path], change.path, hinweise)
        elif change.kind == "eigene":
            daneben = ziel.with_suffix(ziel.suffix + ".neu")
            daneben.write_bytes(files[change.path])
            hinweise.append(
                f"{change.path} hast du geaendert -- die neue Version liegt als "
                f"{daneben.name} daneben."
            )
        elif change.kind == "entfallen":
            hinweise.append(
                f"{change.path} gehoert nicht mehr zum Kurs. Sie bleibt liegen; "
                "du kannst sie loeschen."
            )
    return hinweise


def _merge_file(ziel: Path, daten: bytes, name: str, hinweise: list[str]) -> None:
    """Fuehrt eine Paketdatei zusammen -- oder legt die neue daneben.

    Gelesen und geschrieben wird als Bytes: Sonst machte Windows aus jedem
    Zeilenende zwei.
    """
    zusammen = merge_init(daten.decode("utf-8"), ziel.read_bytes().decode("utf-8"))
    if zusammen is None:
        daneben = ziel.with_suffix(ziel.suffix + ".neu")
        daneben.write_bytes(daten)
        hinweise.append(
            f"{name} liess sich nicht zusammenfuehren. Die neue Version liegt "
            f"als {daneben.name} daneben."
        )
        return
    ziel.write_bytes(zusammen.encode("utf-8"))


# ----------------------------------------------------------------------
# Die neueste Version von GitHub holen
# ----------------------------------------------------------------------

#: Ein Versions-Tag in der Ausgabe von `git ls-remote --tags`.
_TAG = re.compile(r"refs/tags/(v(\d+)\.(\d+)\.(\d+))$")

#: Fuehrt einen Befehl aus und liefert seine Ausgabe: Befehl, Arbeitsordner.
Runner = Callable[[list[str], Path | None], str]


class FetchFailed(Exception):
    """Die neue Version liess sich nicht holen -- der Text sagt, warum."""


def repository_of(project: Path) -> str:
    """Liest die Adresse des Repositorys aus `pyproject.toml`.

    Returns:
        Die Adresse unter `[project.urls]`, sonst `REPOSITORY`.
    """
    try:
        with (project / "pyproject.toml").open("rb") as datei:
            daten = tomllib.load(datei)
    except (OSError, tomllib.TOMLDecodeError):
        return REPOSITORY
    adresse = daten.get("project", {}).get("urls", {}).get("Repository")
    return str(adresse) if adresse else REPOSITORY


def newest_tag(ls_remote: str) -> str | None:
    """Findet in der Ausgabe von `git ls-remote --tags` den neuesten Tag.

    Gezaehlt werden nur Tags der Form `v1.2.3`, verglichen Zahl fuer Zahl --
    `v0.10.0` ist also neuer als `v0.9.0`.
    """
    tags: list[tuple[tuple[int, int, int], str]] = []
    for zeile in ls_remote.splitlines():
        treffer = _TAG.search(zeile.strip())
        if treffer:
            nummer = (int(treffer[2]), int(treffer[3]), int(treffer[4]))
            tags.append((nummer, treffer[1]))
    return max(tags)[1] if tags else None


def _run(command: list[str], cwd: Path | None) -> str:
    """Fuehrt einen Befehl aus; ein Fehler wird zu `FetchFailed`.

    `git` fragt dabei nie nach einem Kennwort: Das Repository ist oeffentlich,
    und eine Rueckfrage liesse das Werkzeug sonst haengen.
    """
    umgebung = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        ergebnis = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True,
            env=umgebung, timeout=TIMEOUT,
        )
    except FileNotFoundError as fehler:
        raise FetchFailed(f"{command[0]} wurde nicht gefunden.") from fehler
    except subprocess.TimeoutExpired as fehler:
        raise FetchFailed(f"Keine Antwort nach {TIMEOUT} Sekunden.") from fehler
    if ergebnis.returncode != 0:
        meldung = (ergebnis.stderr or ergebnis.stdout).strip().splitlines()
        raise FetchFailed(meldung[-1] if meldung else f"{command[0]} schlug fehl.")
    return ergebnis.stdout


def _git(*arguments: str) -> list[str]:
    """Baut einen git-Befehl, der die Einstellungen des Rechners nicht braucht.

    - Keine gespeicherte Anmeldung: Das Repository ist oeffentlich.
    - Keine Umwandlung der Zeilenenden: Mit `core.autocrlf=true`, unter
      Windows ueblich, machte git sonst auch in PDF-Dateien aus jedem
      Zeilenende-Byte zwei -- und die PDFs waeren kaputt. So kommt jede
      Datei Byte fuer Byte an, wie sie im Repository liegt.
    """
    git = shutil.which("git")
    if git is None:
        raise FetchFailed("git ist auf diesem Rechner nicht installiert.")
    return [git, "-c", "credential.helper=", "-c", "core.autocrlf=false", *arguments]


def latest_tag(repository: str, run: Runner = _run) -> str:
    """Fragt bei GitHub nach dem neuesten Versions-Tag.

    Raises:
        FetchFailed: Ohne git, ohne Netz -- oder wenn es noch keinen Tag gibt.
    """
    tag = newest_tag(run(_git("ls-remote", "--tags", "--refs", repository), None))
    if tag is None:
        raise FetchFailed(f"Unter {repository} gibt es noch keine Version.")
    return tag


def fetch_package(
    repository: str, tag: str, workdir: Path, run: Runner = _run
) -> Path:
    """Holt einen Stand von GitHub und baut daraus das Schuelerpaket.

    Gebaut wird mit den Werkzeugen **aus diesem Stand**: Was ins Paket
    gehoert, steht damit an genau einer Stelle, und das Ergebnis gleicht dem
    Release. PyFoot kommt als Nachbarordner dazu, in der festgelegten Version.

    Args:
        repository: Adresse von pyfoot-space.
        tag: Der Versions-Tag, etwa `v0.1.1`.
        workdir: Ein leerer Ordner fuer die Zwischenstaende.
        run: Fuehrt einen Befehl aus (fuer die Tests austauschbar).

    Returns:
        Der Ordner mit dem fertigen Paket.

    Raises:
        FetchFailed: Wenn ein Schritt scheitert.
    """
    space = workdir / "pyfoot-space"
    run(_git("clone", "--quiet", "--depth", "1", "--branch", tag, repository, str(space)), None)

    try:
        with (space / "pyproject.toml").open("rb") as datei:
            sae_gmo = tomllib.load(datei)["tool"]["sae-gmo"]
        version = str(sae_gmo["pyfoot"]["version"])
        pyfoot_repository = str(sae_gmo["pyfoot"]["repository"])
        nachbar = str(sae_gmo["neighbours"]["pyfoot"])
    except (OSError, KeyError, tomllib.TOMLDecodeError) as fehler:
        raise FetchFailed(f"{tag}: pyproject.toml nennt keine PyFoot-Version.") from fehler

    pyfoot = (space / nachbar).resolve()
    run(
        _git("clone", "--quiet", "--depth", "1", "--branch", f"v{version}",
             pyfoot_repository, str(pyfoot)),
        None,
    )
    run([sys.executable, str(space / "tools" / "get_pyfoot.py"), "--local"], space)

    ziel = workdir / "paket"
    run(
        [sys.executable, str(space / "tools" / "build_student_package.py"),
         "--folder", "--out", str(ziel)],
        space,
    )
    paket = ziel / "Space"
    if not paket.is_dir():
        raise FetchFailed(f"{tag}: Das Paket wurde nicht gebaut.")
    return paket


# ----------------------------------------------------------------------
# Aufruf
# ----------------------------------------------------------------------


def _known_hashes(project: Path) -> tuple[dict[str, str], str]:
    """Liest das Manifest der Version, die gerade im Projekt liegt."""
    pfad = project / MANIFEST
    if not pfad.is_file():
        return {}, "unbekannt"
    try:
        inhalt = json.loads(pfad.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, "unlesbar"
    dateien = inhalt.get("dateien", {})
    return dateien, str(inhalt.get("version", "unbekannt"))


def main(arguments: list[str]) -> int:
    """Frischt das Projekt auf und meldet, was geschehen ist."""
    parser = argparse.ArgumentParser(
        description="Frischt Space auf, ohne eigene Dateien zu ueberschreiben."
    )
    parser.add_argument(
        "quelle", nargs="?",
        help="Space.zip oder ein Ordner; ohne Angabe die neueste Version von GitHub",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="nur zeigen, was geschehen wuerde"
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="kein Backup anlegen"
    )
    options = parser.parse_args(arguments)

    bekannt, alte_version = _known_hashes(PROJECT_ROOT)

    if options.quelle:
        quelle = Path(options.quelle)
        if not quelle.exists():
            print(f"Nicht gefunden: {quelle}", file=sys.stderr)
            return 1
        try:
            files = package_files(quelle)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 1
        herkunft = str(quelle)
        neue_version = _version_of(files)
    else:
        geholt = _from_github(alte_version)
        if isinstance(geholt, int):
            return geholt
        herkunft, neue_version, files = geholt

    changes = plan(PROJECT_ROOT, files, bekannt)

    print(f"Paket:   {herkunft}")
    print(f"Version: {alte_version}  ->  {neue_version}")
    print("=" * 60)
    _report(changes)

    zu_tun = [c for c in changes if c.kind not in ("gleich", "entfallen")]
    if not zu_tun:
        print("\nAlles ist schon aktuell. Es gibt nichts zu tun.")
        return 0
    if options.dry_run:
        print("\nDry run -- es wurde nichts geaendert.")
        return 0
    if (PROJECT_ROOT / "tests").is_dir():
        # Das Projekt der Lehrkraft ist die Quelle der Pakete, nicht ihr Ziel.
        print("\nHier liegt ein Ordner tests\\ -- das ist das Projekt der Lehrkraft.")
        print("Es wird nicht aufgefrischt. Ein Dry run geht: --dry-run")
        return 1

    if not options.no_backup:
        print(f"\nBackup: {backup(PROJECT_ROOT)}")

    hinweise = apply(PROJECT_ROOT, files, changes)
    (PROJECT_ROOT / MANIFEST).write_text(
        manifest_of(files, neue_version), encoding="utf-8"
    )

    print("\nFertig.")
    for hinweis in hinweise:
        print(f"  ! {hinweis}")
    return 0


def _from_github(alte_version: str) -> tuple[str, str, dict[str, bytes]] | int:
    """Holt die neueste Version von GitHub.

    Returns:
        Herkunft, Version und Dateien des Pakets -- oder, wenn es nichts zu
        tun gibt oder nicht ging, gleich den Rueckgabewert fuer `main`: 0,
        wenn die neueste Version schon da ist, 1 bei einem Fehler (der Grund
        ist dann schon gemeldet).
    """
    repository = repository_of(PROJECT_ROOT)
    print(f"Frage {repository} nach der neuesten Version ...")
    try:
        tag = latest_tag(repository)
        if tag == alte_version:
            print(f"Du hast schon die neueste Version ({tag}). Es gibt nichts zu tun.")
            return 0
        print(f"Hole {tag} ...")
        with tempfile.TemporaryDirectory(
            prefix="space_update_", ignore_cleanup_errors=True
        ) as zwischen:
            files = package_files(fetch_package(repository, tag, Path(zwischen)))
    except (FetchFailed, ValueError) as fehler:
        print(f"Die neue Version liess sich nicht von GitHub holen: {fehler}")
        print("Stattdessen geht es mit einer heruntergeladenen Space.zip:")
        zip_datei = find_package()
        beispiel = zip_datei if zip_datei is not None else Path("C:/Pfad/Space.zip")
        print(f"    python tools\\update_space.py {beispiel}")
        return 1
    return f"{repository} ({tag})", tag, files


def _version_of(files: dict[str, bytes]) -> str:
    """Liest die Version aus dem Manifest des neuen Pakets."""
    if MANIFEST not in files:
        return "ohne Angabe"
    try:
        return str(json.loads(files[MANIFEST].decode("utf-8")).get("version", "?"))
    except json.JSONDecodeError:  # pragma: no cover -- kaputtes Paket
        return "unlesbar"


def _report(changes: list[Change]) -> None:
    """Zeigt den Plan, nach Art gebuendelt."""
    for kind in KINDS:
        betroffen = [c for c in changes if c.kind == kind]
        if not betroffen:
            continue
        if kind == "gleich":
            print(f"  {len(betroffen)} Datei(en) sind schon aktuell.")
            continue
        for change in betroffen:
            print(f"  {change.line()}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
