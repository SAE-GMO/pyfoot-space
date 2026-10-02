# Space — das Basisprojekt des Kurses

Raumschiffe, PowerUps und Asteroiden auf einem Gitter. **Dies ist der Ordner, in
dem im Unterricht gearbeitet wird.**

> Dies ist **Teil 2 von drei**. Teil 1 ist die Bibliothek
> [pyfoot](https://github.com/SAE-GMO/pyfoot), Teil 3 die Kursdokumentation mit
> Arbeitsblaettern und Musterloesungen. Sie ist privat; Lehrkraefte bekommen
> Zugang auf Anfrage (siehe unten).

## Fuer den Unterricht: das fertige Paket

Wer nur unterrichten oder lernen will, braucht dieses Repository nicht zu
klonen. Unter **Releases** liegt `Space.zip`: entpacken, fertig -- die
Bibliothek PyFoot ist darin enthalten.

Pfade in dieser Datei gelten ab dem Projektordner: `tools\check_environment.py`
meint die Datei `check_environment.py` im Ordner `tools` darin, egal wo der
Ordner liegt.

## Schnellstart

```bash
python tools\check_environment.py
```

Meldet die Pruefung etwas als fehlend, wende dich an den IT-Support. Sonst:

```bash
python main_space.py
```

Es oeffnet sich ein Fenster, in dem ein Raumschiff losfliegt. Schliessen mit
`Esc`.

**Die ausfuehrliche Anleitung steht in `docs/ANLEITUNG.md`**, die
Installationsanleitung fuer den IT-Support in `docs/SUPPORT_INSTALLATION.md`
(beide auch als PDF).

## PyFoot ist mitgeliefert, nicht installiert

Im Paket liegt die Bibliothek als Ordner `pyfoot\` im Projekt. Damit laeuft
alles ohne Installation -- an der Schule hat niemand Administratorrechte, und
jede nachtraegliche Aenderung an einem installierten Paket muesste der
IT-Support vornehmen.

```python
from pyfoot import run, set_world
```

**Im Repository liegt der Ordner nicht.** Welche Version gebraucht wird,
steht in `pyproject.toml` unter `[tool.sae-gmo.pyfoot]`. Nach dem Klonen
holt sie dieser Befehl von GitHub:

```bash
python tools\get_pyfoot.py
```

Wer an PyFoot selbst arbeitet und es als Nachbarordner neben diesem Projekt
liegen hat, uebernimmt dessen Stand mit `--local`. Wo der Nachbarordner
liegt, steht an genau einer Stelle: `pyproject.toml`, Abschnitt
`[tool.sae-gmo.neighbours]`. Ein Test meldet, wenn die Kopie nicht die
festgelegte Version hat. `tools\check_environment.py` bietet an, sie zu
holen, wenn sie fehlt.

**Bewusst kein ZIP-Archiv:** Aus einem Archiv koennen weder mypy noch Pylance
die Typangaben lesen. Die Typpruefung meldete dann faelschlich "keine Fehler",
statt die vorhandenen zu zeigen -- gemessen und deshalb verworfen.

Installiert werden muessen nur `pygame` und `mypy`; beides einmalig durch den
IT-Support (siehe `docs/SUPPORT_INSTALLATION.md`).

## Eine Aufgabe loesen

Gearbeitet wird in der Oberflaeche:

```bash
python main_editor.py
```

Die Anweisungen kommen in `ships\normal_spaceship.py`:

```python
class NormalSpaceship(Spaceship):
    __slots__ = ()

    def init(self) -> None:
        self.move()
        self.drop_power_up()
        self.move()
        self.turn_left()
```

Die Welt wechselt man per Rechtsklick im Klassenbaum. `main_space.py` zeigt
dieselbe Welt ohne Oberflaeche -- die Kommandozeile bleibt vollwertig.

Nach einer Aenderung muss die Oberflaeche nicht neu gestartet werden:
speichern, im Fenster `R` druecken, Start. Zuruecksetzen liest geaenderte
Dateien aus `ships\` und `levels\` neu ein.

Geht etwas schief -- das Raumschiff fliegt aus der Welt, ein Name ist
vertippt --, haelt das Programm an und zeigt ein Fehlerfenster. `E` springt
in VS Code an die Zeile, `R` setzt zurueck, `Esc` schliesst das Fenster.

## Aufbau

| Ordner | Inhalt | |
| --- | --- | --- |
| `ships/` | selbst geschriebene Akteure, darunter `normal_spaceship.py` | **den Schueler:innen** |
| `levels/` | **alle Welten** -- je eine Datei, dazu selbst geschriebene | **den Schueler:innen** |
| `space/actors/` | Spaceship, SensorSpaceship, PowerUp, Asteroid, Hinweisfenster | vorgegeben |
| `space/worlds/` | Weltraumwelt und die Grundklasse `StartWorld` | vorgegeben |
| `space/assets/` | Grafiken und das Skript, das sie erzeugt | vorgegeben |
| `pyfoot/` | mitgelieferte Bibliothek -- **Kopie, hier nichts aendern**; im Repository nicht enthalten, siehe oben | vorgegeben |
| `docs/` | Anleitung und Installationsanleitung, je als Markdown und PDF | alle |
| `tools/` | Pruefwerkzeuge | |
| `tests/` | automatisierte Tests des Projekts | **nicht im Schuelerpaket** |

Die Oberflaeche legt neue Klassen in `ships/` beziehungsweise `levels/` ab --
getrennt vom Kursinhalt, damit sich beides nicht vermischt.

`ships/normal_spaceship.py` ist mitgeliefert und zugleich die Einstiegsdatei:
Die ersten Anweisungen des Kurses werden dort hineingeschrieben. Damit ein
Fehler darin nicht das ganze Projekt lahmlegt, bindet `space/` diese Datei
**nicht** beim Start ein, sondern erst, wenn eine Welt ihr Raumschiff baut.

## Das Paket fuer die Schueler:innen

Dieser Ordner ist das Projekt der **Lehrkraft**. Was in den Unterricht geht,
baut dieses Werkzeug:

```bash
python tools\build_student_package.py
```

Es legt `dist\Space.zip` an -- mit `pyfoot/` in der festgelegten Version
(fehlt es, wird es vorher geholt), `space/`, `ships/`, `levels/`, `docs/`,
den beiden Startdateien, den Lizenzhinweisen und den Werkzeugen, die in der
Anleitung stehen. **Ohne `tests/`** und ohne die Werkzeuge der Lehrkraft.
Die Musterloesungen liegen ohnehin nicht in diesem Repository.

Gepackt wird nach einer Erlaubnisliste, nicht nach einer Ausschlussliste: Was
spaeter dazukommt, geht nicht versehentlich mit. Ein Test prueft, dass keine
Loesung im Paket landet.

## Eine neue Version ausliefern

Jedes Paket traegt ein Manifest `tools\paket.json`: Version und eine
Pruefsumme je Datei. Damit frischen die Schueler:innen ihr Projekt auf, ohne
ihre Arbeit zu verlieren:

```bash
python tools\update_space.py --dry-run
```

**Woher die neue Version kommt.** Ohne Pfad fragt das Werkzeug per `git`
nach dem neuesten Versions-Tag dieses Repositorys (Adresse aus
`pyproject.toml`, `[project.urls]`), klont diesen Stand und die PyFoot-Version,
die er festlegt, in einen temporaeren Ordner und baut daraus das Paket -- mit
`build_student_package.py` aus genau diesem Stand. Das Ergebnis gleicht dem
Release; im Manifest steht dann der Tag als Version. Das Repository ist
oeffentlich, `git` fragt nicht nach einer Anmeldung. Ohne `git` oder Netz
nennt das Werkzeug den Grund; dann geht es mit einer heruntergeladenen
`Space.zip` als Pfad.

Eine neue Version erreicht die Schueler:innen also, sobald ihr Tag auf GitHub
steht (siehe „Automatische Pruefung und Release").

Verglichen wird jede Datei mit dem Stand, der **zuletzt ausgeliefert** wurde:

| Fall | Was geschieht |
| --- | --- |
| Datei fehlt | wird angelegt |
| Datei unveraendert | wird ersetzt |
| Datei veraendert | bleibt; die neue Version landet daneben als `name.py.neu` |
| Datei nur im Projekt | bleibt unberuehrt -- eigene Schiffe und Welten |
| Datei nicht mehr im Paket | wird gemeldet, nicht geloescht |

`ships\__init__.py` und `levels\__init__.py` enthalten Mitgeliefertes **und**
Eigenes. Sie werden zusammengefuehrt: Grundlage ist die neue Datei -- dort
stimmt die Reihenfolge, eine Grundklasse steht vor ihren Unterklassen --, die
eigenen Eintraege kommen dahinter.

Die neue Version heisst `name.py.neu` und nicht `name.neu.py`. Mit der Endung
`.py` stuende sie im Klassenbaum und mypy pruefte sie mit.

Vor jeder Aenderung legt das Werkzeug ein Backup des ganzen Projekts unter
`backup\` ab.

## Automatische Pruefung und Release

**Bei jedem Push** holt GitHub die festgelegte PyFoot-Version und laesst
Tests und Typpruefung laufen (`.github/workflows/tests.yml`, Windows,
Python 3.11 und 3.13). Der Haken am Commit zeigt das Ergebnis.

**Bei jedem neuen Tag** `v<version>` baut GitHub `Space.zip` und haengt es an
das Release (`.github/workflows/release.yml`). Vorher prueft es, dass der Tag
zur `version` in `pyproject.toml` passt, und laesst alle Tests laufen; schlaegt
etwas fehl, entsteht kein Release. Eine neue Version heisst also:

1. `version` in `pyproject.toml` erhoehen, committen, pushen,
2. `git tag -a v0.2.0 -m "Space 0.2.0"`,
3. `git push origin v0.2.0`.

## Werkzeuge

```bash
python tools\check_environment.py
```

```bash
python tools\check_code.py
```

```bash
python tools\check_project.py
```

```bash
python -m pytest
```

Die Skripte unter `tools\` finden das Projekt selbst und lassen sich aus jedem
Verzeichnis aufrufen.

## Grafiken neu erzeugen

```bash
python space\assets\generate_assets.py
```

Alle vier Grafiken entstehen aus geometrischen Grundformen. Es werden keine
fremden Vorlagen verwendet.

## Bewusst nicht vorhanden

Einige Methoden fehlen absichtlich, weil ihre Umsetzung Gegenstand einer Aufgabe
ist -- etwa `turn_right()` sowie `is_asteroid_left()` und
`is_asteroid_right()`. Tests sichern ab, dass sie nicht versehentlich ergaenzt
werden.

Ebenso bewusst: `space/assets/generate_assets.py` bindet pygame direkt ein. Das
Skript laeuft nicht zur Laufzeit, sondern erzeugt einmalig Bilddateien; PyFoot
bietet dafuer bewusst keine Zeichen-Schnittstelle.

## Arbeitsblaetter und Musterloesungen

Die Arbeitsblaetter des Kurses liegen mit den Musterloesungen in einem
privaten Repository. Lehrkraefte, die sie im eigenen Unterricht nutzen
moechten, melden sich ueber ein
[Issue](https://github.com/SAE-GMO/pyfoot-space/issues) in diesem Repository.
Die Musterloesungen sind bewusst nicht oeffentlich, damit Schueler:innen sie
nicht vorab finden.

## Abhaengigkeiten

| Paket | Wofuer | Lizenz |
| --- | --- | --- |
| [pygame](https://www.pygame.org) | Grafik und Fenster, zur Laufzeit | LGPL-2.1 |
| [mypy](https://mypy-lang.org) | Typpruefung (`tools\check_code.py`) | MIT |
| [pytest](https://pytest.org) | Tests, nur fuer die Entwicklung | MIT |
| [PyFoot](https://github.com/SAE-GMO/pyfoot) | die Bibliothek, mitgeliefert | MIT |

pygame wird nur eingebunden, nicht veraendert oder mitgeliefert; die LGPL
erlaubt das unter jeder Lizenz.

## Vorbilder

Inspiriert von -- uebernommen wurden Ideen, kein Quelltext:

1. **Karel J. Robot** (Joseph Bergin, Mark Stehlik, Jim Roberts, Richard
   Pattis): ein Roboter in einer Gitterwelt als Einstieg ins Programmieren
2. **Greenfoot** (Michael Kölling u. a.): Welt und Akteure, der
   `act()`-Zyklus
3. **pyGreenfoot**: eine Umsetzung dieser Idee in Python mit pygame
4. **Python-Spacebug** ([inf-schule.de](https://inf-schule.de), heute
   gepflegt von der Universitaet Trier): Missionen im Weltraum

Die Grafiken entstehen aus einem eigenen Skript (siehe oben); keine stammt aus
einem der Vorbilder.

## Entstehung

Kurskonzept und Aufgaben stammen von Jörg Schaede, aufbauend auf den
genannten Vorbildern. Der Quelltext und die Ueberarbeitung der Materialien
entstanden mit Unterstuetzung des KI-Assistenten Claude (Anthropic). Alle
Inhalte wurden vom Autor geprueft und werden von ihm verantwortet.

## Lizenz

(c) 2026 Jörg Schaede

- Quelltext: **MIT** -- siehe `LICENSE`
- Anleitungen in `docs/`: **CC BY-SA 4.0** -- siehe `docs/LICENSE.md`
