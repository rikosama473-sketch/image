@echo off
setlocal
cd /d "%~dp0\..\.."
echo IMAGE Character Creator - instalador del recorte local para anime
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: No se encontro el lanzador de Python "py".
  echo Instala Python 3.10 o superior y activa la opcion para usar Python desde Windows.
  pause
  exit /b 1
)
echo Se instalara rembg con el backend CPU. Los pesos del modelo se descargan
echo en el primer uso y quedan en la cache local. No se configura ninguna clave API.
echo.
py -m pip install -r requirements-avatar-cutout.txt
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo instalar el motor. Revisa la conexion y la version de Python.
  pause
  exit /b 1
)
echo.
echo Instalacion completada. Cierra y vuelve a abrir start-avatar-maker.bat.
pause
