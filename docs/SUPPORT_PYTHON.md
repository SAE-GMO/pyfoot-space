# Installationsanleitung für den IT-Support: Python

<!-- ki-hinweis -->

Diese Anleitung richtet sich an die Systembetreuung. Lehrkräfte und
Schüler:innen haben keine lokalen Administratorrechte. Sie beschreibt Python
und die Python-Pakete. Die Einrichtung des Editors steht in
`SUPPORT_VSCODE.md`.

**Was verteilt wird:** der Ordner `SpaceProject` aus dem Paket `SpaceProject.zip`. Er ist der
Arbeitsordner der Schüler:innen und enthält die Bibliothek PyFoot bereits. Das
Paket bekommen Sie von der Lehrkraft; die neueste öffentliche Fassung liegt
unter <https://github.com/SAE-GMO/pyfoot-space/releases> (oberster Eintrag,
Datei `SpaceProject.zip`).

**Pfadangaben:** `<SPACE-ORDNER>` steht für den Ordner, in den das Paket
entpackt wurde, z. B. `C:\Schule\SpaceProject`. Relative Pfade gelten ab dort:
`tools\check_environment.py` ist also `C:\Schule\SpaceProject\tools\check_environment.py`.

---

## 1. Kurzfassung

<!-- cols: 36 20 16 28 kompakt -->

| Was | Version | Für wen | Adminrechte |
| --- | --- | --- | --- |
| Python | 3.11 oder neuer | alle | ja, für systemweite Installation |
| Paket `pygame` | 2.5 oder neuer | alle | ja, für systemweite Installation |
| Paket `mypy` | aktuell | alle | ja, für systemweite Installation |
| Pakete `pytest`, `markdown`, `xhtml2pdf` | aktuell | nur Lehrkräfte | ja |

**mypy wird auf allen Arbeitsplätzen gebraucht.** Es liefert dieselben
Hinweise wie der Editor, nur auf der Konsole — Schüler:innen rufen es über
`python tools\check_code.py` auf. Auf Rechnern von Lehrkräften dient es
zusätzlich der Qualitätssicherung des Projekts selbst.

**PyFoot wird NICHT installiert.** Die Lernbibliothek liegt als Ordner
`pyfoot\` im Arbeitsordner `SpaceProject` und wird mit ihm verteilt. Das ist Absicht:
Die Bibliothek wird im Laufe des Schuljahres weiterentwickelt, und jede
Änderung soll ohne Zutun des Supports möglich sein — es genügt, den Ordner
`SpaceProject` auszutauschen.

**Nicht nötig:** Der Ordner `SpaceProject` wird **nicht** installiert. Er läuft direkt,
sobald Python, `pygame` und `mypy` vorhanden sind. Es sind keine
Systemdienste, keine Registry-Einträge und keine Umgebungsvariablen außer dem
PATH-Eintrag von Python erforderlich.

**Kein Internetzugang der Endgeräte nötig,** wenn nach Abschnitt 5 offline
installiert wird.

---

## 2. Vorher prüfen: Was fehlt überhaupt?

Vor jeder Installation feststellen, was bereits vorhanden ist. Das Skript ändert
nichts, es meldet nur den Zustand und nennt anschließend genau die noch nötigen
Befehle.

```bash
cd <SPACE-ORDNER>
```

```bash
python tools\check_environment.py
```

Ist Python noch gar nicht installiert, schlägt bereits der Aufruf fehl — dann
mit Abschnitt 3 beginnen.

Das Skript endet mit Rückgabewert `0`, wenn alles Nötige vorhanden ist, sonst
mit `1`. Es lässt sich damit auch in Verteilungsskripte einbinden.

---

## 3. Python installieren (Adminrechte)

### Über die Softwareverteilung der Schule

Ist Python 3.11 oder neuer in MNS+ paketiert, genügt die neueste dort
paketierte Version. Wichtig ist nur der PATH-Eintrag (siehe unten).

### Über winget, systemweit

```powershell
winget install --id Python.Python.3.13 --scope machine `
    --accept-package-agreements --accept-source-agreements
```

