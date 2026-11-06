@echo off
rem ------------------------------------------------------------------------
rem  Richtet Python fuer das Projekt Space auf einem eigenen Rechner ein.
rem
rem  1. sucht eine installierte Python-Version, fuer die es pygame gibt (die
rem     neueste von 3.11 bis 3.13); gibt es nur neuere, bietet es an, 3.13
rem     zusaetzlich zu installieren,
rem  2. prueft, ob der Microsoft-Store-Platzhalter fuer "python" aus ist,
rem  3. prueft den PATH und traegt Python notfalls ein (nur fuer das eigene
rem     Benutzerkonto, ohne Administratorrechte),
rem  4. bringt pip auf den neuesten Stand und installiert dann die fehlenden
rem     Pakete.
rem
rem  Aufruf: Doppelklick, oder im Terminal
rem      tools\setup_python.bat           einrichten
rem      tools\setup_python.bat /check    nur pruefen, nichts aendern
rem
rem  An der Schule nicht noetig: Dort richtet der IT-Support alles ein.
rem ------------------------------------------------------------------------
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "CHECK_ONLY="
if /i "%~1"=="/check" set "CHECK_ONLY=1"
set "PACKAGES=pygame mypy"
set "MIN_VERSION=311"
rem Die neueste Python-Version, fuer die es pygame als fertiges Paket gibt
rem (pygame 2.6.1, Stand 11/2026). Bei neueren versucht pip, pygame selbst zu
rem uebersetzen, und scheitert. Gleicher Wert in check_environment.py.
set "MAX_VERSION=313"
set "MAX_LABEL=3.13"
set "ALIAS_DIR=%LOCALAPPDATA%\Microsoft\WindowsApps"
set "PYGAME_HIDE_SUPPORT_PROMPT=1"
set "PROBLEMS=0"

echo ================================================================
echo   Python für das Projekt Space einrichten
echo ================================================================
if defined CHECK_ONLY echo   Nur prüfen: Es wird nichts geändert.
echo.

rem ---- 1. Python finden ---------------------------------------------------
:search
echo [1/4] Python suchen ...
set "PYEXE="
set "PYVER=0"
set "NEWEST_EXE="
set "NEWEST_VER=0"
for /f "delims=" %%E in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do call :consider "%%E"
rem py -0p listet alle Versionen, die der Starter kennt, mit ihrem Pfad.
for /f "tokens=1,2,*" %%A in ('py -0p 2^>nul') do call :from_list "%%B" "%%C"
for /f "delims=" %%E in ('where python 2^>nul') do call :consider "%%E"
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do call :consider "%%D\python.exe"
for /d %%D in ("%LOCALAPPDATA%\Python\pythoncore-3*") do call :consider "%%D\python.exe"
for /d %%D in ("%ProgramFiles%\Python3*") do call :consider "%%D\python.exe"

if defined PYEXE goto :found
if %NEWEST_VER% GTR %MAX_VERSION% goto :too_new
if defined NEWEST_EXE goto :too_old
goto :no_python

:found
for %%F in ("%PYEXE%") do set "PYDIR=%%~dpF"
set "PYDIR=%PYDIR:~0,-1%"
set "STORE_PY="
echo "%PYEXE%" | findstr /i "\\WindowsApps\\" >nul && set "STORE_PY=1"
for /f "delims=" %%V in ('call "%PYEXE%" -V') do echo   gefunden: %%V
echo   in: %PYEXE%
echo.

