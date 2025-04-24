@echo off
set "BASE_DIR=%~dp0.."
set "UTILS_DIR=%BASE_DIR%\utils"
set "SCRIPT=%UTILS_DIR%\validate_translations.py"

echo Verification et correction des traductions...

:: Verifie l'existence du script Python
if not exist "%SCRIPT%" (
    echo Erreur : validate_translations.py introuvable a l'emplacement %SCRIPT%
    pause
    exit /b 1
)

:: Change le repertoire courant pour garantir le bon contexte
cd /d "%UTILS_DIR%"

:: Definit le mode par defaut a --all si aucun argument n'est fourni
set "MODE=%1"
if "%MODE%"=="" set MODE=--all

:: Execute le script Python et capture les erreurs
python "%SCRIPT%" %MODE%
if %ERRORLEVEL% neq 0 (
    echo Erreur : Echec de la verification/correction des traductions. Consultez les messages ci-dessus.
    pause
    exit /b 1
)

echo Succes : Verification et correction des traductions terminees sans erreur.
pause
exit /b 0