@echo off
title BRASFUT - baixar nova versao
cd /d "%~dp0"
rem Baixa a versao mais nova ja extraida em Documents\bras2.0\<proximo numero>.0
rem e leva o save junto. Detalhes em ferramentas\nova-versao.ps1.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ferramentas\nova-versao.ps1" %*
echo.
pause