rem ---- 2. Microsoft-Store-Platzhalter -------------------------------------
echo [2/4] Microsoft-Store-Platzhalter prüfen ...
if defined STORE_PY (
    echo   Python stammt aus dem Microsoft Store. Der Eintrag "python" muss
    echo   dann eingeschaltet bleiben - hier ist nichts zu tun.
    goto :check_path
)
call :stub_active
if not defined STUB (
    echo   in Ordnung: Der Platzhalter ist aus.
    goto :check_path
)
echo   Der Platzhalter ist AN. Er öffnet den Microsoft Store, statt Python
echo   zu starten.
if defined CHECK_ONLY (
    set /a PROBLEMS+=1
    goto :check_path
)
echo.
echo   Gleich öffnen sich die Einstellungen. Dort:
echo     Apps ^> Erweiterte App-Einstellungen ^> App-Ausführungsaliase
echo   und diese beiden Schalter AUSschalten:
echo     App-Installer  python.exe
echo     App-Installer  python3.exe
echo   Danach hierher zurück und eine Taste drücken.
echo.
start "" ms-settings:advanced-apps
pause
call :stub_active
if defined STUB (
    echo   Der Platzhalter ist noch an. Das Skript macht trotzdem weiter: Mit
    echo   dem PATH aus Schritt 3 startet "python" das richtige Programm.
) else (
    echo   in Ordnung: Der Platzhalter ist jetzt aus.
)
echo.

rem ---- 3. PATH -------------------------------------------------------------
:check_path
echo [3/4] PATH prüfen ...
if defined STORE_PY (
    echo   Beim Python aus dem Store nicht nötig.
    goto :packages
)
call :first_python
if /i "!FIRST!"=="!PYEXE!" (
    echo   in Ordnung: "python" startet !PYEXE!
    goto :packages
)
if defined FIRST (
    echo   "python" startet zurzeit: !FIRST!
) else (
    echo   "python" wird zurzeit nicht gefunden.
)
call :user_path_first
if not errorlevel 1 (
    echo   Python steht aber schon vorn im PATH deines Benutzerkontos. Nur
    echo   dieses Fenster kennt ihn noch nicht: Ein neues Terminal nimmt ihn.
    set "PATH=!PYDIR!;!PYDIR!\Scripts;!PATH!"
    goto :packages
)
if defined CHECK_ONLY (
    set /a PROBLEMS+=1
    goto :packages
)
echo   Trage Python in den PATH deines Benutzerkontos ein ...
call :set_user_path
if errorlevel 1 (
    echo   FEHLER: Der PATH ließ sich nicht ändern.
    set /a PROBLEMS+=1
    goto :packages
)
rem Auch fuer dieses Fenster, damit die folgenden Schritte ihn schon nutzen.
set "PATH=!PYDIR!;!PYDIR!\Scripts;!PATH!"
call :first_python
if /i "!FIRST!"=="!PYEXE!" (
    echo   erledigt.
) else (
    echo   Eingetragen, aber "python" startet weiterhin: !FIRST!
    echo   Diese Version steht im PATH für alle Benutzer weiter vorn. Das
    echo   lässt sich nur mit Administratorrechten ändern. Starte Python dann
    echo   mit "py" statt "python", und wähle in VS Code die Version oben aus.
)
echo.

rem ---- 4. Pakete -----------------------------------------------------------
:packages
echo [4/4] Pakete prüfen ...
"%PYEXE%" -m pip --version >nul 2>&1
if errorlevel 1 (
    if defined CHECK_ONLY (
        echo   pip fehlt.
        set /a PROBLEMS+=1
        goto :summary
    )
    echo   pip fehlt, wird eingerichtet ...
    "%PYEXE%" -m ensurepip --upgrade
)
if not defined CHECK_ONLY (
    echo   pip auf den neuesten Stand bringen ...
    "%PYEXE%" -m pip install --upgrade pip --disable-pip-version-check --quiet
    if errorlevel 1 echo   Hinweis: pip ließ sich nicht aktualisieren, es geht mit der alten Version weiter.
)
call :missing_packages
if not defined MISSING (
    echo   in Ordnung: %PACKAGES% sind installiert.
    goto :summary
)
echo   fehlt:!MISSING!
if defined CHECK_ONLY (
    set /a PROBLEMS+=1
    goto :summary
)
echo   Installiere ... (das braucht Internet und kann ein paar Minuten dauern)
rem Nur fertige Pakete: Ein Versuch, selbst zu uebersetzen, scheitert ohnehin
rem und haeuft nur seitenweise Meldungen an.
"%PYEXE%" -m pip install --only-binary :all: --disable-pip-version-check!MISSING!
call :missing_packages
if defined MISSING (
    echo.
    echo   FEHLER: Nicht installiert:!MISSING!
    echo   Die Meldung von pip steht direkt darüber. Häufigste Ursache: keine
    echo   Internetverbindung. Danach das Skript noch einmal starten.
    set /a PROBLEMS+=1
) else (
    echo   erledigt.
)

