@echo off
title BRASFUT
cd /d "%~dp0"

if exist "dist\BRASFUT.exe" start "" "dist\BRASFUT.exe" & exit /b 0
if exist "BRASFUT.exe" start "" "BRASFUT.exe" & exit /b 0

if not exist "brasfut_app.py" goto semarquivo
if not exist "brasfut.py" goto semarquivo

set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY python --version >nul 2>&1
if not errorlevel 1 if not defined PY set "PY=python"
if not defined PY goto sempython

%PY% brasfut_app.py
if errorlevel 1 goto falhou
exit /b 0

:falhou
echo.
echo  O jogo fechou com erro. A mensagem esta acima.
echo  Se falar em tkinter, reinstale o Python marcando "tcl/tk and IDLE".
echo  Para jogar so no terminal, use: python brasfut.py
echo.
pause
exit /b 1

:semarquivo
echo  Faltam arquivos nesta pasta. Precisa ter brasfut.py e brasfut_app.py.
echo.
dir /b
echo.
pause
exit /b 1

:sempython
echo  Python nao encontrado.
echo  Instale pela Microsoft Store (busque por Python, nao pede admin)
echo  ou em python.org marcando "Add python.exe to PATH".
echo.
pause
exit /b 1
