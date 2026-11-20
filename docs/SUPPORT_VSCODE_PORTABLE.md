# Installationsanleitung für den IT-Support: VS Code ohne Adminrechte

<!-- ki-hinweis -->

Diese Anleitung ist **nur eine Rückfallebene**, wenn VS Code nicht
systemweit installiert werden kann. Der Regelfall steht in
`SUPPORT_VSCODE.md`; Python und die Pakete in `SUPPORT_PYTHON.md`.

**Pfadangaben:** `<VSCODE-ORDNER>` steht für den Ordner, in den VS Code
entpackt wurde, `<SPACE-ORDNER>` für den Arbeitsordner der Schüler:innen,
z. B. `C:\Schule\SpaceProject`.

---

## 1. Portables VS Code

VS Code gibt es als ZIP-Archiv, das sich in einen beliebigen Ordner entpacken
lässt und kein Installationsprogramm braucht. Der Ordner muss dem Benutzer
gehören, denn VS Code speichert dann Einstellungen und Erweiterungen darin —
`C:\Program Files` ist dafür **nicht** geeignet.

Eine solche Ausgabe kann ein eigenes Python mitbringen. Prüfen:

```bash
dir <VSCODE-ORDNER>\python\python.exe
```

Falls vorhanden, die Pakete direkt dorthin installieren:

```bash
<VSCODE-ORDNER>\python\python.exe -m pip install pygame mypy pytest markdown xhtml2pdf
```

Das gelingt ohne Adminrechte, weil der Ordner dem Benutzer gehört. Danach in
VS Code diese Python-Version auswählen: *Strg + Umschalt + P*, dann
*Python: Interpreter auswählen*, dann `<VSCODE-ORDNER>\python\python.exe`.

**Erweiterungen:** Die VSIX-Dateien aus `SUPPORT_VSCODE.md`, Abschnitt 3,
lassen sich einzeln installieren, auch ohne Internet:

```bash
<VSCODE-ORDNER>\bin\code.cmd --install-extension <Datei>.vsix
```

**Verteilung:** Der komplette VS-Code-Ordner lässt sich mitsamt Paketen und
Erweiterungen kopieren. Ein Arbeitsplatz ist damit ohne jede Installation
einsatzbereit.

> **Vorsicht bei zwei VS-Code-Installationen.** Ist zusätzlich eine normale
> Version vorhanden, verwenden beide getrennte Erweiterungen und getrennte
> Einstellungen. `code` im Suchpfad findet meist die installierte Version —
> nicht unbedingt die, mit der gearbeitet wird.

---

## 2. Wenn der Doppelklick keinen Editor öffnet

Ein Doppelklick auf eine Klasse soll ihre Datei öffnen — und zwar in dem
Editor, mit dem gerade gearbeitet wird. Für VS Code ruft PyFoot dafür
`code -r -g datei:zeile` auf; `-r` öffnet im **schon offenen Fenster**, statt
ein zweites aufzumachen. PyCharm bekommt `--line zeile datei`.

Gesucht wird der Reihe nach:

1. den Eintrag in `PYFOOT_EDITOR`
2. das VS Code, aus dessen Terminal gestartet wurde
3. PyCharm, wenn aus PyCharm heraus gestartet wurde
4. `code` im Suchpfad
5. die üblichen Orte einer VS-Code-Installation
6. ein installiertes PyCharm
7. die Standardanwendung des Systems für `.py`

**Ein aus dem ZIP entpacktes VS Code steht in keinem Suchpfad.** Wird es nicht
gefunden, trägt man es einmal ein:

```powershell
setx PYFOOT_EDITOR "<VSCODE-ORDNER>\bin\code.cmd"
```

`setx` schreibt die Angabe dauerhaft in das Benutzerprofil; **neue** Konsolen
kennen sie danach. Für die laufende Sitzung zusätzlich:

```powershell
$env:PYFOOT_EDITOR = "<VSCODE-ORDNER>\bin\code.cmd"
```

Prüfen, ob PyFoot etwas findet — der Befehl nennt den Fund oder `None`:

```powershell
python -c "from pyfoot.editor import source; print(source.find_editor())"
```

> `PYFOOT_EDITOR` nimmt jedes Programm an — Notepad++, Thonny, IDLE. Nur
> VS Code und PyCharm springen an die Zeile; andere Editoren öffnen die Datei
> am Anfang. Die Statuszeile nennt in jedem Fall Datei und Zeile.
