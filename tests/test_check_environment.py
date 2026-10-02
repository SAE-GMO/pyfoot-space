"""Tests fuer die Pruefung der Arbeitsumgebung."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import check_environment as env  # noqa: E402


def test_vorhandenes_paket_wird_erkannt() -> None:
    assert env.check_package("json", "Standardbibliothek") is True


def test_fehlendes_paket_wird_erkannt() -> None:
    assert env.check_package("gibt_es_nicht_12345", "Testfall") is False


def test_pip_befehl_ohne_adminrechte_nutzt_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(env, "in_virtual_environment", lambda: False)
    monkeypatch.setattr(env, "site_packages_writable", lambda: False)

    assert env.pip_command(["pygame"]) == "python -m pip install --user pygame"


def test_pip_befehl_mit_schreibrecht_ohne_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(env, "in_virtual_environment", lambda: False)
    monkeypatch.setattr(env, "site_packages_writable", lambda: True)

    assert env.pip_command(["pygame"]) == "python -m pip install pygame"


def test_pip_befehl_in_virtueller_umgebung_ohne_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(env, "in_virtual_environment", lambda: True)
    monkeypatch.setattr(env, "site_packages_writable", lambda: False)

    assert env.pip_command(["a", "b"]) == "python -m pip install a b"


class _Terminal:
    """Ein Terminal, in dem jemand antworten kann."""

    @staticmethod
    def isatty() -> bool:
        return True


def test_installiert_wird_nur_nach_ja(monkeypatch: pytest.MonkeyPatch) -> None:
    aufrufe: list[list[str]] = []
    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(subprocess, "run", lambda args: aufrufe.append(args))

    assert env.offer_install(["pygame"], ask=lambda _frage: "n") is False
    assert aufrufe == []


def test_nach_ja_installiert_dasselbe_python(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mit dem Python, das die Pruefung ausfuehrt -- nicht mit irgendeinem."""
    aufrufe: list[list[str]] = []

    class Ergebnis:
        returncode = 0

    def run(args: list[str]) -> Ergebnis:
        aufrufe.append(args)
        return Ergebnis()

    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(env, "in_virtual_environment", lambda: False)
    monkeypatch.setattr(env, "site_packages_writable", lambda: False)

    assert env.offer_install(["pygame", "mypy"], ask=lambda _frage: "j") is True
    assert aufrufe == [[sys.executable, "-m", "pip", "install", "--user", "pygame", "mypy"]]


def test_ohne_terminal_wird_nicht_gefragt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Etwa unter pytest oder in einer Ausgabe ohne Eingabe: kein Warten."""

    def fragen(_frage: str) -> str:
        raise AssertionError("haette nicht fragen duerfen")

    monkeypatch.setattr(sys, "stdin", None)

    assert env.offer_install(["pygame"], ask=fragen) is False


def test_pyfoot_wird_nur_nach_ja_geholt(monkeypatch: pytest.MonkeyPatch) -> None:
    aufrufe: list[list[str]] = []
    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(subprocess, "run", lambda args: aufrufe.append(args))

    assert env.offer_fetch_pyfoot("get_pyfoot.py", ask=lambda _frage: "n") is False
    assert aufrufe == []


def test_nach_ja_wird_pyfoot_mit_demselben_python_geholt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aufrufe: list[list[str]] = []

    class Ergebnis:
        returncode = 0

    def run(args: list[str]) -> Ergebnis:
        aufrufe.append(args)
        return Ergebnis()

    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(subprocess, "run", run)

    assert env.offer_fetch_pyfoot("get_pyfoot.py", ask=lambda _frage: "j") is True
    assert aufrufe == [[sys.executable, "get_pyfoot.py"]]


def test_pyfoot_holen_fragt_nicht_ohne_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    def fragen(_frage: str) -> str:
        raise AssertionError("haette nicht fragen duerfen")

    monkeypatch.setattr(sys, "stdin", None)

    assert env.offer_fetch_pyfoot("get_pyfoot.py", ask=fragen) is False


def test_der_ordner_tools_gilt_als_projektordner(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Rechtsklick auf `tools` -> 'In integriertem Terminal oeffnen' (HA01)."""
    monkeypatch.chdir(Path(env.PROJECT_ROOT) / "tools")

    assert env.check_project_folder() is True
    assert "cd .." in capsys.readouterr().out


def test_mindestversion_passt_zum_projekt() -> None:
    """Die geforderte Version muss zu pyproject.toml passen."""
    pyproject = (
        Path(__file__).resolve().parent.parent / "pyproject.toml"
    ).read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in pyproject
    assert env.MINIMUM_PYTHON == (3, 11)


def test_pflichtpakete_sind_vollstaendig() -> None:
    """PyFoot als Bibliothek, pygame fuer die Anzeige, mypy fuer die Typpruefung."""
    namen = sorted(paket for paket, _modul, _zweck in env.REQUIRED_PACKAGES)
    assert namen == ["mypy", "pyfoot", "pygame"]


def test_pyfoot_ist_pflicht() -> None:
    """Space importiert PyFoot als Bibliothek -- ohne sie laeuft nichts."""
    namen = [paket for paket, _modul, _zweck in env.REQUIRED_PACKAGES]
    assert "pyfoot" in namen


def test_lehrkraftpakete_sind_vollstaendig() -> None:
    namen = sorted(paket for paket, _modul, _zweck in env.TEACHER_PACKAGES)
    assert namen == ["markdown", "pytest", "xhtml2pdf"]


def test_pylance_wird_geprueft() -> None:
    """Pylance liefert die Warnungen im Editor und darf nicht fehlen."""
    namen = [erweiterung for erweiterung, _zweck in env.VSCODE_EXTENSIONS]
    assert "ms-python.vscode-pylance" in namen
    assert "ms-python.python" in namen


def test_projektordner_liegt_im_suchpfad() -> None:
    """Sonst faende die Pruefung die mitgelieferte Bibliothek nicht.

    Beim Aufruf eines Skripts legt Python nur dessen Ordner in den Suchpfad --
    hier 'tools'. Die Bibliothek liegt aber eine Ebene hoeher.
    """
    assert env.PROJECT_ROOT in sys.path


def test_mitgelieferte_bibliothek_wird_gefunden() -> None:
    """Der Aufruf aus `tools` heraus muss pyfoot finden koennen."""
    assert env.check_package("pyfoot", "Testfall") is True


def test_weitere_python_installationen_werden_erkannt() -> None:
    """Mehrere Python-Versionen sind die haeufigste Ursache dafuer, dass es
    in der Konsole laeuft, ueber den Play-Knopf aber nicht."""
    weitere = env.other_python_installations()
    assert isinstance(weitere, list)
    assert sys.executable not in weitere


def test_keine_syntaxwarnungen_im_skript() -> None:
    """Escape-Fehler in Pfadangaben faellen sonst erst beim Aufruf auf."""
    import warnings

    quelle = Path(env.__file__).read_text(encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        compile(quelle, env.__file__, "exec")
