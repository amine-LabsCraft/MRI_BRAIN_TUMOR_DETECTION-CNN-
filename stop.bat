@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM   BrainScan AI — Arrêt des serveurs (kill ports 8000 & 3000)
REM ═══════════════════════════════════════════════════════════════════════════

chcp 65001 >nul
echo.
echo 🛑  Arret des serveurs BrainScan AI...
echo.

REM Tuer ce qui tourne sur le port 8000 (API)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   - API (PID %%a) sur le port 8000
    taskkill /F /PID %%a >nul 2>&1
)

REM Tuer ce qui tourne sur le port 3000 (Web)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo   - Web (PID %%a) sur le port 3000
    taskkill /F /PID %%a >nul 2>&1
)

REM Fermer les fenêtres titrées BrainScan
taskkill /FI "WINDOWTITLE eq BrainScan API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq BrainScan Web*" /F >nul 2>&1

echo.
echo ✅  Servers arretes.
echo.
timeout /t 2 /nobreak >nul
