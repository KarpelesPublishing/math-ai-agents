@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto venv
where py >nul 2>nul
if not errorlevel 1 goto launcher
where python >nul 2>nul
if not errorlevel 1 goto plain
echo Python 3.10 or later was not found. Opening the reading guide, which needs no Python.
echo Install Python from python.org, then run this file again to compute and open notebooks.
start "" "guide\index.html"
goto done
:venv
".venv\Scripts\python.exe" "tools\launch_lab.py"
goto done
:launcher
py -3 "tools\launch_lab.py"
goto done
:plain
python "tools\launch_lab.py"
:done
pause
