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

import update_space  # noqa: E402
from update_space import (  # noqa: E402
    REPOSITORY,
    Change,
    FetchFailed,
    apply,
    backup,
    data_hash,
    fetch_package,
    find_package,
    latest_tag,
    manifest_of,
    merge_init,
    newest_tag,
    package_files,
    plan,
    repository_of,
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


# ----------------------------------------------------------------------
# Neueste Version von GitHub
#
# Hier laeuft kein echtes git: Ein nachgebauter Ablauf legt an, was ein
# Klonen anlegen wuerde, und merkt sich die Befehle. So pruefen die Tests
# ohne Netz, was das Werkzeug verlangt.
# ----------------------------------------------------------------------

LS_REMOTE = """\
1111111111111111111111111111111111111111\trefs/tags/v0.9.0
2222222222222222222222222222222222222222\trefs/tags/v0.10.0
3333333333333333333333333333333333333333\trefs/tags/v0.2.5
4444444444444444444444444444444444444444\trefs/tags/probe
"""

SPACE_PYPROJECT = """\
[tool.sae-gmo.pyfoot]
version = "0.3.0"
repository = "https://example.org/pyfoot"

[tool.sae-gmo.neighbours]
pyfoot = "../pyfoot"
"""


class FakeRunner:
    """Merkt sich die Befehle und legt an, was sie anlegen wuerden."""

    def __init__(self, ls_remote: str = LS_REMOTE, build: bool = True) -> None:
        self.ls_remote = ls_remote
        self.build = build
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], cwd: Path | None) -> str:
        self.commands.append(command)
        if "ls-remote" in command:
            return self.ls_remote
        if "clone" in command:
            ziel = Path(command[-1])
            ziel.mkdir(parents=True)
            if "pyfoot-space" in ziel.name:
                (ziel / "pyproject.toml").write_text(SPACE_PYPROJECT, encoding="utf-8")
        elif command[-3:-1] == ["--folder", "--out"] and self.build:
            paket = Path(command[-1]) / "Space"
            paket.mkdir(parents=True)
            (paket / "main_space.py").write_text("neu\n", encoding="utf-8")
        return ""


def test_der_neueste_tag_wird_zahlenweise_bestimmt() -> None:
    """`v0.10.0` ist neuer als `v0.9.0`, auch wenn es als Text kleiner ist."""
    assert newest_tag(LS_REMOTE) == "v0.10.0"


def test_ohne_versions_tag_gibt_es_keinen_neuesten() -> None:
    """Andere Tags zaehlen nicht."""
    assert newest_tag("abc\trefs/tags/probe\n") is None
    assert newest_tag("") is None


def test_die_adresse_steht_in_der_pyproject(tmp_path: Path) -> None:
    """Die Adresse kommt aus `[project.urls]`, sonst gilt die Vorgabe."""
    assert repository_of(tmp_path) == REPOSITORY

    (tmp_path / "pyproject.toml").write_text(
        '[project.urls]\nRepository = "https://example.org/space"\n', encoding="utf-8"
    )
    assert repository_of(tmp_path) == "https://example.org/space"


def test_die_eigene_pyproject_nennt_das_repository() -> None:
    """Das ausgelieferte Projekt fragt am richtigen Ort nach."""
    assert repository_of(PROJECT_ROOT) == REPOSITORY


def test_git_fragt_nie_nach_einer_anmeldung() -> None:
    """Gespeicherte Anmeldungen bleiben aus -- das Repository ist oeffentlich."""
    runner = FakeRunner()
    latest_tag("https://example.org/space", run=runner)

    befehl = runner.commands[0]
    assert befehl[1:3] == ["-c", "credential.helper="]
    assert befehl[-4:] == ["ls-remote", "--tags", "--refs", "https://example.org/space"]


