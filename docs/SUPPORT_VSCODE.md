# Installationsanleitung für den IT-Support: VS Code

<!-- ki-hinweis -->

## 1. Kurzfassung

<!-- cols: 40 22 18 20 kompakt -->

| Was | Version | Für wen | Adminrechte |
| --- | --- | --- | --- |
| VS Code (MNS+) | 1.105.0, mindestens 1.104 | alle | ja |
| Erweiterung Python (`ms-python.python`) | 2025.18.0 | alle | nein, siehe Abschnitt 3 |
| Erweiterung Pylance (`ms-python.vscode-pylance`) | 2025.10.2 | alle | nein, siehe Abschnitt 3 |
| Erweiterung Python Debugger (`ms-python.debugpy`) | 2025.16.0 | alle | nein, siehe Abschnitt 3 |
| Erweiterung Python Environments (`ms-python.vscode-python-envs`) | 1.12.0 | alle | nein, siehe Abschnitt 3 |
| Benutzereinstellungen (`settings.json`) | – | alle | siehe Abschnitt 4 |

**Pylance ist nicht optional.** Diese Erweiterung erzeugt die Warnungen, die
Schüler:innen beim Schreiben im Editor sehen. Ohne sie bleiben Typfehler
unbemerkt — deshalb bitte ausdrücklich prüfen (Abschnitt 5).

> **Hinweis:** Pylance darf lizenzrechtlich nur im offiziellen VS Code von
> Microsoft verwendet werden, nicht in VSCodium oder anderen Abwandlungen.

---

## 2. VS Code installieren (Adminrechte)

### Über MNS+ (empfohlen)

Das Paket **Visual Studio Code 1.105.0** zuweisen (Stand 19.11.2026). Auch
ein neueres MNS+-Paket passt, sofern es mindestens Version 1.104 ist. Ältere
Pakete wie 1.90.1 genügen **nicht**: Die Erweiterungen aus Abschnitt 3
brauchen 1.104, den Ordner für vorinstallierte Erweiterungen kennt VS Code
erst ab 1.96.

### Nur als Übergang: winget

Wenn es eilt und kein passendes MNS+-Paket da ist. Installiert den
**System Installer** (für alle Benutzer nach `C:\Program Files\Microsoft VS Code`)
in der aktuellen Version; die Erweiterungen aus Abschnitt 3 passen auch dazu.

```powershell
winget install --id Microsoft.VisualStudioCode --scope machine `
    --accept-package-agreements --accept-source-agreements
