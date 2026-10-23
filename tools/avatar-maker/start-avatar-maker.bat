@echo off
setlocal
cd /d "%~dp0..\.."
echo IMAGE Character Creator - editor visual y estudio de edicion por IA
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: No se encontro el lanzador de Python "py".
  echo Instala Python 3.10 o superior y activa la opcion para usar Python desde Windows.
  pause
  exit /b 1
)
set "AVATAR_PY=py"
py -3.13 -c "import rembg" >nul 2>nul && set "AVATAR_PY=py -3.13"
if "%AVATAR_PY%"=="py" py -3.12 -c "import rembg" >nul 2>nul && set "AVATAR_PY=py -3.12"
if "%AVATAR_PY%"=="py" py -3.11 -c "import rembg" >nul 2>nul && set "AVATAR_PY=py -3.11"
echo Editor local: http://127.0.0.1:8766/tools/avatar-maker/index.html
echo La edicion generativa requiere OPENAI_API_KEY en el entorno antes de iniciar.
echo El recorte local es opcional; si esta instalado, el lanzador elegira Python compatible.
echo La clave nunca se guarda en los archivos del proyecto.
echo Pulsa Ctrl+C en esta ventana para cerrar el servidor.
echo.
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8766/tools/avatar-maker/index.html"
%AVATAR_PY% tools/avatar-maker/ai_edit_server.py --host 127.0.0.1 --port 8766
pause
