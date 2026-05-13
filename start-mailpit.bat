@echo off
REM ============================================================
REM Lance Mailpit pour capturer les emails du backend en local.
REM
REM Pre-requis : avoir telecharge mailpit.exe et l'avoir place
REM soit dans le PATH, soit dans le meme dossier que ce script,
REM soit en adaptant la variable MAILPIT_EXE ci-dessous.
REM
REM Apres lancement :
REM   - SMTP  : 127.0.0.1:1025  (le backend y envoie les mails)
REM   - Web UI: http://127.0.0.1:8025  (ouvrir dans le navigateur)
REM ============================================================

setlocal

set "MAILPIT_EXE=mailpit.exe"

REM Si mailpit.exe est a cote de ce script, on l'utilise en priorite.
if exist "%~dp0mailpit.exe" set "MAILPIT_EXE=%~dp0mailpit.exe"

where /Q "%MAILPIT_EXE%"
if errorlevel 1 if not exist "%MAILPIT_EXE%" (
    echo.
    echo [ERREUR] mailpit.exe est introuvable.
    echo Telechargez-le depuis https://github.com/axllent/mailpit/releases
    echo puis placez mailpit.exe a cote de ce script, ou ajoutez-le au PATH.
    echo.
    pause
    exit /b 1
)

echo Lancement de Mailpit...
echo   SMTP    : 127.0.0.1:1025
echo   Web UI  : http://127.0.0.1:8025
echo.
echo (Ctrl+C pour arreter)
echo.

"%MAILPIT_EXE%" --smtp 127.0.0.1:1025 --listen 127.0.0.1:8025

endlocal
