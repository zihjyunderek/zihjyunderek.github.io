@echo off
REM ============================================================
REM  DEV SERVER - live preview with hot reload
REM  Double-click this file. Edits to src/ appear instantly.
REM  See docs/local-dev.md for the full workflow (Chinese).
REM  (Lives in scripts/ - cd up to the repo root before running npm.)
REM ============================================================
cd /d "%~dp0.."

where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo [ERROR] Node.js not found.
  echo         Install the LTS version from: https://nodejs.org/
  echo         Then double-click this file again.
  echo.
  pause
  exit /b 1
)

if not exist node_modules (
  echo [SETUP] First run - installing dependencies, takes 1-2 minutes, one time only...
  call npm install
  if errorlevel 1 (
    echo [ERROR] npm install failed. Check your network and retry.
    pause
    exit /b 1
  )
)

echo.
echo [DEV] Starting dev server at http://localhost:4321
echo       Browser opens automatically. Press Ctrl+C here to stop.
echo.
call npm run dev -- --open
pause
