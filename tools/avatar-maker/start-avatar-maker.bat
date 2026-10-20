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
echo Editor local: http://127.0.0.1:8766/tools/avatar-maker/index.html
echo La IA requiere OPENAI_API_KEY configurada en el entorno antes de iniciar.
echo La clave nunca se guarda en los archivos del proyecto.
echo Pulsa Ctrl+C en esta ventana para cerrar el servidor.
echo.
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8766/tools/avatar-maker/index.html"
py tools/avatar-maker/ai_edit_server.py --host 127.0.0.1 --port 8766
pause