rem ---- Abschluss -----------------------------------------------------------
:summary
echo.
echo ================================================================
if defined CHECK_ONLY (
    if !PROBLEMS! EQU 0 (
        echo   Alles in Ordnung.
    ) else (
        echo   !PROBLEMS! Punkt^(e^) offen. Zum Einrichten ohne /check starten.
    )
    goto :end
)
if !PROBLEMS! NEQ 0 (
    echo   Es ist noch nicht alles eingerichtet, siehe oben.
    goto :end
)
echo   Fertig. Jetzt noch:
echo   - alle Terminals und VS Code schließen und neu öffnen,
echo     damit sie den neuen PATH kennen;
echo   - in VS Code: Strg+Umschalt+P, "Python: Interpreter auswählen",
echo     dort diese Version nehmen:
echo       %PYEXE%
echo ================================================================
rem Bewusst ohne check_environment.py: Zu Hause kommt VS Code erst nach diesem
rem Skript (AB01d), die Pruefung meldete es sonst als fehlend.
goto :end

:no_python
echo   Kein Python gefunden.
echo   Lade es von https://www.python.org/downloads/ herunter und setze im
echo   Installer unten den Haken bei "Add python.exe to PATH".
echo   Danach dieses Skript noch einmal starten.
set /a PROBLEMS+=1
goto :end

:too_new
for /f "delims=" %%V in ('call "%NEWEST_EXE%" -V') do echo   gefunden: %%V
echo   in: %NEWEST_EXE%
echo.
echo   Diese Version ist zu neu: pygame gibt es bisher nur bis Python %MAX_LABEL%.
echo   Nötig ist zusätzlich Python %MAX_LABEL%. Die neue Version darf bleiben.
set /a PROBLEMS+=1
if defined CHECK_ONLY goto :end
if defined INSTALL_TRIED goto :manual_install
where pymanager >nul 2>&1 || goto :manual_install
echo.
choice /c JN /m "  Python %MAX_LABEL% jetzt installieren"
if errorlevel 2 goto :end
set "INSTALL_TRIED=1"
pymanager install %MAX_LABEL%
set "PROBLEMS=0"
echo.
goto :search

:manual_install
echo   Lade Python %MAX_LABEL% herunter: https://www.python.org/downloads/windows/
echo   Dort unter "Stable Releases" die neueste Version 3.13.x nehmen,
echo   "Windows installer (64-bit)". Im Installer unten den Haken bei
echo   "Add python.exe to PATH" setzen, danach dieses Skript noch einmal starten.
goto :end

:too_old
echo   Gefunden ist nur eine zu alte Version: %NEWEST_EXE%
echo   Nötig ist mindestens Python 3.11. Lade eine neue Version von
echo   https://www.python.org/downloads/ herunter und setze im Installer
echo   den Haken bei "Add python.exe to PATH".
set /a PROBLEMS+=1
goto :end

:end
echo.
pause
exit /b %PROBLEMS%


rem ========================================================================
rem  Unterprogramme
rem ========================================================================

rem Eine Zeile aus "py -0p", ab dem zweiten Wort: "*" markiert die
rem Standardversion, danach folgt der Pfad. Ein Pfad mit Leerzeichen kommt in
rem zwei Teilen an.
:from_list
if "%~1"=="*" (
    call :consider "%~2"
    exit /b 0
)
if "%~2"=="" (
    call :consider "%~1"
) else (
    call :consider "%~1 %~2"
)
exit /b 0

