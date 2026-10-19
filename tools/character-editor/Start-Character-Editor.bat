@echo off
setlocal
cd /d "%~dp0..\.."
echo IMAGE - Editor modular de personajes
echo Selecciona la carpeta donde guardas tus imagenes.
set "IMAGE_FOLDER_FILE=%TEMP%\image-character-editor-folder.txt"
del "%IMAGE_FOLDER_FILE%" >nul 2>nul
powershell -NoProfile -STA -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = 'Elige la carpeta de imagenes que quieres explorar'; $d.ShowNewFolderButton = $false; if ($d.ShowDialog() -eq 'OK') { [System.IO.File]::WriteAllText($env:TEMP + '\image-character-editor-folder.txt', $d.SelectedPath) }"
if not exist "%IMAGE_FOLDER_FILE%" (
  echo No seleccionaste una carpeta. No se ha modificado ningun archivo.
  pause
  exit /b 1
)
set /p "IMAGE_ASSET_DIR="<"%IMAGE_FOLDER_FILE%"
del "%IMAGE_FOLDER_FILE%" >nul 2>nul
if not defined IMAGE_ASSET_DIR (
  echo No se selecciono una carpeta.
  pause
  exit /b 1
)
where python >nul 2>nul
if errorlevel 1 (
  echo No encuentro Python. Se requiere Python 3.10 o posterior.
  echo Consulta docs\CHARACTER_EDITOR_GUIDE.md para ver el comando.
  pause
  exit /b 2
)
python ml\character_editor_server.py --assets-dir "%IMAGE_ASSET_DIR%" --open-browser
pause
