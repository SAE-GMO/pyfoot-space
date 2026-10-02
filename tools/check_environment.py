"""Prueft, was fuer PyFoot bereits vorhanden ist und was noch fehlt.

Das Skript meldet den Ist-Zustand und gibt anschliessend genau die Befehle
aus, die noch noetig sind -- passend dazu, ob Administratorrechte vorliegen
oder nicht. Fehlen Pflichtpakete, **bietet** es an, sie gleich zu
installieren; ohne ausdrueckliches "j" aendert es nichts. (An der Schule
installiert der IT-Support.)

Aufruf (im Projektordner):
    python tools\\check_environment.py

Ebenso aus dem Ordner `tools` heraus (`python check_environment.py`) oder in
VS Code ueber *Ausfuehren* -> *Ohne Debuggen ausfuehren*.

Es kommt bewusst ohne fremde Pakete aus und laeuft auch mit aelteren
Python-Versionen, damit es eine zu alte Version melden kann, statt daran zu
scheitern.
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import sysconfig
from typing import Callable

#: Der Projektordner, aus dem Ort dieser Datei bestimmt.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Beim Aufruf eines Skripts legt Python nur dessen Ordner in den Suchpfad --
# hier also 'tools'. Die mitgelieferte Bibliothek liegt aber eine Ebene hoeher.
# Ohne diese Zeile meldet die Pruefung 'pyfoot' faelschlich als fehlend.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# pygame gibt beim Einbinden eine Begruessung aus, die den Bericht
# unuebersichtlich macht.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
# Kein Fenster oeffnen: Die Pruefung soll auch ohne Bildschirm laufen.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

MINIMUM_PYTHON = (3, 11)

#: Ohne diese Pakete laeuft das Projekt nicht.
#: PyFoot wird nicht installiert, sondern liegt als Ordner im Projekt.
#: Geprueft wird trotzdem, ob es sich einbinden laesst -- sonst fehlt oder
#: klemmt die mitgelieferte Kopie.
REQUIRED_PACKAGES = [
    ("pyfoot", "pyfoot", "mitgelieferte Lernbibliothek (Ordner pyfoot)"),
    ("pygame", "pygame", "Grafikausgabe -- muss installiert sein"),
    ("mypy", "mypy", "Typpruefung auf der Konsole (tools\\check_code.py)"),
]

#: Diese Pakete braucht nur die Lehrkraft.
TEACHER_PACKAGES = [
    ("pytest", "pytest", "automatisierte Tests"),
    ("markdown", "markdown", "Arbeitsblaetter nach PDF umsetzen"),
    ("xhtml2pdf", "xhtml2pdf", "Arbeitsblaetter nach PDF umsetzen"),
]

OK = "[ OK   ]"
MISSING = "[FEHLT ]"
WARN = "[ !    ]"


def line(status: str, label: str, detail: str = "") -> None:
    """Gibt eine Ergebniszeile aus."""
    text = "{0} {1}".format(status, label)
    if detail:
        text = "{0:<52} {1}".format(text, detail)
    print(text)


def heading(text: str) -> None:
    """Gibt eine Abschnittsueberschrift aus."""
    print("")
    print(text)
    print("-" * len(text))


def check_python() -> bool:
    """Prueft die Python-Version."""
    version = sys.version_info
    found = "{0}.{1}.{2}".format(version[0], version[1], version[2])
    needed = "{0}.{1}".format(MINIMUM_PYTHON[0], MINIMUM_PYTHON[1])

    if version[:2] >= MINIMUM_PYTHON:
        line(OK, "Python " + found, "benoetigt: " + needed + " oder neuer")
        return True

    line(MISSING, "Python " + found, "zu alt, benoetigt: " + needed + " oder neuer")
    return False


def other_python_installations() -> list[str]:
    """Sucht weitere Python-Installationen auf dem Rechner.

    Sind mehrere vorhanden, ist die haeufigste Fehlerursache, dass der Editor
    eine andere auswaehlt als die Konsole -- dann fehlen dort die Pakete,
    obwohl sie installiert sind.
    """
    found: list[str] = []
    launcher = shutil.which("py")
    if launcher is None:
        return found

    try:
        result = subprocess.run(
            [launcher, "-0p"], capture_output=True, text=True, timeout=30, shell=True
        )
    except Exception:
        return found

    current = os.path.normcase(os.path.abspath(sys.executable))
    for row in result.stdout.splitlines():
        parts = row.split()
        for part in parts:
            if part.lower().endswith("python.exe"):
                path = part.strip('"')
                if os.path.normcase(os.path.abspath(path)) != current:
                    found.append(path)
    return found


def check_pip() -> bool:
    """Prueft, ob pip verfuegbar ist."""
    try:
        import pip  # noqa: F401
    except ImportError:
        line(MISSING, "pip", "Paketverwaltung fehlt")
        return False

    line(OK, "pip", "Paketverwaltung vorhanden")
    return True


def check_package(module_name: str, purpose: str) -> bool:
    """Prueft, ob ein Paket eingebunden werden kann."""
    try:
        importlib.import_module(module_name)
    except Exception:
        line(MISSING, module_name, purpose)
        return False

    line(OK, module_name, purpose)
    return True


def site_packages_writable() -> bool:
    """Prueft, ob ohne Adminrechte in die Paketablage geschrieben werden kann."""
    target = sysconfig.get_paths().get("purelib", "")
    return bool(target) and os.access(target, os.W_OK)


def in_virtual_environment() -> bool:
    """Prueft, ob gerade eine virtuelle Umgebung aktiv ist."""
    return sys.base_prefix != sys.prefix


def check_project_folder() -> bool:
    """Prueft, ob das Skript aus dem Projektordner heraus laeuft."""
    current = os.getcwd()
    expected = ["space", "tools"]
    missing = [name for name in expected if not os.path.isdir(os.path.join(current, name))]

    if not missing:
        line(OK, "Projektordner", current)
        return True

    # Rechtsklick auf `tools` -> "In integriertem Terminal oeffnen" landet hier.
    # Fuer diese Pruefung genuegt das; die Programme starten aber eine Ebene hoeher.
    tools = os.path.join(PROJECT_ROOT, "tools")
    if os.path.normcase(os.path.abspath(current)) == os.path.normcase(tools):
        line(OK, "Projektordner", PROJECT_ROOT)
        print("         Das Terminal steht im Ordner tools. Vor 'python main_editor.py'")
        print("         eine Ebene hoeher wechseln:  cd ..")
        return True

    line(WARN, "Projektordner", "fehlende Unterordner: " + ", ".join(missing))
    print("         Das Terminal steht vermutlich im falschen Ordner.")
    return False


#: Erweiterungen, die VS Code fuer den Kurs braucht.
#: Pylance liefert die Typwarnungen, die Schueler:innen waehrend des Schreibens
#: im Editor sehen. Ohne Pylance bleiben Typfehler unbemerkt -- deshalb wird es
#: hier eigens geprueft und nicht als selbstverstaendlich vorausgesetzt.
VSCODE_EXTENSIONS = [
    ("ms-python.python", "Python-Unterstuetzung"),
    ("ms-python.vscode-pylance", "Typwarnungen im Editor"),
]


def check_vscode() -> bool:
    """Prueft, ob VS Code samt der benoetigten Erweiterungen eingerichtet ist."""
    executable = shutil.which("code")
    if executable is None:
        line(WARN, "VS Code", "nicht im Suchpfad gefunden")
        return False

    line(OK, "VS Code", executable)

    try:
        result = subprocess.run(
            [executable, "--list-extensions"],
            capture_output=True,
            text=True,
            timeout=60,
            shell=True,
        )
    except Exception:
        line(WARN, "Erweiterungen", "liessen sich nicht pruefen")
        return False

    installed = result.stdout.lower()
    complete = True
    for extension, purpose in VSCODE_EXTENSIONS:
        if extension in installed:
            line(OK, extension, purpose)
        else:
            line(MISSING, extension, purpose)
            complete = False

    return complete


def pip_arguments(packages: list[str]) -> list[str]:
    """Die pip-Aufrufargumente fuer die vorliegende Umgebung (ohne `python`)."""
    user = [] if in_virtual_environment() or site_packages_writable() else ["--user"]
    return ["-m", "pip", "install", *user, *packages]


def pip_command(packages: list[str]) -> str:
    """Baut den passenden pip-Befehl zum Abtippen."""
    return " ".join(["python", *pip_arguments(packages)])


def offer_install(
    packages: list[str], ask: Callable[[str], str] = input
) -> bool:
    """Bietet an, fehlende Pakete gleich zu installieren.

    Gefragt wird nur, wenn jemand antworten kann -- also im Terminal, auch
    ueber *Ohne Debuggen ausfuehren* in VS Code. Installiert wird mit genau
    dem Python, das diese Pruefung ausfuehrt; so landen die Pakete dort, wo
    sie gebraucht werden, auch wenn mehrere Python-Versionen da sind.

    Returns:
        Ob installiert wurde und pip Erfolg gemeldet hat.
    """
    if sys.stdin is None or not sys.stdin.isatty():
        return False
    print("Nur auf dem eigenen Rechner -- an der Schule installiert der IT-Support.")
    try:
        antwort = ask("Soll ich sie jetzt installieren? [j/n] ").strip().lower()
    except EOFError:
        return False
    if antwort not in ("j", "ja", "y", "yes"):
        return False
    print("")
    result = subprocess.run([sys.executable, *pip_arguments(packages)])
    return result.returncode == 0


def offer_fetch_pyfoot(
    getter: str, ask: Callable[[str], str] = input
) -> bool:
    """Bietet an, PyFoot gleich zu holen (nur im Git-Repository noetig).

    Gefragt wird wie bei `offer_install` nur, wenn jemand antworten kann.

    Returns:
        Ob geholt wurde und das Werkzeug Erfolg gemeldet hat.
    """
    if sys.stdin is None or not sys.stdin.isatty():
        return False
    try:
        antwort = ask("Soll ich PyFoot jetzt holen? [j/n] ").strip().lower()
    except EOFError:
        return False
    if antwort not in ("j", "ja", "y", "yes"):
        return False
    print("")
    result = subprocess.run([sys.executable, getter])
    return result.returncode == 0


def main() -> int:
    """Fuehrt alle Pruefungen aus und meldet, was noch zu tun ist."""
    print("PyFoot -- Pruefung der Arbeitsumgebung")
    print("=" * 52)

    heading("Grundlagen")
    python_ok = check_python()
    line(OK, "verwendet wird", sys.executable)
    pip_ok = check_pip()
    check_project_folder()

    others = other_python_installations()
    if others:
        line(WARN, "weitere Python-Installationen", str(len(others)))
        for path in others:
            print(f"         {path}")
        print("         Achte darauf, dass VS Code dieselbe auswaehlt wie oben.")

    if in_virtual_environment():
        line(OK, "virtuelle Umgebung", sys.prefix)
    else:
        writable = "schreibbar" if site_packages_writable() else "nicht schreibbar"
        line(OK, "Paketablage", writable)

    heading("Pflichtpakete (Lehrkraft und Schueler:innen)")
    missing_required = []
    for package, module, purpose in REQUIRED_PACKAGES:
        if not check_package(module, purpose):
            missing_required.append(package)

    heading("Zusatzpakete (nur Lehrkraft)")
    missing_teacher = []
    for package, module, purpose in TEACHER_PACKAGES:
        if not check_package(module, purpose):
            missing_teacher.append(package)

    heading("Editor")
    editor_ok = check_vscode()

    heading("Ergebnis")

    if not editor_ok:
        print("Hinweis: Ohne die Erweiterung ms-python.vscode-pylance zeigt der")
        print("Editor keine Typwarnungen an. Siehe docs\\SUPPORT_INSTALLATION.md")
        print("(Installationsanleitung fuer den IT-Support), Abschnitt 5.")
        print("")

    if not python_ok:
        print("Python muss zuerst aktualisiert werden. Siehe")
        print("docs\\SUPPORT_INSTALLATION.md, Abschnitt 2.")
        return 1

    if not pip_ok:
        print("pip fehlt. Nachinstallieren mit:")
        print("")
        print("    python -m ensurepip --upgrade")
        return 1

    if not missing_required and not missing_teacher:
        print("Alles vorhanden. Es ist nichts zu tun.")
        return 0

    if "pyfoot" in missing_required:
        print("Die Bibliothek PyFoot fehlt oder ist unvollstaendig.")
        print("Sie gehoert als Ordner 'pyfoot' in diesen Projektordner.")
        getter = os.path.join(PROJECT_ROOT, "tools", "get_pyfoot.py")
        if os.path.isfile(getter):
            # Aus dem Git-Repository: Dort liegt PyFoot nicht bei, sondern
            # wird in der festgelegten Version geholt.
            print("Holen laesst sie sich mit:")
            print(r"    python tools\get_pyfoot.py")
            print("")
            if offer_fetch_pyfoot(getter):
                print("")
                print("Geholt. Die Pruefung laeuft noch einmal:")
                return subprocess.call([sys.executable, os.path.abspath(__file__)])
        else:
            # Im Schuelerpaket ist sie immer dabei; fehlt sie, ist das Paket
            # unvollstaendig entpackt.
            print("Das Paket ist vermutlich unvollstaendig entpackt. Bitte die")
            print("ZIP-Datei noch einmal vollstaendig entpacken.")
        print("")
        missing_required = [p for p in missing_required if p != "pyfoot"]
        if not missing_required:
            return 1

    if missing_required and in_virtual_environment():
        print("Du arbeitest in einer virtuellen Umgebung:")
        print(f"    {sys.prefix}")
        print("Dort fehlen Pakete, die es ausserhalb vielleicht schon gibt.")
        print("Entweder hier nachinstallieren (siehe unten) -- oder in VS Code")
        print("eine andere Python-Version waehlen:")
        print("    Strg + Umschalt + P  ->  'Python: Interpreter auswaehlen'")
        print("")

    if missing_required:
        if other_python_installations():
            print("Achtung: Auf diesem Rechner gibt es mehrere Python-Versionen.")
            print("Fehlt ein Paket nur im Editor, aber nicht in der Konsole, hat")
            print("VS Code die falsche ausgewaehlt. Umstellen mit:")
            print("    Strg + Umschalt + P  ->  'Python: Interpreter auswaehlen'")
            print(f"    und diese hier waehlen: {sys.executable}")
            print("")

        print("Fehlende Pflichtpakete:")
        print("")
        print("    " + pip_command(missing_required))
        print("")
        if offer_install(missing_required):
            # Frisch installierte Pakete findet dieser Lauf nicht zuverlaessig
            # (der Ordner fuer --user kann eben erst entstanden sein). Deshalb
            # prueft ein neuer Lauf.
            print("")
            print("Installiert. Die Pruefung laeuft noch einmal:")
            return subprocess.call([sys.executable, os.path.abspath(__file__)])

    if missing_teacher:
        print("Fehlende Zusatzpakete (nur fuer die Lehrkraft noetig):")
        print("")
        print("    " + pip_command(missing_teacher))
        print("")

    print("Danach diese Pruefung erneut ausfuehren.")
    return 1 if missing_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
