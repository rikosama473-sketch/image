@echo off
setlocal
cd /d "%~dp0\..\.."
echo IMAGE Character Creator - instalador del recorte local para anime
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: No se encontro el lanzador de Python "py".
  echo Instala Python 3.11, 3.12 o 3.13 y activa la opcion para usar Python desde Windows.
  pause
  exit /b 1
)
set "AVATAR_CUTOUT_PY="
py -3.13 -m pip --version >nul 2>nul && set "AVATAR_CUTOUT_PY=py -3.13"
if not defined AVATAR_CUTOUT_PY py -3.12 -m pip --version >nul 2>nul && set "AVATAR_CUTOUT_PY=py -3.12"
if not defined AVATAR_CUTOUT_PY py -3.11 -m pip --version >nul 2>nul && set "AVATAR_CUTOUT_PY=py -3.11"
if not defined AVATAR_CUTOUT_PY (
  echo ERROR: rembg 2.0.85 requiere Python 3.11, 3.12 o 3.13.
  echo Instala una de estas versiones y vuelve a ejecutar el instalador.
  pause
  exit /b 1
)
echo Se instalara rembg con backend CPU usando %AVATAR_CUTOUT_PY%.
echo Los pesos del modelo se descargan en el primer uso y quedan en la cache local.
echo No se configura ninguna clave API.
echo.
%AVATAR_CUTOUT_PY% -m pip install -r requirements-avatar-cutout.txt
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo instalar el motor. Revisa la conexion y la version de Python.
  pause
  exit /b 1
)
echo.
echo Instalacion completada. El lanzador preferira la version compatible con rembg.
pause