rem Prueft %1: Ist es ein lauffaehiges Python, merkt es sich die neueste
rem Version ueberhaupt (NEWEST_*) und die neueste, fuer die es pygame gibt
rem (PY*). Der Store-Platzhalter laeuft nicht und faellt so raus.
:consider
if not exist "%~1" exit /b 0
set "CAND_VER="
for /f "delims=" %%V in ('call "%~1" -c "import sys; print(sys.version_info[0]*100+sys.version_info[1])" 2^>nul') do set "CAND_VER=%%V"
if not defined CAND_VER exit /b 0
rem Nur eine Zahl zaehlt -- eine Meldung des Platzhalters waere keine.
echo(!CAND_VER!| findstr /r "^[0-9][0-9]*$" >nul || exit /b 0
set "CAND_EXE="
for /f "delims=" %%X in ('call "%~1" -c "import sys; print(sys.executable)"') do set "CAND_EXE=%%X"
if %CAND_VER% GTR %NEWEST_VER% (
    set "NEWEST_VER=%CAND_VER%"
    set "NEWEST_EXE=!CAND_EXE!"
)
if %CAND_VER% LSS %MIN_VERSION% exit /b 0
if %CAND_VER% GTR %MAX_VERSION% exit /b 0
if %CAND_VER% LEQ %PYVER% exit /b 0
set "PYVER=%CAND_VER%"
set "PYEXE=!CAND_EXE!"
exit /b 0

rem Ob Python (PYDIR) schon an erster Stelle im Benutzer-PATH steht, wie er in
rem der Registry liegt -- also auch fuer neue Fenster. Fehlercode 0 heisst ja.
:user_path_first
set "PF_DIR=%PYDIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d = $env:PF_DIR.TrimEnd('\');" ^
  "$k = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment');" ^
  "$p = [string]$k.GetValue('Path', '', 'DoNotExpandEnvironmentNames');" ^
  "if (($p -split ';')[0].TrimEnd('\') -eq $d) { exit 0 } else { exit 1 }"
exit /b %errorlevel%

rem Setzt STUB, wenn python.exe oder python3.exe nur der Store-Platzhalter ist:
rem Die Datei ist da, laesst sich aber nicht als Python starten.
:stub_active
set "STUB="
for %%N in (python.exe python3.exe) do (
    if exist "%ALIAS_DIR%\%%N" (
        "%ALIAS_DIR%\%%N" -V >nul 2>&1 || set "STUB=1"
    )
)
exit /b 0

rem Setzt FIRST auf das Programm, das "python" im Moment startet.
:first_python
set "FIRST="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined FIRST set "FIRST=%%P"
exit /b 0

rem Setzt MISSING auf die Pakete aus PACKAGES, die sich nicht einbinden lassen.
:missing_packages
set "MISSING="
for %%P in (%PACKAGES%) do (
    "%PYEXE%" -c "import %%P" >nul 2>&1 || set "MISSING=!MISSING! %%P"
)
exit /b 0

rem Stellt PYDIR und PYDIR\Scripts an den Anfang des Benutzer-PATH. Alte
rem Eintraege derselben Ordner werden entfernt. Der Wert bleibt vom Typ
rem REG_EXPAND_SZ, damit Eintraege wie %USERPROFILE%\... weiter gelten.
rem Das Setzen und Loeschen von PYFOOT_SETUP meldet die Aenderung an Windows,
rem damit neu geoeffnete Programme den neuen PATH sehen.
:set_user_path
set "PF_DIR=%PYDIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d = $env:PF_DIR.TrimEnd('\'); $s = $d + '\Scripts';" ^
  "$k = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true);" ^
  "$old = [string]$k.GetValue('Path', '', 'DoNotExpandEnvironmentNames');" ^
  "$rest = @($old -split ';' | Where-Object { $_ -and $_.TrimEnd('\') -ne $d -and $_.TrimEnd('\') -ne $s });" ^
  "$k.SetValue('Path', ((@($d, $s) + $rest) -join ';'), 'ExpandString'); $k.Close();" ^
  "[Environment]::SetEnvironmentVariable('PYFOOT_SETUP', '1', 'User');" ^
  "[Environment]::SetEnvironmentVariable('PYFOOT_SETUP', $null, 'User')"
exit /b %errorlevel%
