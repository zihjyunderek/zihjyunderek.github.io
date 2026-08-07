@echo off
REM ============================================================
REM  PRODUCTION PREVIEW - build the real static site, then serve it
REM  This is byte-for-byte what GitHub Pages will publish.
REM  Run this as a final check before git push.
REM  (Lives in scripts/ - cd up to the repo root before running npm.)
REM ============================================================
cd /d "%~dp0.."

where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo [ERROR] Node.js not found.
  echo         Install the LTS version from: https://nodejs.org/
  echo.
  pause
  exit /b 1
)

if not exist node_modules (
  echo [SETUP] First run - installing dependencies...
  call npm install
  if errorlevel 1 (
    echo [ERROR] npm install failed. Check your network and retry.
    pause
    exit /b 1
  )
)

echo.
echo [BUILD] Building production output to .\dist ...
call npm run build
if errorlevel 1 (
  echo.
  echo [ERROR] Build failed - fix the error above before pushing to GitHub.
  pause
  exit /b 1
)

echo.
echo [PREVIEW] Serving the exact production build at http://localhost:4321
echo           Press Ctrl+C here to stop.
echo.
call npm run preview -- --open
pause
