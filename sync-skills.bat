@echo off
chcp 65001 >nul
setlocal
REM ============================================================
REM  One-click sync: local custom skills -> GitHub
REM  Usage: double-click this file (needs network / VPN)
REM  Logic lives in sync_skills.py (auto-discovers local skills
REM  marked agent_created: true and mirrors full folders).
REM ============================================================

set "REPO=%~dp0"
cd /d "%REPO%" || (echo [error] cannot cd to "%REPO%" & pause & exit /b 1)

set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (where py >nul 2>nul && set "PY=py")
if not defined PY (
  echo [error] python not found in PATH
  pause
  exit /b 1
)

%PY% "%REPO%sync_skills.py" %*
set "RC=%errorlevel%"

echo.
if "%RC%"=="0" (echo [done]) else (echo [failed] exit code=%RC%)
pause
endlocal
exit /b %RC%
