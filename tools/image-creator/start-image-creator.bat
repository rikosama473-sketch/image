@echo off
setlocal
set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
cd /d "%ROOT%"

set "PYTHON_CMD=py -3.11"
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 set "PYTHON_CMD=python"
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: no se encontro Python.
  echo Ejecuta primero tools\image-creator\setup-image-creator.bat
  pause
  exit /b 1
)

start "IMAGE - motor local" cmd /k "cd /d ""%ROOT%"" && %PYTHON_CMD% ml\local_server.py"
timeout /t 3 >nul
start "" "http://127.0.0.1:8765"
