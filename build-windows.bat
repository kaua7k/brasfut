@echo off
setlocal
title BRASFUT - gerar o executavel
cd /d "%~dp0"

echo.
echo  ===========================================================
echo   BRASFUT - gerador do executavel
echo  ===========================================================
echo.
echo  Pasta: %CD%
echo.

if not exist "brasfut.py" goto semjogo
if not exist "brasfut_app.py" goto semjogo

echo  [1/4] Procurando o Python...
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY python --version >nul 2>&1
if not errorlevel 1 if not defined PY set "PY=python"
if not defined PY goto sempython
%PY% --version
echo.

echo  [2/4] Instalando o empacotador PyInstaller...
%PY% -m pip install --upgrade --quiet pip pyinstaller
if errorlevel 1 goto falhapip
echo        ok
echo.

echo  [3/4] Empacotando. Leva de 1 a 3 minutos.
echo.
%PY% -m PyInstaller --onefile --windowed --name BRASFUT --clean -y brasfut_app.py
if errorlevel 1 goto falhabuild
echo.

echo  [4/4] Limpando temporarios...
if exist build rmdir /s /q build
if exist BRASFUT.spec del /q BRASFUT.spec
echo.

echo  ===========================================================
echo   PRONTO: %CD%\dist\BRASFUT.exe
echo.
echo   Leva o jogo e os elencos dentro. Pode mover para onde
echo   quiser. O save aparece na pasta do .exe.
echo   Daqui pra frente, o iniciar.bat ja abre o executavel.
echo  ===========================================================
echo.
pause
exit /b 0

:semjogo
echo  ERRO: preciso do brasfut.py e do brasfut_app.py nesta pasta.
echo  Se o navegador salvou como .txt, renomeie tirando o .txt.
echo.
dir /b
echo.
pause
exit /b 1

:sempython
echo  ERRO: Python nao encontrado.
echo  Instale pela Microsoft Store (busque por Python) ou em python.org
echo  marcando "Add python.exe to PATH". Depois rode este arquivo de novo.
echo.
pause
exit /b 1

:falhapip
echo  ERRO: falhou ao instalar o PyInstaller. Costuma ser proxy ou rede.
echo.
pause
exit /b 1

:falhabuild
echo  ERRO: o empacotamento falhou. A causa esta nas linhas acima.
echo.
pause
exit /b 1