### Mit der Installationsdatei, unbeaufsichtigt

Herunterladen von <https://www.python.org/downloads/windows/>
(Datei `python-3.13.x-amd64.exe`), dann:

```powershell
.\python-3.13.x-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 `
    Include_pip=1 Include_test=0
```

Bedeutung der Schalter:

<!-- cols: 30 70 kompakt -->

| Schalter | Wirkung |
| --- | --- |
| `InstallAllUsers=1` | systemweit nach `C:\Program Files\Python313` |
| `PrependPath=1` | trägt Python in den PATH ein — **wichtig**, sonst findet die Konsole `python` nicht |
| `Include_pip=1` | installiert die Paketverwaltung mit |
| `Include_test=0` | spart die Testsuite von Python selbst |

### PATH prüfen

Nach der Installation eine **neue** Konsole öffnen und prüfen:

```bash
python --version
```

Erwartet wird `Python 3.11.x` oder neuer. Erscheint stattdessen der
Microsoft-Store oder eine Fehlermeldung, fehlt der PATH-Eintrag. Dann manuell
ergänzen (Adminrechte, systemweit):

```bash
setx /M PATH "%PATH%;C:\Program Files\Python313;C:\Program Files\Python313\Scripts"
```

Anschließend alle Konsolen und den Editor neu starten.

> **Hinweis zum Microsoft Store:** Windows 11 bringt einen Platzhalter mit, der
> beim Aufruf von `python` den Store öffnet. Er lässt sich abschalten unter
> *Einstellungen*, dann *Apps*, dann *Erweiterte App-Einstellungen*, dann
> *App-Ausführungsaliase*; dort `python.exe` und `python3.exe` deaktivieren.

---

## 4. Pakete installieren (Adminrechte)

Systemweit installieren, damit Lehrkräfte und Schüler:innen nichts weiter tun
müssen. Konsole **als Administrator** öffnen.

Pflicht für alle Arbeitsplätze:

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install pygame mypy
```

Zusätzlich nur auf Rechnern von Lehrkräften:

```bash
python -m pip install pytest markdown xhtml2pdf
```

Prüfen:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

---

## 5. Ohne Internetzugang der Endgeräte

Auf einem Rechner **mit** Internetzugang und gleicher Windows- und
Python-Version die Pakete einmalig herunterladen:

```bash
python -m pip download pygame mypy pytest markdown xhtml2pdf -d D:\pyfoot_pakete
```

Den Ordner auf die Zielrechner kopieren, dort installieren:

```bash
python -m pip install --no-index --find-links D:\pyfoot_pakete pygame mypy
```

---

## 6. Falls keine Adminrechte verfügbar sind

Diese Wege funktionieren im Benutzerkontext, sind aber **nur Rückfallebene**.
Für den Regelbetrieb ist die systemweite Installation nach Abschnitt 3 und 4
vorzuziehen, weil sonst jedes Benutzerprofil eigene Kopien anlegt.

### Python im Benutzerkontext

```powershell
winget install --id Python.Python.3.13 --scope user `
    --accept-package-agreements --accept-source-agreements
```

### Pakete im Benutzerkontext

```bash
python -m pip install --user pygame mypy
```

Die Pakete landen unter `%APPDATA%\Python\Python313\site-packages`. Bei
servergespeicherten Profilen erhöht das die Profilgröße — bitte einplanen.

### Virtuelle Umgebung im Projektordner

Sauberste Lösung ohne Adminrechte, aber je Kopie des Projekts einmal nötig:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
python -m pip install pygame mypy
```

Der Editor erkennt `.venv` im Projektordner selbstständig und bietet sie zur
Auswahl an (siehe `SUPPORT_VSCODE.md`).

---

## 7. Abnahme

Auf einem eingerichteten Arbeitsplatz mit einem **normalen Benutzerkonto**
prüfen:

```bash
cd <SPACE-ORDNER>
```

```bash
python tools\check_environment.py
```

