@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 run_editor.py
) else (
  python run_editor.py
)
if errorlevel 1 (
  echo.
  echo Could not start the editor. Install Python 3 from python.org or run run_editor.py manually.
  pause
)
endlocal
