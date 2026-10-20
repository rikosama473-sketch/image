@echo off
setlocal
cd /d "%~dp0..\.."
echo IMAGE Character Creator
echo Opening local editor at http://127.0.0.1:8766/tools/avatar-maker/index.html
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8766/tools/avatar-maker/index.html"
py -m http.server 8766 --bind 127.0.0.1
