@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM   BrainScan AI — Lanceur Windows (double-clic pour démarrer)
REM   Lance l'API + l'interface dans 2 fenêtres séparées
REM ═══════════════════════════════════════════════════════════════════════════

setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo [ERREUR] Python venv introuvable : %PYTHON%
    echo Cree d'abord le venv : python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║   🧠  BrainScan AI — Lancement automatique                       ║
echo ║       ResNet50 · 98.96%% Accuracy                                 ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM ─── Lancement de l'API dans une nouvelle fenêtre
echo [1/3] Demarrage de l'API FastAPI sur http://localhost:8000 ...
start "BrainScan API (port 8000)" cmd /k "%PYTHON% -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload"

REM ─── Petit délai pour laisser le modèle charger
echo [2/3] Attente du chargement du modele (15s)...
timeout /t 15 /nobreak >nul

REM ─── Lancement du serveur web dans une autre fenêtre
echo [3/3] Demarrage de l'interface web sur http://localhost:3000 ...
start "BrainScan Web (port 3000)" cmd /k "cd /d "%~dp0interface" && %PYTHON% -m http.server 3000"

REM ─── Petit délai puis ouverture du navigateur
timeout /t 2 /nobreak >nul
start "" "http://localhost:3000"

echo.
echo ════════════════════════════════════════════════════════════════════
echo  ✅ Tout est lance !
echo ════════════════════════════════════════════════════════════════════
echo.
echo   🌐 Interface  : http://localhost:3000
echo   🔌 API health : http://localhost:8000/health
echo   📚 API docs   : http://localhost:8000/docs
echo.
echo   Pour arreter : ferme les 2 fenetres "BrainScan API" et "BrainScan Web"
echo.
pause
endlocal
