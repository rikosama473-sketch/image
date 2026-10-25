@echo off
setlocal
cd /d "%~dp0\..\.."

echo.
echo IMAGE - instalar generador local para Windows (CPU)
echo Requiere Internet para dependencias y modelos que aun no esten en cache.
echo Los pesos de difusion se descargan al pulsar Generar, no desde este instalador.
echo.

set "PYTHON_CMD=py -3.11"
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 set "PYTHON_CMD=python"
%PYTHON_CMD% --version
if errorlevel 1 (
  echo ERROR: instala Python 3.11 o 3.12 desde https://www.python.org/downloads/windows/
  echo Marca "Add Python to PATH" durante la instalacion.
  pause
  exit /b 1
)

%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 goto :failed

echo.
echo Instalando PyTorch CPU, sin CUDA...
%PYTHON_CMD% -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto :failed

echo.
echo Instalando Diffusers y dependencias del motor...
%PYTHON_CMD% -m pip install -r requirements-diffusion.txt
if errorlevel 1 goto :failed

echo.
echo Instalando el recortador anime local para PNG transparente...
%PYTHON_CMD% -m pip install -r requirements-avatar-cutout.txt
if errorlevel 1 goto :failed

echo.
echo LISTO. Ejecuta tools\image-creator\start-image-creator.bat para abrir IMAGE.
echo El modelo anime y el segmentador se descargan en su primer uso.
pause
exit /b 0

:failed
echo.
echo ERROR: fallo una instalacion. Lee el mensaje anterior y vuelve a intentarlo.
pause
exit /b 1