Alle Pflichtpakete müssen `[ OK ]` melden. Danach der eigentliche Funktionstest:

```bash
python main_space.py
```

Es muss sich ein Fenster öffnen, in dem ein Raumschiff über ein Gitter fliegt.
Schließen mit `Esc`. Damit ist der Arbeitsplatz einsatzbereit.

---

## 8. Häufige Störungen

<!-- cols: 25 23 52 kompakt -->

| Symptom | Ursache | Abhilfe |
| --- | --- | --- |
| `python` öffnet den Microsoft Store | App-Ausführungsalias aktiv | siehe Hinweis in Abschnitt 3 |
| `'python' is not recognized` | PATH-Eintrag fehlt | Abschnitt 3, „PATH prüfen" |
| `ModuleNotFoundError:`<br>`No module named 'pygame'` | Paket fehlt oder in anderem Python installiert | `python -m pip install pygame` mit **demselben** `python` wie im Fehler |
| `ModuleNotFoundError:`<br>`No module named 'pyfoot'` | der mitgelieferte Ordner `pyfoot\` fehlt im Arbeitsordner | Ordner `SpaceProject` vollständig neu verteilen |
| `ModuleNotFoundError:`<br>`No module named 'space'` | Konsole steht im falschen Ordner | `cd` in den Projektordner |
| `ModuleNotFoundError:`<br>`No module named 'space'`, obwohl der Ordner da ist | **der Unterordner heißt `Space` statt `space`.** Beim Entpacken oder Verschieben schreibt Windows Ordnernamen mitunter groß. Der Dateidienst ist zwar groß-klein-blind, Python prüft die Schreibung aber genau | Unterordner in Kleinbuchstaben umbenennen — siehe Hinweis unter der Tabelle |
| PowerShell fragt „Führen Sie ausschließlich vertrauenswürdige Skripts aus" | Zonenmarkierung heruntergeladener Dateien | ohne Adminrechte:<br>`Unblock-File -Path "<Pfad aus der Warnung>"` |
| mypy meldet `Duplicate module named "__main__"` | Konsole steht im falschen Ordner; mypy meldet das irreführend | `cd` in den Projektordner, oder `python tools\check_project.py` verwenden — das funktioniert von überall |
| Mehrere Python-Versionen parallel | verschiedene Installationen | zeigt die genutzte Installation:<br>`python -c "import sys; print(sys.executable)"` |
| Fenster öffnet sich nicht, Fehler zu SDL | Grafiktreiber oder Sitzung ohne Bildschirm | auf einem Arbeitsplatz mit Bildschirm testen |

Störungen, die nur im Editor auftreten (Play-Knopf, Doppelklick auf eine
Klasse), stehen in `SUPPORT_VSCODE.md`.

### Wenn ein Ordner plötzlich großgeschrieben ist

Der Paketordner `space` ist kleingeschrieben. Beim Entpacken und Verschieben
kann Windows daraus `Space` machen — vor allem, wenn ein Ordner gleichen
Namens darüber liegt. Deshalb heißt der Projektordner seit November 2026
`SpaceProject`; ältere Pakete hießen noch `Space`. Sichtbar ändert
sich fast nichts, und der Dateidienst stört sich nicht daran; **Python schon.**
Die Meldung nennt dann nur das fehlende Modul, nicht den Grund.

So sieht man die tatsächliche Schreibung:

```powershell
Get-ChildItem -Directory | Select-Object Name
```

Umbenennen geht **nicht in einem Schritt**: Der direkte Versuch scheitert mit
„Der Quell- und der Zielpfad dürfen nicht identisch sein", weil Windows
`Space` und `space` für denselben Namen hält. Es braucht einen Zwischenschritt:

```powershell
Rename-Item Space -NewName zwischenschritt; Rename-Item zwischenschritt -NewName space
```

Danach zeigt `Get-ChildItem -Directory` den Namen klein. Denselben Weg gibt es
für `ships`, `levels` und `pyfoot` — alle vier sind kleingeschrieben, nur der
Projektordner darüber heißt `SpaceProject`.
