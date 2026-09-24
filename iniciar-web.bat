@echo off
title BRASFUT (navegador)
cd /d "%~dp0"

if not exist "server.py" goto semarquivo
if not exist "brasfut.py" goto semarquivo

set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY python --version >nul 2>&1
if not errorlevel 1 if not defined PY set "PY=python"
if not defined PY goto sempython

if not exist "web\dist\index.html" goto sembuild

echo.
echo  BRASFUT abrindo no navegador.
echo  So um BRASFUT por vez: se a janela antiga (iniciar.bat) estiver
echo  aberta, este aqui recusa abrir para nao sobrescrever o save.
echo.
echo  Feche esta janela preta para encerrar o jogo.
echo.

%PY% server.py
if errorlevel 1 goto falhou
exit /b 0

:falhou
echo.
echo  O servidor fechou com erro. A mensagem esta acima.
echo  Para jogar pela janela de sempre, use: iniciar.bat
echo.
pause
exit /b 1

:sembuild
echo  A interface web ainda nao foi compilada.
echo.
echo  Com o Node instalado, rode uma vez:
echo      cd web
echo      npm install
echo      npm run build
echo.
echo  Enquanto isso da para jogar pela janela de sempre: iniciar.bat
echo.
pause
exit /b 1

:semarquivo
echo  Faltam arquivos nesta pasta. Precisa ter brasfut.py e server.py.
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