```

---

## 3. Erweiterungen für alle Benutzer vorinstallieren

Erweiterungen installiert VS Code je Benutzerprofil, nicht in den
Programmordner. Für eine zentrale Bereitstellung gibt es unter Windows einen
eigenen Weg:

1. Im Installationsordner einen Ordner `bootstrap\extensions` anlegen:
   `C:\Program Files\Microsoft VS Code\bootstrap\extensions`
2. Die vier Erweiterungen als VSIX-Datei dort ablegen (Links unten).
3. Startet ein Benutzer VS Code zum ersten Mal, installiert VS Code alle
   Dateien aus diesem Ordner still im Hintergrund in sein Profil — ohne
   Internet und ohne Adminrechte.

Werden Profile beim Abmelden zurückgesetzt, ist jeder Start ein „erster Start“;
die Erweiterungen werden dann jedes Mal aus dem lokalen Ordner nachinstalliert.
Das dauert ein bis zwei Minuten.

Beschreibung von Microsoft:
<https://code.visualstudio.com/docs/enterprise/extensions>

**Die VSIX-Dateien** (Windows x64, zueinander passende stabile Versionen). Sie
laufen mit **jedem VS Code ab 1.104**, also mit dem MNS+-Paket 1.105.0 und mit
neueren Versionen. Die Links laden die Datei direkt herunter:

- Python 2025.18.0:
  [ms-python.python-2025.18.0@win32-x64.vsix](https://marketplace.visualstudio.com/_apis/public/gallery/publishers/ms-python/vsextensions/python/2025.18.0/vspackage?targetPlatform=win32-x64)
- Pylance 2025.10.2:
  [ms-python.vscode-pylance-2025.10.2.vsix](https://marketplace.visualstudio.com/_apis/public/gallery/publishers/ms-python/vsextensions/vscode-pylance/2025.10.2/vspackage)
- Python Debugger 2025.16.0:
  [ms-python.debugpy-2025.16.0@win32-x64.vsix](https://marketplace.visualstudio.com/_apis/public/gallery/publishers/ms-python/vsextensions/debugpy/2025.16.0/vspackage?targetPlatform=win32-x64)
- Python Environments 1.12.0:
  [ms-python.vscode-python-envs-1.12.0@win32-x64.vsix](https://marketplace.visualstudio.com/_apis/public/gallery/publishers/ms-python/vsextensions/vscode-python-envs/1.12.0/vspackage?targetPlatform=win32-x64)

Alle vier werden gebraucht: Python bringt die anderen drei als Paket mit, lädt
sie ohne Internet aber nicht selbst nach. **Nur diese vier Dateien** in den
Ordner legen; neuere Versionen dort verlangen ein neueres VS Code, und VS Code
versucht dann beim Start, passende Versionen über den Proxy zu laden.

---

## 4. Benutzereinstellungen

Die Datei `settings.json` (liegt bei) schaltet die KI-Funktionen und die
Willkommensseite ab, stellt das helle Farbschema und Zoomen mit
*Strg + Mausrad* ein und verhindert Aktualisierungen und Online-Abfragen beim
Start (damit keine Proxy-Abfrage erscheint). Sie gehört in jedes Benutzerprofil:

```
C:\Users\<username>\AppData\Roaming\Code\User\settings.json
```

Da die Profile bei jedem Neustart zurückgesetzt werden, gehört sie in die
Vorlage, aus der die Profile neu entstehen (an derselben Stelle unter
`AppData\Roaming\Code\User`), oder wird per Anmeldeskript kopiert.

---

<!-- newpage -->

## 5. Prüfen

Mit einem **normalen Benutzerkonto** (z. B. einem Schülerkonto) anmelden,
VS Code starten und etwa eine Minute warten, bis die Erweiterungen installiert
sind (ein bis zwei Minuten). Dann auf einem der beiden Wege prüfen:

**Im Editor:** In VS Code *Strg + Umschalt + X* drücken. Links erscheint die
Liste der Erweiterungen; unter *Installiert* müssen Python, Pylance,
Python Debugger und Python Environments stehen.

**In einer Konsole:** Eingabeaufforderung oder PowerShell öffnen (Startmenü,
`cmd` eintippen) oder in VS Code *Terminal*, dann *Neues Terminal*. Dort
eingeben:

```bash
code --list-extensions
```

In der Ausgabe müssen diese vier Zeilen stehen:

```
ms-python.debugpy
ms-python.python
ms-python.vscode-pylance
ms-python.vscode-python-envs
```

Zum Schluss das Projekt öffnen (*Datei*, dann *Ordner öffnen*,
den Projektordner `SpaceProject` wählen), `main_editor.py` öffnen und oben rechts auf den
Play-Knopf klicken. Es muss sich das PyFoot-Fenster öffnen. Beim Start
darf keine Proxy-Abfrage und keine Willkommensseite mit Copilot erscheinen.

---

## 6. Python-Version in VS Code wählen

VS Code nimmt normalerweise das Python aus dem Suchpfad. Falls nicht:
*Strg + Umschalt + P*, dann *Python: Interpreter auswählen*, dann
**Python 3.13** wählen.

> **Häufige Stolperfalle:** VS Code legt manchmal ein leeres `.venv` an und
> wählt es aus. Dann fehlen dort **alle** Pakete, obwohl sie systemweit
> vorhanden sind — der Play-Knopf scheitert, das Terminal funktioniert. Entweder
> die Pakete in die Umgebung nachinstallieren oder das `.venv` löschen und eine
> andere Python-Version auswählen.