def test_git_wandelt_keine_zeilenenden_um(tmp_path: Path) -> None:
    """Mit `core.autocrlf=true` gingen sonst die PDFs beim Klonen kaputt."""
    runner = FakeRunner()
    fetch_package("https://example.org/space", "v0.10.0", tmp_path, run=runner)

    for befehl in (c for c in runner.commands if "clone" in c):
        stelle = befehl.index("core.autocrlf=false")
        assert befehl[stelle - 1] == "-c"


def test_ohne_tag_wird_das_gemeldet() -> None:
    """Ein Repository ohne Version ist ein Fehler, kein leeres Paket."""
    with pytest.raises(FetchFailed, match="keine Version"):
        latest_tag("https://example.org/space", run=FakeRunner(ls_remote=""))


def test_ohne_git_wird_das_gemeldet(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fehlt git, sagt die Meldung genau das."""
    monkeypatch.setattr("update_space.shutil.which", lambda name: None)

    with pytest.raises(FetchFailed, match="git ist auf diesem Rechner nicht"):
        latest_tag("https://example.org/space", run=FakeRunner())


def test_das_paket_entsteht_aus_dem_getaggten_stand(tmp_path: Path) -> None:
    """Geholt wird der Tag, dazu PyFoot in der Version, die er festlegt."""
    runner = FakeRunner()

    paket = fetch_package("https://example.org/space", "v0.10.0", tmp_path, run=runner)

    assert (paket / "main_space.py").read_text(encoding="utf-8") == "neu\n"
    klone = [c for c in runner.commands if "clone" in c]
    assert klone[0][-4:] == ["--branch", "v0.10.0", "https://example.org/space",
                             str(tmp_path / "pyfoot-space")]
    assert klone[1][-4:] == ["--branch", "v0.3.0", "https://example.org/pyfoot",
                             str((tmp_path / "pyfoot").resolve())]


def test_gebaut_wird_mit_den_werkzeugen_des_neuen_stands(tmp_path: Path) -> None:
    """Was ins Paket gehoert, bestimmt die neue Version, nicht die alte."""
    runner = FakeRunner()

    fetch_package("https://example.org/space", "v0.10.0", tmp_path, run=runner)

    werkzeuge = [Path(c[1]) for c in runner.commands if c[0] == sys.executable]
    neu = tmp_path / "pyfoot-space" / "tools"
    assert werkzeuge == [neu / "get_pyfoot.py", neu / "build_student_package.py"]


def test_ein_fehlendes_paket_wird_gemeldet(tmp_path: Path) -> None:
    """Baut das Werkzeug nichts, endet es mit einer Meldung."""
    with pytest.raises(FetchFailed, match="nicht gebaut"):
        fetch_package(
            "https://example.org/space", "v0.10.0", tmp_path, run=FakeRunner(build=False)
        )


def test_mit_der_neuesten_version_gibt_es_nichts_zu_tun(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Steht der neueste Tag schon im Manifest, wird nichts geholt."""
    monkeypatch.setattr(update_space, "_known_hashes", lambda project: ({}, "v0.10.0"))
    monkeypatch.setattr(update_space, "latest_tag", lambda repository: "v0.10.0")

    def nicht_holen(*args: object) -> Path:
        raise AssertionError("darf nicht geholt werden")

    monkeypatch.setattr(update_space, "fetch_package", nicht_holen)

    assert update_space.main(["--dry-run"]) == 0
    assert "schon die neueste Version (v0.10.0)" in capsys.readouterr().out


def test_ohne_netz_zeigt_es_den_weg_ueber_die_zip(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Geht GitHub nicht, nennt das Werkzeug den Grund und den anderen Weg."""

    def kein_netz(repository: str) -> str:
        raise FetchFailed("Could not resolve host: github.com")

    monkeypatch.setattr(update_space, "latest_tag", kein_netz)
    monkeypatch.setattr(update_space, "find_package", lambda: None)

    assert update_space.main(["--dry-run"]) == 1
    ausgabe = capsys.readouterr().out
    assert "Could not resolve host" in ausgabe
    assert "update_space.py C:" in ausgabe
